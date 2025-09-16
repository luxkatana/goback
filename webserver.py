from flask import Flask, render_template, Response, Request
from dotenv import load_dotenv
from os import getenv

load_dotenv()


app = Flask(__name__)


@app.route("/login")
async def login() -> Response:
    return render_template("login.html")


@app.route("/signup")
async def signup() -> Response:
    return render_template("signup.html")


@app.get("/")
async def index() -> Response:
    return render_template("index.html")


if __name__ == "__main__":
    WEBSERVER_HOST = getenv("WEBSERVER_HOST")
    WEBSERVER_PORT = getenv("WEBSERVER_PORT")
    DEBUG_MODE = getenv("FLASK_DEBUG_MODE", "").lower() in {"yes", "y"}

    app.run(host=WEBSERVER_HOST, port=WEBSERVER_PORT, debug=DEBUG_MODE)
