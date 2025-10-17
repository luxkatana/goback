import aiomysql
import secrets
from flask import Flask, make_response, redirect, render_template, Response
import flask_login
from extensions import db
from dotenv import load_dotenv
from os import environ, getenv
from appwrite_session import AppwriteSession
from models import User
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_required, login_user, logout_user
import forms


load_dotenv()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = environ["MYSQL_CONNECTION_STRING"]
app.secret_key = secrets.token_urlsafe(40)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    return db.session.query(User).where(User.user_id == user_id).first()


db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/login", methods=["GET", "POST"])
async def login() -> Response:
    form = forms.LoginForm()
    msg = ""
    if form.validate_on_submit():
        corresponding_user = (
            db.session.query(User).where(User.email == form.email.data).first()
        )

        if (
            corresponding_user is not None
            and check_password_hash(corresponding_user.password, form.password.data)
            is True
        ):
            msg = "Correct!"
            login_user(corresponding_user)
            return redirect("/dashboard")
        else:
            msg = "Invalid user/password"

    return render_template("login.html", form=form, msg=msg)


@app.get("/dashboard")
@login_required
def dashboard_route() -> Response:
    print(flask_login.current_user)
    return render_template("dashboard.html", current_user=flask_login.current_user)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create_route() -> Response:
    pass


@app.get("/logout")
def logout_route() -> Response:
    logout_user()
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
async def signup() -> Response:
    registration_form = forms.RegistrationForm()
    message = ""
    if registration_form.validate_on_submit():
        if (
            db.session.query(User)
            .where(User.email == registration_form.email.data)
            .first()
            is not None
        ):
            message = "This email is already taken, make another one "
        else:
            hashed_password = generate_password_hash(registration_form.email.data)
            newuser = User(
                username=registration_form.username.data,
                password=hashed_password,
                email=registration_form.email.data,
            )
            db.session.add(newuser)
            db.session.commit()
            login_user(newuser)
            return redirect("/dashboard")

    return render_template("signup.html", form=registration_form, message=message)


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
    return render_template("index.html", current_user=flask_login.current_user)


if __name__ == "__main__":
    WEBSERVER_HOST = getenv("WEBSERVER_HOST")
    WEBSERVER_PORT = getenv("WEBSERVER_PORT")
    DEBUG_MODE = getenv("FLASK_DEBUG_MODE", "").lower() in {"yes", "y"}

    app.run(host=WEBSERVER_HOST, port=WEBSERVER_PORT, debug=DEBUG_MODE)
