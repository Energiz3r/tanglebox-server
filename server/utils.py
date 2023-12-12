import json


def createChunk(content: str, stop: bool = False):
    return bytes(
        f'data: {{"content":{json.dumps(content)},"stop":"{stop}"}}\n\n', "utf-8"
    )


def parseChunkContent(chunk, isOpenAi):
    chunkStr = chunk.decode("utf-8")
    if isOpenAi:
        chunkJson = json.loads(chunkStr)
        response = chunkJson["choices"][0]["message"]["content"]
        return response
    if "data:" in chunkStr:
        chunkSplit = chunkStr.split("data:")
    elif "error:" in chunkStr:
        chunkSplit = chunkStr.split("error:")
    else:
        print("couldn't split chunk on data: or error:", chunkStr)
        chunkSplit = [chunkStr]
    chunkContent = ""
    for eventObjectJson in chunkSplit:
        if len(eventObjectJson):
            eventObjectJsonClean = eventObjectJson.strip()
            while (
                eventObjectJsonClean[-2:] == "\\n"
            ):  # remove trailing escaped \n from string eg {"content":"stuff"}\\n\\n
                eventObjectJsonClean = eventObjectJsonClean[:-2]
            if eventObjectJsonClean[:-1] == '"':
                eventObjectJsonClean += "}"
            
            if "content" in eventObjectJsonClean:
                try:
                    eventObject = json.loads(eventObjectJsonClean)
                    chunkContent += str(eventObject["content"])
                except json.decoder.JSONDecodeError:
                    print("Json decode error with event chunk, not parsing:", eventObjectJsonClean)
                    chunkContent += eventObjectJsonClean
            else:
                print("'content' not found in event chunk:", eventObjectJsonClean)
                chunkContent += eventObjectJsonClean           
        
    return chunkContent


def checkApiToken(token):
    try:
        with open("apiTokens.txt", "r") as file:
            tokensList = file.read().splitlines()
    except FileNotFoundError:
        print("API tokens file not found")
        tokensList = []
    for tokenLine in tokensList:
        pair = tokenLine.split(":")
        if pair[1] == "TOKEN":
            continue
        if pair[1] == token:
            return True
    return False


def remove_keys_from_dict(dict_obj: dict, keys_to_remove: list) -> dict:
    return {key: value for key, value in dict_obj.items() if key not in keys_to_remove}


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


bc = bcolors.OKGREEN
tc = bcolors.WARNING
th = bcolors.OKBLUE
vs = "│"


def printDictAsTable(dict, title="Table output:", headers=["Key", "Value"], isError=False):
    table = ""
    borderCol = bc
    if isError:
        borderCol = bcolors.FAIL
    maxKeyWidth = max(len(str(key)) for key in dict.keys())
    maxValueWidth = max(len(str(value)) for value in dict.values())
    if maxValueWidth < 8:
        maxValueWidth = 8
    tableHeaders = (
        borderCol
        + vs
        + " "
        + th
        + "   ".join(
            cell.ljust(maxKeyWidth if cell == headers[0] else maxValueWidth)
            for cell in headers
        )
        + borderCol
        + vs
        + "\n"
    )
    for key, value in dict.items():
        table += (
            borderCol
            + vs
            + " "
            + tc
            + f" {vs} ".join(
                str(cell)
                .replace("\n", "\\n")
                .ljust(maxKeyWidth if cell == key else maxValueWidth)
                for cell in [key, value]
            )
            + borderCol
            + vs
            + "\n"
        )
    tableWidth = maxKeyWidth + maxValueWidth + 4
    border = ""
    spacer = ""
    for i in range(tableWidth):
        spacer += " "
        border += "─"
    table = (
        borderCol
        + "┌"
        + border
        + "┐\n"
        + vs
        + tc
        + (" " + title).ljust(tableWidth)
        + borderCol
        + vs
        + "\n"
        + vs
        + spacer
        + vs
        + "\n"
        + tableHeaders
        + table
        + "└"
        + border
        + "┘"
        + bcolors.ENDC
    )
    print(table)
