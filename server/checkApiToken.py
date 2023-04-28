
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