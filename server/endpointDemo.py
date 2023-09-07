from flask import Flask, render_template, request, Response, abort
import requests
import json

# example of an event-stream chunk:
#   data: {"content":"some text","stop":false}\n\n


def parseChunkContent(chunk):
    chunkStr = chunk.decode("utf-8")
    chunkSplit = chunkStr.split("data:")
    chunkContent = ""
    for eventObjectJson in chunkSplit:
        if len(eventObjectJson):
            eventObjectJsonClean = eventObjectJson.strip()
            while (
                eventObjectJsonClean[-2:] == "\\n"
            ):  # remove trailing escaped \n from string eg {"content":"stuff"}\\n\\n
                eventObjectJsonClean = eventObjectJsonClean[:-2]
            try:
                eventObject = json.loads(eventObjectJsonClean)
                if "content" in eventObject:
                    chunkContent += str(eventObject["content"])
            except json.decoder.JSONDecodeError:
                print(f"Json decode error parsing chunk: '{chunk}'")
    return chunkContent


app = None


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route(f"/api", methods=["POST"])
def eventStreamRoute():
    data = request.get_json()
    if not "payload" in data:
        abort(400, "Payload missing from request")

    def generateProxyStreamingResponse():
        entireResponse = ""
        try:
            req = requests.post("http://192.168.1.10:3000", json=data, stream=True)
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    entireResponse += parseChunkContent(chunk)
                    yield chunk
        except request.exceptions.RequestException as e:
            app.logger.error("Error reading from endpoint: {0}".format(e))
            yield str(e)
        print(f"Response:", entireResponse)

    return Response(
        generateProxyStreamingResponse(),
        content_type="application/json",
    )


if __name__ == "__main__":
    app = Flask(__name__)
    app.run(host="0.0.0.0", port=8080)
