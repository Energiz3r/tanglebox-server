import time
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    LlamaTokenizer,
    LlamaForCausalLM,
    AutoModel,
)
from compression import compress_module
from mps_patch import replace_llama_attn_with_non_inplace_operations
from pyllamacpp.model import Model


class LanguageModel:
    @torch.no_grad()
    @torch.inference_mode()
    def __init__(
        self,
        model_name,
        num_gpus,
        device,
        debug,
        load_8bit,
        vram_gb,
    ):
        self.model_name = model_name
        self.num_gpus = num_gpus
        self.device = device
        self.debug = debug
        self.load_8bit = load_8bit

        isGgmlDetected = (
            device == "cpu-ggml"
            or "ggml" in model_name.lower()
            or "q4_0" in model_name.lower()
            or "q4_1" in model_name.lower()
        )
        isLlamaDetected = not isGgmlDetected and (
            "vicuna" in model_name.lower()
            or "llama" in model_name.lower()
            # or "alpaca" in model_name.lower()
        )

        if isGgmlDetected:
            print("Configuring for ggml")
            self.tokenizer = None
            self.model = Model(ggml_model=model_name, n_ctx=2048, log_level=0)
            print("Language model initialised.")
            return

        if "chatglm" in model_name:
            print("Configuring for chatglm model type")
            num_gpus = int(num_gpus)
            kwargs = {
                "torch_dtype": torch.half,
                "low_cpu_mem_usage": True,
                "device_map": "auto",
                "max_memory": {i: str(vram_gb) + "GiB" for i in range(num_gpus)},
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
            }

        if self.debug:
            print("Setting up tokenizer...")
        if isLlamaDetected:
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
        if isLlamaDetected:
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

        print("Language model initialised.")
