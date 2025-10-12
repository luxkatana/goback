import aiomysql
from flask import Flask, make_response, render_template, Response
from dotenv import load_dotenv
from os import getenv
from appwrite_session import AppwriteSession

load_dotenv()


app = Flask(__name__)


@app.route("/login")
async def login() -> Response:
    return render_template("login.html")


@app.route("/signup")
async def signup() -> Response:
    return render_template("signup.html")


@app.get("/media/<string:file_id>")
async def get_media(file_id: str):
    if len(file_id) != 32:  # Is een md5 hash, en die heeft altijd 32 karakters
        return "Invalid file id"

    async with AppwriteSession() as session:
        file_fetch_response = await session.get_file_content(file_id)
        response_object = make_response(file_fetch_response)

        async with session.mysql_conn.cursor() as cursor:
            cursor: aiomysql.Cursor
            await cursor.execute(
                "SELECT mimetype FROM goback_assets_metadata WHERE file_id = %s;",
                (file_id,),
            )
            result = tuple(await cursor.fetchall())
            if (
                len(result) == 0 or (inner_str := result[0][0]) == "any"
            ):  # Assume its just a text/plain
                response_object.content_type = "text/html"
            else:
                response_object.content_type = inner_str

    return response_object


@app.get("/")
async def index() -> Response:
    return render_template("index.html")


if __name__ == "__main__":
    WEBSERVER_HOST = getenv("WEBSERVER_HOST")
    WEBSERVER_PORT = getenv("WEBSERVER_PORT")
    DEBUG_MODE = getenv("FLASK_DEBUG_MODE", "").lower() in {"yes", "y"}

    app.run(host=WEBSERVER_HOST, port=WEBSERVER_PORT, debug=DEBUG_MODE)
