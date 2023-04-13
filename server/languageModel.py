import time
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    LlamaTokenizer,
    LlamaForCausalLM,
    AutoModel,
)
from convos import convoTemplates, SeparatorStyle
from compression import compress_module
from generateTokenStream import generateTokenStream
from mps_patch import replace_llama_attn_with_non_inplace_operations


class LanguageModel:
    @torch.no_grad()
    @torch.inference_mode()
    def __init__(
        self,
        model_name,
        num_gpus,
        device,
        debug,
        modelSettings,
        load_8bit,
        llama,
        vram_gb,
    ):
        self.model_name = model_name
        self.num_gpus = num_gpus
        self.device = device
        self.debug = debug
        self.modelSettings = modelSettings
        self.load_8bit = load_8bit
        isLlamaDetected = (
            "vicuna" in model_name.lower()
            or "llama" in model_name.lower()
            # or "alpaca" in model_name.lower()
        )
        self.isLlama = llama or isLlamaDetected
        if self.isLlama:
            print("LLaMA model detected", self.isLlama)

        if "chatglm" in model_name:
            print("Configuring for chatglm model type")
            num_gpus = int(num_gpus)
            kwargs = {
                "torch_dtype": torch.half,
                "low_cpu_mem_usage": True,
                "device_map": "auto",
                "max_memory": {i: str(vram_gb) + "GiB" for i in range(num_gpus)},
                # "offload_folder": "./offload",
            }
        elif device == "cuda":
            print("Configuring for CUDA acceleration")
            num_gpus = int(num_gpus)
            kwargs = {
                "torch_dtype": torch.half,
                "low_cpu_mem_usage": True,
                "device_map": "auto",
                "max_memory": {i: str(vram_gb) + "GiB" for i in range(num_gpus)},
                # "offload_folder": "./offload",
            }
        elif device == "cpu-gptq":
            print("Configuring for CPU and GPTQ models")
            kwargs = {
                "torch_dtype": torch.float32,
                "low_cpu_mem_usage": True,
                # "max_memory": {0: "64GiB"},
            }
        elif device == "mps":
            print("Configuring for Apple silicon")
            kwargs = {"torch_dtype": torch.float16}
            # Avoid bugs in mps backend by not using in-place operations.
            replace_llama_attn_with_non_inplace_operations()
        else:
            print("Configuring for CPU")
            kwargs = {
                "torch_dtype": torch.float32,
                "low_cpu_mem_usage": True,
                # "max_memory": {0: "64GiB"},
            }

        if self.debug:
            print("Setting up tokenizer...")
        if self.isLlama:
            print("Using LlamaTokenizer")
            self.tokenizer = LlamaTokenizer.from_pretrained(model_name)
        elif "chatglm" in model_name:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True
            )
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        if self.debug:
            print("Tokenizer:", self.tokenizer)

        print(f"Loading model '{model_name}' ({device})...")
        if self.isLlama:
            self.model = LlamaForCausalLM.from_pretrained(model_name, **kwargs)
        elif "chatglm" in model_name:
            self.model = AutoModel.from_pretrained(
                model_name, trust_remote_code=True, **kwargs
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(model_name, **kwargs)

        if (device == "cuda" and num_gpus == 1) or device == "mps":
            self.model.to(device)
        else:
            self.model.to(memory_format=torch.channels_last)

        if load_8bit:
            print("Compressing model...")
            compress_module(self.model, device)

        if self.debug:
            print("Setting up convo...")
        self.conversation = convoTemplates["v1"].copy()

        print("Language model initialised.")

    def runInference(self, inputString, websocket):
        try:
            inp = inputString
        except EOFError:
            inp = ""
        if not inp:
            print("No input received...")
            return

        if inp == "#-delete-#":
            self.conversation = convoTemplates["v1"].copy()
            websocket.send("#-delete-#")
            print("Deleted user's conversation.")
            return

        print(f"{self.conversation.roles[0]}: {inputString}")

        if self.debug:
            print(f'Received input "{inp}"')

        if self.debug:
            print("Preparing conversation...")
        self.conversation.append_message(self.conversation.roles[0], inp)
        self.conversation.append_message(self.conversation.roles[1], None)
        prompt = self.conversation.get_prompt()

        if self.debug:
            print(
                "Inferencing with temp",
                self.modelSettings.temperature,
                "and max tokens",
                self.modelSettings.max_new_tokens,
            )

        params = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.modelSettings.temperature,
            "max_new_tokens": self.modelSettings.max_new_tokens,
            "stop": self.conversation.sep
            if self.conversation.sep_style == SeparatorStyle.SINGLE
            else self.conversation.sep2,
        }

        print(f"{self.conversation.roles[1]}: ", end="", flush=True)
        pre = 0

        if self.debug:
            print("Declaring token generators...")
        tokenGenerators = generateTokenStream(
            self.tokenizer, self.model, params, self.device, self.debug
        )

        if self.debug:
            print("Executing token generators...")
        for modelOutput in tokenGenerators:
            modelOutputMinusPrompt = modelOutput[len(prompt) + 1 :].strip()
            modelOutput = modelOutputMinusPrompt
            modelOutput = modelOutput.split(" ")
            now = len(modelOutput)
            if now - 1 > pre:
                print(" ".join(modelOutput[pre : now - 1]), end=" ", flush=True)
                currentOutput = " ".join(modelOutput[pre : now - 1]) + " "
                websocket.send(currentOutput)
                pre = now - 1

        finalOutput = " ".join(modelOutput[pre:])

        print(finalOutput, flush=True)

        websocket.send(finalOutput)
        self.conversation.messages[-1][-1] = " ".join(modelOutput)

        if self.debug:
            print("\n", {"prompt": prompt, "outputs": modelOutput}, "\n")
