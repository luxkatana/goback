from io import BytesIO

from sqlmodel import Session
from hashlib import sha256
from models import SitesMetadata, db_engine
from config_manager import get_tomllib_config, validate_appwrite_credentials
import httpx

holder = get_tomllib_config()

APPWRITE_API_KEY = holder.api_key
APPWRITE_ENDPOINT = holder.endpoint_url
APPWRITE_PROJECT_ID = holder.project_id
APPWRITE_STORAGE_BUCKET_ID = holder.storage_bucket_id
validate_appwrite_credentials(holder)


class AssetsCache:
    def __init__(self, existing: dict[str, str] = None) -> None:
        self.cache: dict[str, str] = existing or {}

    @property
    def empty(self) -> bool:
        return len(self.cache.keys()) == 0

    def get_truncated_hash(self, original_file_id: str) -> str | None:
        return self.cache[original_file_id]

    def add_to_cache(self, original_hash: str, truncated_hash: str):
        self.cache[original_hash] = truncated_hash

    def exists(self, original_hash: str) -> bool:
        return isinstance(self.cache.get(original_hash, None), str)


def hash_sha256_to_36(content: bytes | str) -> str:
    return sha256(
        content if isinstance(content, bytes) else content.encode()
    ).hexdigest()[:36]


async def insert_site_row(site_url: str, document_file_id: str, user_id: int = -1):
    with Session(db_engine) as db_session:
        new_metadata = SitesMetadata(
            site_url=site_url, document_file_id=document_file_id, user_id=user_id
        )
        db_session.add(new_metadata)
        db_session.commit()


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
    ) -> None:
        with BytesIO() as io:
            io.write(file_content)
            response = await self.httpx_client.post(
                f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_STORAGE_BUCKET_ID}/files",
                data={"fileId": file_identifier},
                files={"file": (file_identifier, io, "text/plain")},
            )
            response.raise_for_status()

    async def get_file_content(self, appwrite_file_id: str) -> bytes:

        response = await self.httpx_client.get(
            f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_STORAGE_BUCKET_ID}/files/{appwrite_file_id}/download"
        )
        return response.raise_for_status().content
