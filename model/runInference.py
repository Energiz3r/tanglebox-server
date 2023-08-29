from generateTokenStream import generateTokenStream
import json


def createChunk(content: str, stop: bool):
    return bytes(
        f'data: {{"content":{json.dumps(content)},"stop":"{stop}"}}\n\n', "utf-8"
    )


def inference(
    model,
    tokenizer,
    inputPrompt,
    stopTokens,
    temperature,
    maxNewTokens,
    device,
    debug,
    shouldStream,
    userIdentifier,
):
    if debug:
        print(
            "Inferencing with temp",
            temperature,
            "and max tokens",
            maxNewTokens,
        )

    if debug:
        print("Declaring token generators...")
    tokenGenerators = generateTokenStream(
        tokenizer,
        model,
        inputPrompt,
        temperature,
        maxNewTokens,
        stopTokens[0],
        device,
        False,  # debug,
    )
    if debug:
        print("Executing token generators...")

    promptForOutput = inputPrompt.replace(stopTokens[0], " ")
    promptForOutput = promptForOutput.lstrip()
    thisResponse = ""
    chunksCount = 0
    lenLastToken = 0
    unsentToken = ""
    # each time we iterate, the model output includes the output so far as well as the prompt input. so we remove the prompt then split by space in order to yeild new chunks
    for modelOutput in tokenGenerators:
        if debug:
            print("Looping a generator...")
            if chunksCount == 0:
                print(
                    f"Model output is:'{modelOutput}'({len(modelOutput)}), prompt for output:'{promptForOutput}'({len(promptForOutput)})"
                )
        modelOutputMinusPrompt = modelOutput[len(promptForOutput) :].strip()
        modelOutputSplitBySpace = modelOutputMinusPrompt.split(" ")
        modelOutputChunks = len(modelOutputSplitBySpace)
        if chunksCount == 0 and lenLastToken == 0:
            thisToken = modelOutputMinusPrompt
        else:
            thisToken = modelOutputMinusPrompt[lenLastToken:]
        if debug:
            print(
                f"This token:'{thisToken}', chunk count:'{chunksCount}', len last token:'{lenLastToken}'"
            )
        thisResponse += thisToken
        lenLastToken += len(thisToken)
        if modelOutputChunks > chunksCount:
            # print('#'+thisToken+"$")
            chunksCount = modelOutputChunks
            fullNewToken = unsentToken + thisToken
            unsentToken = ""
            if shouldStream:
                if debug:
                    print(f"Finished looping, yielding token:'{fullNewToken}'")
                yield createChunk(fullNewToken, False)
            else:
                if debug:
                    print(f"Finished looping, no new chunks to output...")
        else:
            unsentToken += thisToken
            # print('!!'+thisToken+"%")
            if debug:
                print(f"Finished looping, added to unsent token(s):'{unsentToken}'")
    # print(thisResponse)
    if shouldStream:
        if debug:
            print(f"Final yield for stream, unsentToken:'{unsentToken}'")
        yield createChunk(unsentToken, True)
    else:
        if debug:
            print(f"Final yield for NON-stream, response:'{thisResponse}'")
        yield createChunk(thisResponse, True)

    if not debug:
        print(f"To ({userIdentifier}):", thisResponse)
    # if debug:
    # print("\n", {"prompt": inputPrompt, "outputs": modelOutput}, "\n")
