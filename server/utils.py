import json

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

def createChunk(content: str, stop: bool = False):
    return bytes(f'data: {{"content":{json.dumps(content)},"stop":"{stop}"}}\n\n', 'utf-8')

def checkApiToken(token):
    try:
        with open("apiTokens.txt", "r") as file:
            tokensList = file.read().splitlines()
    except FileNotFoundError:
        print("API tokens file not found")
        tokensList = []
    for tokenLine in tokensList:
        pair = tokenLine.split(':')
        if pair[1] == 'TOKEN':
            continue
        if pair[1] == token:
            return True
    return False

    # @app.route("/test", methods=['POST'])
    # def testRoute():
    #     def generate_test_response():
    #         start_time = time.time()
    #         while time.time() - start_time < 12:
    #             if time.time() - start_time > 10:
    #                 yield bytes('data: {"content":"finished","stop":true}\n\n', 'utf-8')    
    #             else:
    #                 yield bytes('data: {"content":"hello world","stop":false}\n\n', 'utf-8')
    #             time.sleep(2)
    #     return Response(stream_with_context(generate_test_response()), content_type="text/event-stream")