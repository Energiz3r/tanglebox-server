import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    LlamaTokenizer,
    LlamaForCausalLM,
    AutoModel,
    AutoConfig,
)
from compression import (
    compress_module,
    compress,
    CompressionConfig,
    get_compressed_list,
    apply_compressed_weight,
)
from mps_patch import replace_llama_attn_with_non_inplace_operations
import glob
import os
import gc
from tqdm import tqdm
from accelerate import init_empty_weights
from accelerate.utils import set_module_tensor_to_device

default_compression_config = CompressionConfig(
    num_bits=8, group_size=256, group_dim=1, symmetric=True, enabled=True
)


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

        isLlamaDetected = (
            "vicuna" in model_name.lower()
            or "llama" in model_name.lower()
            or "rippa" in model_name.lower()
        )

        if load_8bit:
            # partially load model
            tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
            base_pattern = os.path.join(model_name, "pytorch_model-*.bin")
            files = glob.glob(base_pattern)

            with init_empty_weights():
                num_gpus = int(num_gpus)
                config = AutoConfig.from_pretrained(
                    model_name,
                    low_cpu_mem_usage=True,
                    device_map="auto",
                    torch_dtype=torch.float16,
                    max_memory={i: str(vram_gb) + "GiB" for i in range(num_gpus)},
                )
                model = AutoModelForCausalLM.from_config(config)
                linear_weights = get_compressed_list(model)

            compressed_state_dict = {}

            for file in files:
                tmp_state_dict = torch.load(file, map_location="cpu")
                for name in tqdm(tmp_state_dict):
                    if name in linear_weights:
                        compressed_state_dict[name] = tmp_state_dict[name].to(device)
                        tensor = compressed_state_dict[name].data
                        compressed_state_dict[name] = compress(
                            tensor, default_compression_config
                        )
                    else:
                        compressed_state_dict[name] = tmp_state_dict[name].to(device)
                    tmp_state_dict[name] = None
                    tensor = None
                    gc.collect()
                    torch.cuda.empty_cache()

            for name in model.state_dict():
                if name not in linear_weights:
                    set_module_tensor_to_device(
                        model, name, device, value=compressed_state_dict[name]
                    )
            apply_compressed_weight(model, compressed_state_dict, device)

            model.to(device)
            self.model = model
            self.tokenizer = tokenizer

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
            print(
                "Configuring for CUDA acceleration",
                vram_gb,
                "GB of vram",
                num_gpus,
                "GPUs",
            )
            num_gpus = int(num_gpus)
            kwargs = {
                "torch_dtype": torch.float16,
                "device_map": "auto",
            }
        elif device == "mps":
            print("Configuring for Apple silicon")
            kwargs = {"torch_dtype": torch.float16}
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
            self.tokenizer = LlamaTokenizer.from_pretrained(
                model_name,
                legacy=True,
            )
        elif "chatglm" in model_name:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True
            )
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        if self.debug:
            print("Tokenizer:", self.tokenizer)

        if isLlamaDetected:
            print(f"Loading Llama Model '{model_name}' ({device})...")
            self.model = LlamaForCausalLM.from_pretrained(model_name, **kwargs)
        elif "chatglm" in model_name:
            print(f"Loading ChatGLM Model '{model_name}' ({device})...")
            self.model = AutoModel.from_pretrained(
                model_name, trust_remote_code=True, **kwargs
            )
        else:
            print(f"Loading Model (auto-detect)'{model_name}' ({device})...")
            self.model = AutoModelForCausalLM.from_pretrained(model_name, **kwargs)

        if load_8bit:
            print("Compressing model...")
            compress_module(self.model, device)

        if (device == "cuda" and num_gpus == 1) or device == "mps":
            self.model.to(device)
        else:
            self.model.to(memory_format=torch.channels_last)

        print("Language model initialised.")

    def close(self):
        self.model.close()
