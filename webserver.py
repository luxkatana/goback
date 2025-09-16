from flask import Flask
from dotenv import load_dotenv
from os import getenv

load_dotenv()


app = Flask(__name__)


if __name__ == "__main__":
    WEBSERVER_HOST = getenv("WEBSERVER_HOST")
    WEBSERVER_PORT = getenv("WEBSERVER_PORT")
    DEBUG_MODE = getenv("FLASK_DEBUG_MODE", "").lower() in {"yes", "y"}

    app.run(host=WEBSERVER_HOST, port=WEBSERVER_PORT, debug=DEBUG_MODE)
