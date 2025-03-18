from settings import loadWebSettings
from endpoints import loadEndpoints
from eventStreamEndpoint import eventStreamRouteHandler
from openAiToLlama import openAiToLlama
import logging
from flask import (
    Flask,
    render_template,
    Response,
    url_for,
    session,
    redirect,
    request,
    send_from_directory
)
from basicQueue import BasicQueue
from utils import remove_keys_from_dict
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
import os
import glob
from dotenv import load_dotenv
load_dotenv()

GOOGLE_DISCOVERY_URL = os.getenv('GOOGLE_DISCOVERY_URL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_APP_SECRET_KEY = os.getenv('GOOGLE_APP_SECRET_KEY')

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


def initWebServer(app, authClient, queue):

    @app.route('/robots.txt')
    @app.route('/sitemap.xml')
    def static_from_root():
        return send_from_directory(app.static_folder, request.path[1:])

    @app.route("/", methods=["GET"])
    def index():
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if not ip:
            ip = request.remote_addr
        print(ip + " requested index.html")
        userInfo = {
            "isLoggedIn": False,
            "userName": "",
            "googleId": "",
            "email": "",
            "profilePic": "",
            "isAdmin": False,
        }
        if "userName" in session:
            settings = loadWebSettings()
            userInfo["isLoggedIn"] = True
            userInfo["userName"] = session["userName"]
            userInfo["googleId"] = session["googleId"]
            userInfo["email"] = session["email"]
            userInfo["profilePic"] = session["profilePic"]
            if settings["adminGoogleId"] != "":
                if session["googleId"] == settings["adminGoogleId"]:
                    userInfo["isAdmin"] = True
            print(userInfo)

        return render_template(
            "index.html",
            userInfo=json.dumps(userInfo),
        )

    
    @app.route("/api/available-endpoints", methods=["POST"])
    def fetchAvailableEndpoints():
        endpoints = loadEndpoints()
        endpointList = []
        for endpoint in endpoints:
            # don't include these values in the response
            if endpoint["isEnabled"]:
                endpointList.append(
                    remove_keys_from_dict(endpoint, ["serverAddress", "port"])
                )
        return Response(json.dumps(endpointList), content_type="application/json")

    for endpoint in loadEndpoints(True):
        if endpoint["isEnabled"]:
            eventStreamRouteHandler(
                app,
                endpoint,
                "api/",
                queue
            )
        else:
            print(f'Endpoint is DISABLED: {endpoint["urlSuffix"]} / {endpoint["label"]}')

    openAiToLlama(app, queue)

    @app.route("/login")
    def login():
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        request_uri = authClient.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=request.base_url + "/callback",
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)

    @app.route("/logout")
    def logout():
        session.pop("userName", None)
        session.pop("googleId", None)
        session.pop("email", None)
        session.pop("profilePic", None)
        return redirect(url_for("index"))

    @app.route("/check-auth")
    def account():
        if "userName" in session:
            return "Hello, {}! ID: {}, Email: {}, Profile picture: {}, ".format(
                session["userName"],
                session["googleId"],
                session["email"],
                session["profilePic"],
            )
        else:
            return "Not logged in."

    @app.route("/login/callback")
    def authorize():
        code = request.args.get("code")
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]
        token_url, headers, body = authClient.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code,
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        authClient.parse_request_body_response(json.dumps(token_response.json()))
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = authClient.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            users_name = userinfo_response.json()["given_name"]
        else:
            return "User email not available or not verified by Google.", 400

        session["googleId"] = unique_id
        session["userName"] = users_name
        session["email"] = users_email
        session["profilePic"] = picture

        return redirect(url_for("index"))


if __name__ == "__main__":
    settings = loadWebSettings(True)
    app = Flask(__name__)
    queue = BasicQueue()
    app.secret_key = GOOGLE_APP_SECRET_KEY
    authClient = WebApplicationClient(GOOGLE_CLIENT_ID)
    initWebServer(app, authClient, queue)

    # hide errors if logging disabled
    if not settings["webDebugOutput"]:
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        app.logger.disabled = True
        log.disabled = True

    if settings["useSsl"]:
        templates = glob.glob('templates/**/*.html', recursive=True)
        static_files = glob.glob('./static/*', recursive=True)
        files_to_watch = templates + static_files
        app.run(host="0.0.0.0", port=settings["port"], ssl_context="adhoc", debug=True, extra_files=files_to_watch)
    else:
        app.run(host="0.0.0.0", port=settings["port"])
