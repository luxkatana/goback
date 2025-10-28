import asyncio
from datetime import datetime
from threading import Thread
import email_validator
import aiomysql
import secrets
from flask import (
    Flask,
    jsonify,
    make_response,
    Response,
    request,
)
from flask_cors import CORS
from httpx import HTTPStatusError
from sqlalchemy import create_engine
from scraper import main as scrape_site
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from extensions import db
from appwrite_session import AppwriteSession
from models import JobTask, User
from config_manager import ConfigurationHolder, get_tomllib_config
from werkzeug.security import check_password_hash, generate_password_hash


success, correspondingval = get_tomllib_config()
if not success:
    print(f"ERROR: while parsing toml gave error: {correspondingval}")
    exit(1)

conf_holder: ConfigurationHolder = correspondingval


app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_urlsafe(40)
app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(40)
jwt = JWTManager(app)

try:
    with create_engine(conf_holder.sqlalchemy_connection_uri).connect() as _:
        ...
    app.config["SQLALCHEMY_DATABASE_URI"] = conf_holder.sqlalchemy_connection_uri
except Exception as e:
    if conf_holder.use_sqlite_as_fallback_option is True:
        print(
            "WARNING: using sqlite memory as fallback option, main db choice gave error: ",
            e,
        )
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        print(app.config["SQLALCHEMY_DATABASE_URI"])
    else:
        raise e


db.init_app(app)
with app.app_context():
    db.create_all()


@app.post("/api/login")
async def login() -> Response:
    json_payload = request.get_json()
    email = json_payload.get("email")
    password = json_payload.get("password")
    if email and password:
        corresponding_user = db.session.query(User).where(User.email == email).first()
        if (
            corresponding_user is not None
            and check_password_hash(corresponding_user.password, password) is True
        ):
            access_token = create_access_token(email)
            return jsonify(access_token=access_token)
        else:
            return jsonify(error=2, msg="Bad credentials")

    return jsonify(error=1, msg="email and password is missing")


@app.get("/api/job/<string:job_id>")
@jwt_required()
async def job_status_route(job_id: str) -> Response:
    usr_email: str = get_jwt_identity()
    user_id = db.session.query(User).where(User.email == usr_email).first().user_id
    jobtask = (
        db.session.query(JobTask)
        .where(JobTask.user_id == user_id, JobTask.job_id == job_id)
        .first()
    )
    if jobtask is None:
        return jsonify(error=1, msg=f"There is no jobtask with id {job_id}")
    return jsonify(jobtask.as_dict())


def task_handler(user_id: int, job_id: int, url: str):
    with app.app_context():
        user = db.session.query(User).where(User.user_id == user_id).first()
        job = db.session.query(JobTask).where(JobTask.job_id == job_id).first()
        try:
            file_id = asyncio.run(scrape_site(url, user, job))
        except HTTPStatusError as e:
            if e.request.url == url:
                job.change_status(
                    f"requested URL host sent error code {e.response.status_code}"
                )
            else:
                job.change_status(
                    f"Asset of requested URL has sent error code {e.response.status_code}"
                )
        except Exception as e:
            job.change_status(str(e))
        else:
            job.change_status(f"Success: {file_id}")
        print("Finished")
        print(job.status)
        # db.session.add(job)
        db.session.commit()


@app.post("/api/scrape")
@jwt_required()
async def scrape_site_route() -> Response:
    user = db.session.query(User).where(User.email == get_jwt_identity()).first()
    json_payload = request.get_json()
    url = json_payload.get("url")
    if not url:
        return jsonify(error=1, msg="URL is missing")

    new_job = JobTask(user_id=user.user_id, created_at=datetime.now())
    db.session.add(new_job)
    db.session.commit()

    Thread(target=task_handler, args=(user.user_id, new_job.job_id, url)).start()

    return jsonify(
        msg="Created and accepted (is running as bg task)", job_task_id=new_job.job_id
    )


@app.post("/api/signup")
async def signup() -> Response:
    json_payload = request.get_json()
    email = json_payload.get("email")
    password = json_payload.get("password")
    username = json_payload.get("username")
    if db.session.query(User).where(User.email == email).first() is not None:
        return jsonify(error=1, msg="Email exists, use another email")

    if len(username) >= 10:
        return jsonify(error=2, msg="Username should be max 10 characters")
    elif len(password) >= 210:
        return jsonify(error=3, msg="Password should be max 210 characters")
    elif len(email) >= 254:
        return jsonify(error=4, msg="Email should be max 254 characters")
    try:
        email_validator.validate_email(email)
    except email_validator.EmailNotValidError:
        return jsonify(error=5, msg="Email is not valid")

    hashed_password = generate_password_hash(password)
    newuser = User(username=username, password=hashed_password, email=email)
    db.session.add(newuser)
    db.session.commit()
    access_token = create_access_token(email)
    return jsonify(created=True, access_token=access_token)


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


if __name__ == "__main__":

    app.run(
        host=conf_holder.webserver_host,
        port=conf_holder.webserver_port,
        debug=conf_holder.debug_mode,
    )
