import asyncio
import pickle
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Path, status, Response
from fastapi.responses import FileResponse
import jwt
import datetime
from threading import Thread
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from httpx import HTTPStatusError
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware
from scraper import main as scrape_site
from appwrite_session import AppwriteSession
from fastapi.staticfiles import StaticFiles
from models import (
    SECRET_KEY,
    AssetMetadata,
    JobTask,
    Status,
    StatusTypesEnum,
    User,
    get_db_session,
    hasher,
    db_engine,
)
from config_manager import ConfigurationHolder, get_tomllib_config

conf_holder: ConfigurationHolder = get_tomllib_config()

app = FastAPI()
prod_mode = False
try:
    app.mount(
        "/assets",
        StaticFiles(directory="./goback-frontend/dist/assets"),
        name="frontend",
    )
    prod_mode = True
except RuntimeError:
    print(
        "Detecting development/debugging mode (missing ./goback-frontend/dist/assets dir)"
    )
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")
db_annotated = Annotated[Session, Depends(get_db_session)]
app.add_middleware(  # Testing purposes
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


async def get_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: db_annotated
) -> User:
    try:
        jwt_decoded = jwt.decode(token, SECRET_KEY, "HS256")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    username = jwt_decoded["sub"]
    return db.exec(select(User).where(User.username == username)).first()


user_annotated = Annotated[User, Depends(get_user)]


if prod_mode:

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse("./goback-frontend/dist/index.html")

    @app.get("/favicon.ico")
    def favicon() -> FileResponse:
        return FileResponse("./goback-frontend/dist/favicon.ico")


@app.get("/api/validate", status_code=status.HTTP_200_OK)
async def validate_access_token(usr: user_annotated):
    del usr.password
    return usr


@app.post("/api/login", status_code=status.HTTP_200_OK)
async def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_annotated
):
    username = credentials.username
    password = credentials.password
    corresponding_user = db.exec(select(User).where(User.username == username)).first()
    if (
        corresponding_user is not None
        and hasher.verify(password, corresponding_user.password) is True
    ):
        access_token = jwt.encode(
            {
                "sub": username,
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=10),
            },
            SECRET_KEY,
            "HS256",
        )
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(401, detail="credentials are invalid")


@app.get("/api/job", status_code=status.HTTP_200_OK)
async def job_status_route(job_id: int, user: user_annotated, db: db_annotated):
    jobtask = db.exec(
        select(JobTask).where(JobTask.user_id == user.user_id, JobTask.job_id == job_id)
    ).first()
    if jobtask is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Jobtask not found")

    loaded: list[str] = pickle.loads(jobtask.status_messages)

    response = jobtask.as_dict()
    response["status_messages"] = loaded
    return response


def task_handler(user_id: int, job_id: int, url: str, db: Session) -> bool:
    user = db.exec(select(User).where(User.user_id == user_id)).first()
    is_ok = False
    job = db.exec(select(JobTask).where(JobTask.job_id == job_id)).first()
    try:
        file_id = asyncio.run(scrape_site(url, user, job, db))
    except HTTPStatusError as e:
        if e.request.url == url:
            job.add_status_message(
                f"requested URL host sent error code {e.response.status_code}",
                StatusTypesEnum.ERROR,
            )
        else:
            job.add_status_message(
                f"Asset of requested URL has sent error code {e.response.status_code}",
                StatusTypesEnum.ERROR,
            )
    except Exception as e:
        job.add_status_message(str(e), StatusTypesEnum.ERROR)
    else:
        job.add_status_message(file_id, StatusTypesEnum.SUCCESS)
        is_ok = True

    db.commit()
    if user_id != -1:
        db.close()
    return is_ok


class ScrapeUrlPayload(BaseModel):
    url: HttpUrl = Field(max_length=100)


@app.post("/api/scrape", status_code=status.HTTP_202_ACCEPTED)
async def scrape_site_route(
    db: db_annotated, user: user_annotated, url_payload: ScrapeUrlPayload
):
    new_job = JobTask(
        user_id=user.user_id,
        created_at=datetime.datetime.now(),
        status_messages=pickle.dumps(
            [Status(message="Job started", status_type=StatusTypesEnum.INFO)]
        ),
    )
    db.add(new_job)
    db.commit()

    Thread(
        target=task_handler, args=(user.user_id, new_job.job_id, str(url_payload.url), Session(db_engine))
    ).start()
    return {"job_id": new_job.job_id}


class SignupCredentials(BaseModel):
    username: str = Field(max_length=30)
    password: str = Field(max_length=30, min_length=8)
    email: EmailStr = Field(max_length=255)


@app.post("/api/signup", status_code=status.HTTP_201_CREATED)
async def signup(db: db_annotated, signupcreds: SignupCredentials):
    email = signupcreds.email
    password = signupcreds.password
    username = signupcreds.username
    if db.exec(select(User).where(User.username == username)).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username exists"
        )

    hashed_password = hasher.hash(password)
    newuser = User(username=username, password=hashed_password, email=email)
    db.add(newuser)
    db.commit()
    access_token = jwt.encode(
        {
            "sub": username,
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=10),
        },
        SECRET_KEY,
        "HS256",
    )
    return {"access_token": access_token}


@app.get("/api/jobs")
async def get_jobs(user: user_annotated, db: db_annotated):
    jobs = db.exec(select(JobTask).where(JobTask.user_id == user.user_id)).all()

    def deserialize_object(job: JobTask) -> dict:
        dict_return = job.model_dump(exclude="status_messages")
        dict_return["status_messages"] = pickle.loads(job.status_messages)
        return dict_return

    jobs = list(map(deserialize_object, jobs))
    return {"length": len(jobs), "jobs": jobs}


@app.get("/media/{file_id}")
async def get_media(
    file_id: Annotated[str, Path(max_length=36, min_length=36)], db: db_annotated
):
    if file_id == "000000000000000000000000000000000000":
        return {"detail": "Could not load element:("}
    async with AppwriteSession() as session:
        file_fetch_response = await session.get_file_content(
            file_id
        )  # A fallback if it doesn't exist
        response_object = Response(file_fetch_response)
        result: AssetMetadata = db.exec(
            select(AssetMetadata).where(AssetMetadata.file_id == file_id)
        ).first()

        if result is None or result.mimetype == "any":  # Assume its just a text/plain
            response_object.media_type = "text/html"
        else:
            response_object.media_type = result.mimetype

    return response_object
