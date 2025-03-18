import uuid
import time
import re
import json

def openAiToMixtral(data, wasSystem, system):
    
    messages = ""
    for i, message in enumerate(data["messages"]):
        content = message["content"]
        if message["role"] == "user":
            if wasSystem and i < 2:
                messages += f"[INST] {system} {content} [/INST]"
            else:
                if i < 1:
                    messages += f"[INST] {content} [/INST]"
                else:
                    messages += f"<s>[INST] {content} [/INST]"
        if message["role"] == "assistant":
            messages += f" {content} </s>"

    stop = "{\"stop\": [\"</s>\",\"###\"]"
    return { "prompt": messages, "stop": stop, "stream": False }


def formatOpenAiRequest(data, abort):
    wasSystem = False
    system = ""
    for message in data["messages"]:
        content = message["content"]
        if not "role" in message or not content:
            abort(400, "malformed 'messages' property")
        if message["role"] == "system":
            wasSystem = True
            system = data["messages"][0]["content"]

    wasFunction = False
    if "tool_choice" in data:
        wasFunction = True
        wasSystem = True
        system = getFunctionPrompt(str(data["tools"]))

    requestBody = openAiToMixtral(data, wasSystem, system)

    return (requestBody, wasFunction)

def getFunctionPrompt(function: str):
    return 'You are a function executing AI model. '\
        'For this function call, return a json object containing the resultant data for each function within <tool_call></tool_call> XML tags as follows: <tool_call> [{"function":"Name","arguments":"Result"}] </tool_call> '\
        'The functions are self-contained, and include a description instructions on how to determine the response. '\
        'Here are the function(s) you are to execute: '\
        + function +\
        ' Don\'t make assumptions about what values to plug into functions. '\
        'Don\'t explain your result or decision. '\
        'Don\'t offer any further assistance.'


def getOutputObj(model: str, usage, wasFunction: bool, response: str):
    toolCalls = None
    toolsError = None
    if wasFunction:
        open_tag_pos = response.index('<tool_call>')
        close_tag_pos = response.index('</tool_call>')
        extracted_text = response[open_tag_pos + len('<tool_call>'): close_tag_pos]
        if not extracted_text:
            toolsError = "tool_call tags not found in function response!"
        else:
            try:
                functionOutput = json.loads(extracted_text)
            except:
                toolsError = "function response could not be parsed!"
            
            if isinstance(functionOutput, list):
                toolCalls = []
                for function in functionOutput:
                    try:
                        toolCalls.append({
                            "id": str(uuid.uuid4()),
                            "type": "function",
                            "function": {
                                "name": function["function"],
                                "arguments": json.dumps(function["arguments"])
                            }
                        })
                    except:
                        toolsError = "values were missing from function results!"
            else:
                toolsError = "function result was not a valid list!"

    if (toolsError != None):
        raise Exception("Error handling function call:", toolsError)

    choices = [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": None if wasFunction else response,
            "tool_calls": toolCalls
        },
        "logprobs": None,
        "finish_reason": "stop"
    }]
    return {"id": str(uuid.uuid4()), "object": "chat.completion", "created": int(time.time()), "model": model, "choices": choices, "usage": usage}


# <tool_call>
# [
#   {
#     "function": "Classification",
#     "arguments": {
#       "classification": "unrelated",
#       "is_blacklisted": false,
#       "blacklisted_topic_match": "",
#       "is_off_topic": true,
#       "off_topic_match": "greeting"
#     }
#   }
# ]
# </tool_call>
