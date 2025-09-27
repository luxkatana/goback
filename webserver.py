from flask import Flask, render_template, Response, Request, send_file
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
from appwrite_session import AppwriteSession

load_dotenv()


app = Flask(__name__)
appwritesession = AppwriteSession()


@app.route("/login")
async def login() -> Response:
    return render_template("login.html")


@app.route("/signup")
async def signup() -> Response:
    return render_template("signup.html")


@app.get("/media/<string:file_id>")
async def get_media(file_id: str):
    if len(file_id) != 32:
        return "Invalid file id"
    file_fetch_response = await appwritesession.get_file(file_id)
    return file_fetch_response


@app.get("/")
async def index() -> Response:
    return render_template("index.html")


if __name__ == "__main__":
    WEBSERVER_HOST = getenv("WEBSERVER_HOST")
    WEBSERVER_PORT = getenv("WEBSERVER_PORT")
    DEBUG_MODE = getenv("FLASK_DEBUG_MODE", "").lower() in {"yes", "y"}

    app.run(host=WEBSERVER_HOST, port=WEBSERVER_PORT, debug=DEBUG_MODE)
