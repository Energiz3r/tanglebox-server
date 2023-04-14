from convos import SeparatorStyle
from generateTokenStream import generateTokenStream
from multiprocessing import cpu_count


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

    if device != "cpu-ggml":
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
    else:
        finalOutputDict = {"finalOutput": ""}

        # these params are shown in the CLI for llama.cpp which works exceptionally well and are replicated here
        #
        # sampling: temp = 0.000000, top_k = 40, top_p = 0.950000, repeat_last_n = 64, repeat_penalty = 1.200000
        # generate: n_ctx = 2048, n_batch = 8, n_predict = -1, n_keep = 2 ( n_keep not implemented in pyllamacpp )
        #
        # I can't find any documentation on how the prompt input should be formatted.
        #
        # `prompt` is formatted like this, with conversation history:
        # A chat between a curious human and an artificial intelligence assistant. The assistant gives helpful,
        # detailed, and polite answers to the human's questions.###Human: Hello###Assistant:
        #                                                                 ^^^^^
        #                                                         the actual input from UI
        #
        # `inputString` is the raw input, eg.: Hello

        llamaCppPrompt = prompt  # includes conversation history
        # llamaCppPrompt = "### Instruction:\n\n" + inputString # no conversation history

        def new_text_callback(text: str):
            # use a dict to escape function scope
            finalOutputDict["finalOutput"] = finalOutputDict["finalOutput"] + text
            if modelSettings.shouldStream:  # stream model output as it's inferenced
                websocket.send(text)
                print(text, end="")
                return False

        print("Inferencing llamacpp with prompt:", llamaCppPrompt)
        try:
            model.generate(
                llamaCppPrompt,
                temp=modelSettings.temperature,
                n_predict=-1,
                new_text_callback=new_text_callback,
                n_threads=cpu_count(),
                verbose=False,
            )
        except:
            pass

        finalOutput = finalOutputDict["finalOutput"]
        # finalOutput = model.generate(prompt, n_predict=55, n_threads=8)

        # send model output in one chunk once inference is finished
        if not modelSettings.shouldStream:
            print("Final output:", finalOutput, flush=True)
            websocket.send(finalOutput)

        # append output to the conversation history once it's finished
        conversation.messages[-1][-1] = finalOutput

    if debug:
        print("\n", {"prompt": prompt, "outputs": modelOutput}, "\n")
