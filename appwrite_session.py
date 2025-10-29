from hashlib import md5, sha256
from io import BytesIO

from sqlmodel import Session
from models import SitesMetadata, db_engine
from config_manager import get_tomllib_config
import httpx

holder = get_tomllib_config()

APPWRITE_API_KEY = holder.api_key
APPWRITE_ENDPOINT = holder.endpoint_url
APPWRITE_PROJECT_ID = holder.project_id
APPWRITE_STORAGE_BUCKET_ID = holder.storage_bucket_id


async def insert_site_row(site_url: str, document_file_id: str, user_id: int = -1):
    with Session(db_engine) as db_session:
        new_metadata = SitesMetadata(
            site_url=site_url, document_file_id=document_file_id, user_id=user_id
        )
        db_session.add(new_metadata)
        db_session.commit()


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
        self.httpx_client: httpx.AsyncClient | None = None


class AppwriteSession:
    async def __aenter__(self):
        self.httpx_client = httpx.AsyncClient(
            headers={
                "X-Appwrite-Project": APPWRITE_PROJECT_ID,
                "X-Appwrite-Key": APPWRITE_API_KEY,
            }
        )
        return self

    async def __aexit__(self, *_):
        if self.httpx_client is not None:
            await self.httpx_client.aclose()

    def __init__(self): ...

    async def appwrite_publish_media(
        self, file_identifier: str, file_content: bytes
    ) -> SavedFile:

        with BytesIO() as io:
            io.write(file_content)
            md5_file_id = md5(file_identifier.encode()).hexdigest()

            response = await self.httpx_client.post(
                f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_STORAGE_BUCKET_ID}/files",
                data={"fileId": md5_file_id},
                files={"file": (file_identifier, io, "text/plain")},
            )

            response.raise_for_status()
            """self.storage.create_file(
                APPWRITE_STORAGE_BUCKET_ID,
                md5_file_id,
                InputFile.from_bytes(file_content.encode(), file_identifier),
            )"""

            return SavedFile(file_identifier, md5_file_id)

    async def get_file_content(self, appwrite_file_id: str) -> bytes:

        response = await self.httpx_client.get(
            f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_STORAGE_BUCKET_ID}/files/{appwrite_file_id}/download"
        )
        return response.content
