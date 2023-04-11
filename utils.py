import torch


def tokensByDevice(device, token, isBase, debug=False, showTokens=False):
    if debug and showTokens:
        print(
            f'{"Tokenising prompt" if isBase else "Inferencing"} using ({device})... Tokens:',
            token,
        )
    elif debug:
        print(f'{"Tokenising prompt" if isBase else "Inferencing"} using ({device})...')
    if device == "cuda":
        if isBase:
            result = torch.as_tensor([token]).cuda()
        else:
            result = torch.as_tensor([[token]], device="cuda")
    elif device == "cpu-gptq":
        if isBase:
            result = token
        else:
            result = torch.as_tensor([[token]])
    elif device == "cpu":
        if isBase:
            result = torch.as_tensor([token])
        else:
            result = torch.as_tensor([[token]])
    if debug:
        print("tokenised result", result)
    return result
