from convos import convoTemplates, SeparatorStyle
from generateTokenStream import generateTokenStream


def runInference(
    inputString,
    websocket,
    modelSettings,
    conversation,
    tokenizer,
    model,
    device,
    debug,
):
    try:
        inp = inputString
    except EOFError:
        inp = ""
    if not inp:
        print("No input received...")
        return

    print(f"{conversation.roles[0]}: {inputString}")

    if debug:
        print(f'Received input "{inp}"')

    if debug:
        print("Preparing conversation...")
    conversation.append_message(conversation.roles[0], inp)
    conversation.append_message(conversation.roles[1], None)
    prompt = conversation.get_prompt()

    if debug:
        print(
            "Inferencing with temp",
            modelSettings.temperature,
            "and max tokens",
            modelSettings.max_new_tokens,
        )

    params = {
        "model": modelSettings.modelName,
        "prompt": prompt,
        "temperature": modelSettings.temperature,
        "max_new_tokens": modelSettings.max_new_tokens,
        "stop": conversation.sep
        if conversation.sep_style == SeparatorStyle.SINGLE
        else conversation.sep2,
    }

    print(f"{conversation.roles[1]}: ", end="", flush=True)
    pre = 0

    if debug:
        print("Declaring token generators...")
    tokenGenerators = generateTokenStream(tokenizer, model, params, device, debug)

    if debug:
        print("Executing token generators...")
    for modelOutput in tokenGenerators:
        modelOutputMinusPrompt = modelOutput[len(prompt) + 1 :].strip()
        modelOutput = modelOutputMinusPrompt
        modelOutput = modelOutput.split(" ")
        now = len(modelOutput)
        if now - 1 > pre:
            print(" ".join(modelOutput[pre : now - 1]), end=" ", flush=True)
            currentOutput = " ".join(modelOutput[pre : now - 1]) + " "
            if modelSettings.shouldStream:
                websocket.send(currentOutput)
            pre = now - 1

    finalOutput = " ".join(modelOutput[pre:])

    print(finalOutput, flush=True)

    if modelSettings.shouldStream:
        websocket.send(finalOutput)
    conversation.messages[-1][-1] = " ".join(modelOutput)
    print(conversation.messages[-1][-1])
    if not modelSettings.shouldStream:
        print("MESSAGE NOT STREAMED")
        websocket.send(conversation.messages[-1][-1])
    if debug:
        print("\n", {"prompt": prompt, "outputs": modelOutput}, "\n")
