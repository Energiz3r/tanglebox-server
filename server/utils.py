import torch
import json

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

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

bc = bcolors.OKGREEN
tc = bcolors.WARNING
th = bcolors.OKBLUE
vs = "│"

def printDictAsTable(dict, title="Table output:", headers = ["Key", "Value"]):
    table = ""
    maxKeyWidth = max(len(str(key)) for key in dict.keys())
    maxValueWidth = max(len(str(value)) for value in dict.values())
    if maxValueWidth < 8:
        maxValueWidth = 8
    tableHeaders = bc + vs + " " + th +  "   ".join(cell.ljust(maxKeyWidth if cell == headers[0] else maxValueWidth) for cell in headers) + bc + vs + "\n"
    for key, value in dict.items():
        table += bc + vs + " " + tc + f" {vs} ".join(str(cell).ljust(maxKeyWidth if cell == key else maxValueWidth) for cell in [key, value]) + bc + vs + "\n"
    tableWidth = maxKeyWidth + maxValueWidth + 4
    border = ""
    spacer = ""
    for i in range(tableWidth):
        spacer += " "
        border += "─"
    table = bc + "┌" + border + "┐\n" + vs + tc + (" " + title).ljust(tableWidth) + bc + vs + "\n" + vs + spacer + vs + "\n" + tableHeaders + table + "└" + border + "┘" + bcolors.ENDC
    print(table)


def processConvo(convo, humanRole, aiRole):
    try:
        convHistoryList = json.loads(convo)
    except json.JSONDecodeError:
        return "Invalid conversationHistory JSON"

    if not isinstance(convHistoryList, list):
        return 'conversationHistory JSON structure must be an array of arrays, eg. [["Human","How do magnets work?"],["AI","They just do"]]'

    convHistoryPyList = []

    for item in convHistoryList:
        if not isinstance(item, list) or len(item) != 2:
            return 'Each conversationHistory subarray must contain exactly 2 values - role and message, eg. [["Human","How do magnets work?"],["AI","They just do"]]'

        role, message = item
        if role not in ('Human', 'AI'):
            return "conversationHistory roles must only be either 'Human' or 'AI'."

        role = humanRole if role == 'Human' else aiRole
        convHistoryPyList.append((role, message))

    return convHistoryPyList