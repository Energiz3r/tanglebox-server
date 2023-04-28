from conversationClass import SeparatorStyle
from generateTokenStream import generateTokenStream
from multiprocessing import cpu_count

def inference(
    model,
    tokenizer,
    inputPrompt,
    outputPrompt,
    temperature,
    maxNewTokens,
    separator,
    device,
    debug,
    shouldStream,
):
    if debug:
        print(
            "Inferencing with temp",
            temperature,
            "and max tokens",
            maxNewTokens,
        )

    if device != "cpu-ggml":
        if debug:
            print("Declaring token generators...")
        tokenGenerators = generateTokenStream(tokenizer, model, inputPrompt, temperature, maxNewTokens, separator, device, debug)
        if debug:
            print("Executing token generators...")

        promptForOutput = outputPrompt
        thisResponse = ""
        chunksCount = 0
        lenLastToken = 0
        unsentToken = ""
        # each time we iterate, the model output includes the output so far as well as the prompt input. so we remove the prompt then split by space in order to yeild new chunks
        for modelOutput in tokenGenerators:
            modelOutputMinusPrompt = modelOutput[len(promptForOutput) + 1 :].strip()
            modelOutputSplitBySpace = modelOutputMinusPrompt.split(" ")
            modelOutputChunks = len(modelOutputSplitBySpace)
            if chunksCount == 0 and lenLastToken == 0:
                thisToken = modelOutputMinusPrompt
            else:
                thisToken = modelOutputMinusPrompt[lenLastToken:]
            thisResponse += thisToken
            lenLastToken += len(thisToken)
            if modelOutputChunks > chunksCount:
                #print('#'+thisToken+"$")
                chunksCount = modelOutputChunks
                fullNewToken = unsentToken + thisToken
                unsentToken = ""
                if shouldStream:
                    yield  fullNewToken
            else:
                unsentToken += thisToken
                #print('!!'+thisToken+"%")
        print(thisResponse)
        if not shouldStream:
            yield thisResponse

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
        llamaCppPrompt = inputPrompt  # includes conversation history
        # llamaCppPrompt = "### Instruction:\n\n" + inputString # no conversation history

        def new_text_callback(text: str):
            # use a dict to escape function scope
            finalOutputDict["finalOutput"] = finalOutputDict["finalOutput"] + text
            if shouldStream:  # stream model output as it's inferenced
                
                print(text, end="")
                yield(text)

                #exit()

        print("Inferencing llamacpp with prompt:", llamaCppPrompt)
        if shouldStream:
            model.generate(
                llamaCppPrompt,
                temp=temperature,
                n_predict=-1,
                new_text_callback=new_text_callback,
                n_threads=cpu_count(),
                verbose=False,
            )
        else:
            finalOutput = model.generate(llamaCppPrompt, n_predict=55, n_threads=8)
            print("Final output:", finalOutput, flush=True)
            yield finalOutput

    if debug:
        print("\n", {"prompt": inputPrompt, "outputs": modelOutput}, "\n")

def websocketInference(
    inputString,
    websocket,
    modelSettings,
    conversation,
    tokenizer,
    model,
    device,
    debug,
    user
):
    try:
        inp = inputString
    except EOFError:
        inp = ""
    if not inp:
        print("No input received...")
        return

    print("From", user + ":", inputString)

    if debug:
        print(f'Received input "{inp}"')

    if debug:
        print("Preparing conversation...")
    conversation.append_message(conversation.roles[0], inp)
    conversation.append_message(conversation.roles[1], None)
    inputPrompt = conversation.getPromptForModel()
    outputPrompt = conversation.getPromptForOutput()
    separator = conversation.sep
    if conversation.sep_style == SeparatorStyle.TWO:
        separator = conversation.sep2      
    
    result = inference(
        model,
        tokenizer,
        inputPrompt,
        outputPrompt,
        modelSettings.temperature,
        modelSettings.maxNewTokens,
        separator,
        device,
        debug,
        modelSettings.shouldStream,
    )
    conversation.messages[-1][-1] = ""
    for chunk in result:
        websocket.send(chunk)
        conversation.messages[-1][-1] += chunk
    print("To", user + ":", conversation.messages[-1])
