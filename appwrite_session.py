from dotenv import load_dotenv
from typing import Any
from os import environ
from appwrite.client import Client
from hashlib import md5, sha256
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile
import aiomysql

# TODO: https requests maken met httpx voor echte async

load_dotenv()
APPWRITE_API_KEY = environ["APPWRITE_KEY"]
APPWRITE_ENDPOINT = environ["APPWRITE_ENDPOINT"]
APPWRITE_PROJECT_ID = environ["APPWRITE_PROJECT_ID"]
APPWRITE_STORAGE_BUCKET_ID = environ["APPWRITE_STORAGE_BUCKET_ID"]
MYSQL_HOST = environ["MYSQL_HOST"]
MYSQL_USER = environ["MYSQL_USER"]
MYSQL_PASS = environ["MYSQL_PASSWORD"]
MYSQL_DB = environ["MYSQL_DB"]


async def insert_site_row(site_url: str, document_file_id: str):
    async with aiomysql.connect(
        MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB
    ) as connection:
        async with connection.cursor() as cursor:
            cursor: aiomysql.Cursor
            await cursor.execute(
                "INSERT INTO goback_sites_metadata (site_url, document_file_id) VALUES (%s,%s)",
                (site_url, document_file_id),
            )

        await connection.commit()


def create_file_identifier(file_content: str, host_url: str) -> str:
    """
    Maakt een naam/identifier voor een bepaalde media.
    Is gebasseerd op het volgende formaat:
        <sha256hash(file_content)_<sha256hash(host_url)>>

    De reden waarom we de file_content nemen, is om elke media te "identificeren" dmv de sha256 hash
    """
    file_content_sha256 = sha256(file_content.encode()).hexdigest()
    host_url_sha256 = sha256(host_url.encode()).hexdigest()
    return f"{file_content_sha256}_{host_url_sha256}"


class SavedFile:
    def __init__(self, file_identifier: str, appwrite_file_id: str):
        self.file_identifier = file_identifier
        self.appwrite_file_id = appwrite_file_id


class AppwriteSession:
    def __init__(self):
        self.client = (
            Client()
            .set_endpoint(APPWRITE_ENDPOINT)
            .set_project(APPWRITE_PROJECT_ID)
            .set_key(APPWRITE_API_KEY)
        )
        self.storage = Storage(self.client)

    async def appwrite_publish_media(
        self, file_identifier: str, file_content: str
    ) -> SavedFile:
        # TODO: check if file exists n stuff

        md5_file_id = md5(file_identifier.encode()).hexdigest()
        self.storage.create_file(
            APPWRITE_STORAGE_BUCKET_ID,
            md5_file_id,
            InputFile.from_bytes(file_content.encode(), file_identifier),
        )

        return SavedFile(file_identifier, md5_file_id)

    async def get_file_metadata(self, appwrite_file_id: str) -> dict[str, Any]:
        metadata = self.storage.get_file(APPWRITE_STORAGE_BUCKET_ID, appwrite_file_id)
        return metadata

    async def get_file_content(self, appwrite_file_id: str) -> bytes:
        return self.storage.get_file_download(
            APPWRITE_STORAGE_BUCKET_ID, appwrite_file_id
        )
