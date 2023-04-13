import torch
from utils import tokensByDevice


# missing the @torch.inference_mode() decorator causes an error:
# "RuntimeError: Inference tensors cannot be saved for backward. To work around you can make a clone to get a normal tensor and use it in autograd."
# Noted here because of the time I wasted debugging. Line must be in every .py file running an inference not just the main
@torch.inference_mode()
def generateTokenStream(
    tokenizer, model, params, device, debug, context_len=2048, stream_interval=2
):
    prompt = params["prompt"]
    temperature = params["temperature"]
    max_new_tokens = params["max_new_tokens"]
    l_prompt = len(prompt)
    stop_str = params.get("stop", None)

    if debug:
        print("Prompt:\n\n", prompt, "\n\n")

    if device == "cpu-gptq":
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    elif device == "cuda":
        input_ids = tokenizer(prompt).input_ids
    else:
        input_ids = tokenizer(prompt).input_ids

    output_ids = list(input_ids)

    max_src_len = context_len - max_new_tokens - 8
    input_ids = input_ids[-max_src_len:]

    for i in range(max_new_tokens):
        if i == 0:
            out = model(
                input_ids=tokensByDevice(device, input_ids, True, debug, debug),
                use_cache=True,
            )
            logits = out.logits
            past_key_values = out.past_key_values
        else:
            if device == "cuda":
                attention_mask = torch.ones(
                    1, past_key_values[0][0].shape[-2] + 1, device="cuda"
                )
            else:
                attention_mask = torch.ones(1, past_key_values[0][0].shape[-2] + 1)
            out = model(
                input_ids=tokensByDevice(device, token, False, debug, debug),
                use_cache=True,
                attention_mask=attention_mask,
                past_key_values=past_key_values,
            )
            logits = out.logits
            past_key_values = out.past_key_values

        if debug:
            print("Finished inferencing a token")

        last_token_logits = logits[0][-1]

        if device == "mps":
            # Switch to CPU by avoiding some bugs in mps backend.
            last_token_logits = last_token_logits.float().to("cpu")

        if temperature < 1e-4:
            print("Temperature was zero, ignoring.")
            token = int(torch.argmax(last_token_logits))
        else:
            probs = torch.softmax(last_token_logits / temperature, dim=-1)
            token = int(torch.multinomial(probs, num_samples=1))

        output_ids.append(token)

        if torch.is_tensor(output_ids[0]):
            output_idsPatched = [*output_ids[0].tolist(), *output_ids[1:]]
            if debug:
                print(
                    "Tokens were tensor patched for GPTQ... Tokens:", output_idsPatched
                )
        elif type(output_ids[0]) is list:
            output_idsPatched = [*output_ids[0], *output_ids[1:]]
            if debug:
                print("Tokens were patched... Tokens:", output_idsPatched)
        else:
            if debug:
                print("Tokens werent patched... Tokens:", output_ids)
            output_idsPatched = output_ids

        if token == tokenizer.eos_token_id:
            stopped = True
        else:
            stopped = False

        if i % stream_interval == 0 or i == max_new_tokens - 1 or stopped:
            output = tokenizer.decode(output_idsPatched, skip_special_tokens=True)
            pos = output.rfind(stop_str, l_prompt)
            if pos != -1:
                output = output[:pos]
                stopped = True
            yield output

        if stopped:
            break

    del past_key_values
