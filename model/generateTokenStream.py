import torch
from utils import tokensByDevice
from utils import bcolors


# missing the @torch.inference_mode() decorator causes an error:
# "RuntimeError: Inference tensors cannot be saved for backward. To work around you can make a clone to get a normal tensor and use it in autograd."
# Noted here because of the time I wasted debugging. Line must be in every .py file running an inference not just the main
@torch.inference_mode()
def generateTokenStream(
    tokenizer, model, inputPrompt, temperature, maxNewTokens, separator, device, debug, context_len=2048, stream_interval=2
):
    prompt = inputPrompt
    l_prompt = len(prompt)

    if debug:
        print("Prompt:\n\n", prompt, "\n\n")

    if device == "cpu-gptq":
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    elif device == "cuda":
        input_ids = tokenizer(prompt).input_ids
    else:
        input_ids = tokenizer(prompt).input_ids

    output_ids = list(input_ids)

    max_src_len = context_len - maxNewTokens - 8
    input_ids = input_ids[-max_src_len:]

    # print("input_ids", input_ids)

    for i in range(maxNewTokens):
        if debug:
            print("Modelling a token...")
        if i == 0:
            out = model(
                input_ids=tokensByDevice(device, input_ids, True, debug, debug),
                use_cache=True,
            )
            if debug:
                print("setting logits...")
            logits = out.logits
            if debug:
                print("setting past key values...")
            past_key_values = out.past_key_values
        else:
            if debug:
                print("setting attention mask...")
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
            if debug:
                print("setting logits...")
            logits = out.logits
            if debug:
                print("setting past key values...")
            past_key_values = out.past_key_values

        if debug:
            print("Finished inferencing a token")

        last_token_logits = logits[0][-1]

        if device == "mps":
            # Switch to CPU by avoiding some bugs in mps backend.
            last_token_logits = last_token_logits.float().to("cpu")

        wasTempZero = False
        if temperature < 1e-4:
            wasTempZero = True
            print("Temperature was zero, ignoring.")
            token = int(torch.argmax(last_token_logits))
        else:
            try:
                probs = torch.softmax(last_token_logits / temperature, dim=-1)
            except:
                print('Softmax float error?', last_token_logits.float())
                probs = torch.softmax(last_token_logits.float() / temperature, dim=-1)
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

        if debug:
            print("Checking for stop token...")
        if token == tokenizer.eos_token_id:
            if debug:
                print("Stopped generating because tokenizer found EOS token id:", token)
            stopped = True
        else:
            if debug:
                print("No stop token found.")
            stopped = False
        
        if debug:
            print("Decoding tokens...")
        if i % stream_interval == 0 or i == maxNewTokens - 1 or stopped:
            output = tokenizer.decode(output_idsPatched, skip_special_tokens=True)
            pos = output.rfind(separator, l_prompt)
            if pos != -1:
                if debug:
                    print("Stopped generating because output contained '",separator,"'")
                output = output[:pos]
                stopped = True
            yield output

        if stopped:
            if wasTempZero == True:
                yield "\n[Your temperature setting cannot be zero - it was ignored.]"
            break

    del past_key_values
