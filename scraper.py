import aiomysql
from extensions import db
from bs4.element import PageElement
from bs4 import BeautifulSoup
import hashlib
from appwrite_session import (
    AppwriteSession,
    create_file_identifier,
    insert_site_row,
    APPWRITE_ENDPOINT,
    APPWRITE_STORAGE_BUCKET_ID,
)
from urllib.parse import urlparse
from dotenv import load_dotenv
import asyncio, bs4, httpx, os

from models import JobTask, User

load_dotenv()
URL_TAGS = frozenset(("href", "src"))


def findcorresponding_mimetype(element: PageElement) -> str:
    match element.name:
        case "script":
            return "application/javascript"

    if element.name == "link" and "stylesheet" in element.attrs.get("rel", []):
        return "text/css"

    return "any"


APPWRITE_KEY = os.getenv("APPWRITE_KEY")
HOST_WEBSERVER_URL = os.getenv("GOBACK_MEDIA_URL")
INTERACTIVE_MODE = __name__ == "__main__"


def dprint(*args, **kwargs) -> None:
    if INTERACTIVE_MODE:
        print(*args, **kwargs)
    else:
        print(f"[FROM WEBSERVER DBG MESSAGES]", *args, **kwargs)


class GobackScraper:
    def __init__(self, url: str):
        self.url = url
        self.httpx_client: httpx.AsyncClient = httpx.AsyncClient(follow_redirects=True)
        self.main_html_content: BeautifulSoup

    async def load_html(self) -> None:
        """
        Retrieves HTML content using the httpx module, and stores the HTML content in self.main_html_content
        May raise a httpx error in case of a HTTP status code that is everything except OK (200)
        """

        response = await self.httpx_client.get(self.url)
        response.raise_for_status()
        self.main_html_content = BeautifulSoup(response.text, "lxml")

    @staticmethod
    def get_useful_attributes(
        attributes: dict[str, str],
    ) -> dict[str, str] | None:
        keys = dict()
        for url_tag in URL_TAGS:
            if (
                corresponding_value := attributes.get(url_tag, None)
            ) is not None:  # Exists there
                keys[url_tag] = corresponding_value
        return keys

    def is_link_tag(tag: bs4.element.Tag) -> bool:
        return GobackScraper.get_useful_attributes(tag.attrs) != {}

    async def walk_through_native(
        self,
    ) -> list[tuple[dict[str, str], PageElement]] | list[None]:

        return list(
            map(
                lambda element: (GobackScraper.get_useful_attributes(element), element),
                self.main_html_content.find_all(GobackScraper.is_link_tag),
            )
        )

    # This may be useful in the future, in case we need more complexity
    """
    async def walk_through(
        self, elements: list[PageElement]
    ) -> list[PageElement] | None:
        useful_elements = []
        for element in elements:
            match type(element):

                case bs4.element.Tag:
                    element: bs4.element.Tag
                    if self.get_useful_attributes(element.attrs):  # If it isnt empty
                        useful_elements.append(element)

                    useful_elements.extend(await self.walk_through(element.children))

                case bs4.element.NavigableString:
                    ...
        return useful_elements
    """

    async def request_html_of_link(
        self, url: str, return_mimetype: bool = False
    ) -> tuple[httpx.Response, str]:
        response = await self.httpx_client.get(url)
        return (
            response.raise_for_status(),
            response.headers.get("Content-Type") if return_mimetype is True else False,
        )


async def main(
    url: str, user: User | None = None, job_task: JobTask | None = None
) -> str:
    dprint("TASK STARTED")
    scraper = GobackScraper(url)
    await scraper.load_html()

    useful_element = await scraper.walk_through_native()
    """
    if len(useful_element) == 0:
        dprint("Nothing to save")
        exit(0)
    """

    async with AppwriteSession() as session:
        for attributes, element in useful_element:
            # an attempt to catch the mime type by html tag

            mimetype = findcorresponding_mimetype(element)

            for key, value in attributes.items():
                url_check = urlparse(value)
                asset_response: None | httpx.Response = None
                if len(url_check.scheme) == 0 and any(
                    [url_check.path.startswith(x) for x in [".", "#"]]
                ):
                    dprint(
                        f"Scraper doesnt support urls such as {value} and therefore will be ignored"
                    )
                    continue

                if (
                    len(url_check.scheme) == 0 and len(url_check.path) != 0
                ):  # Doesnt have a scheme, and therefore is something like /here.jpg or here.jpg
                    url_check = urlparse(url)._replace(query=None, path=url_check.path)

                try:
                    asset_response, optional_mimetype = (
                        await scraper.request_html_of_link(
                            url_check.geturl(),
                            return_mimetype=(
                                asset_response == "any"
                            ),  # An attempt on obtaining the mime-type by response
                        )
                    )
                except httpx._exceptions.HTTPStatusError as e:
                    if job_task:
                        raise e
                    dprint(
                        f"Error when trying to fetch (this element will therefore be skipped) {url_check}\t{e}"
                    )
                    continue

                if optional_mimetype is not False:
                    mimetype = optional_mimetype
                unique_identifier = create_file_identifier(
                    asset_response.text, urlparse(url).hostname
                )
                try:
                    savedfile = await session.appwrite_publish_media(
                        unique_identifier, asset_response.content
                    )
                except Exception:
                    dprint(
                        "File exists on the server, but I am just going to delete that"
                    )
                    md5_hash = hashlib.md5(unique_identifier.encode()).hexdigest()
                    await session.httpx_client.delete(
                        f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_STORAGE_BUCKET_ID}/files/{md5_hash}"
                    )
                    # _response.raise_for_status()
                    savedfile = await session.appwrite_publish_media(
                        unique_identifier, asset_response.content
                    )

                element.attrs[key] = (
                    f"{HOST_WEBSERVER_URL}/media/{savedfile.appwrite_file_id}"
                )
                async with session.mysql_conn.cursor() as cursor:
                    cursor: aiomysql.Cursor
                    await cursor.execute(
                        "INSERT INTO goback_assets_metadata (file_id, mimetype) VALUES (%s, %s)",
                        (savedfile.appwrite_file_id, mimetype),
                    )
                    await session.mysql_conn.commit()
        site_document_indentifier = create_file_identifier(
            str(scraper.main_html_content), url
        )
        try:
            document_metadata = await session.appwrite_publish_media(
                site_document_indentifier, str(scraper.main_html_content).encode()
            )
        except Exception:
            md5_hash = hashlib.md5(site_document_indentifier.encode()).hexdigest()
            await session.httpx_client.delete(
                f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_STORAGE_BUCKET_ID}/files/{md5_hash}"
            )
            document_metadata = await session.appwrite_publish_media(
                site_document_indentifier, str(scraper.main_html_content).encode()
            )

        dprint("==========HTML_CONTENT==========")
        dprint(str(scraper.main_html_content))
        dprint("================================")

        dprint(
            "file id to access with through appwrite:",
            document_metadata.appwrite_file_id,
        )
        dprint(
            f"Link to access file (based on env vars): {HOST_WEBSERVER_URL}/media/{document_metadata.appwrite_file_id}"
        )
        await insert_site_row(
            url,
            document_metadata.appwrite_file_id,
            -1 if user is None else user.user_id,
        )
        return document_metadata.appwrite_file_id


if (
    INTERACTIVE_MODE
):  # Directly ran using the python3 interpreter, prevents accidental runs for example as importing this module
    url = input("Enter url to retrieve (live mode or something): ")
    url = (
        "https://cooletaseen.hondsrugcollege.com/document_img.html"
        if url == ""
        else url
    )  # Test url

    if not url.startswith("http"):
        url = f"http://{url}"
    asyncio.run(main(url))
