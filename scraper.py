from bs4.element import PageElement
from bs4 import BeautifulSoup
import hashlib
from rich import print
from sqlmodel import Session, select
from appwrite_session import (
    AppwriteSession,
    hash_sha256_to_36,
    insert_site_row,
    AssetsCache,
)
from urllib.parse import urljoin, urlparse
import asyncio, bs4, httpx


from models import AssetMetadata, JobTask, StatusTypesEnum, User, db_engine

from config_manager import get_tomllib_config, ConfigurationHolder

conf_holder: ConfigurationHolder = get_tomllib_config()
URL_TAGS = frozenset(("href", "src"))


def prepare_dummy_user() -> User:
    with Session(db_engine) as session:
        usr = session.exec(select(User).where(User.user_id == -1)).first()  # Guest id
        if usr is not None:
            return usr
        guestusr = User(  # Fake credentials, don't think these are real, luxkatana.eu doesn't even exist, GITGUARDIAN!!!
            user_id=-1,
            username="Guest user DO NOT DELETE",
            password="iamaguest!!!",
            email="someguests@luxkatana.eu",
        )
        session.add(guestusr)
        session.commit()
        return guestusr


def findcorresponding_mimetype(element: PageElement) -> str:
    match element.name:
        case "script":
            return "application/javascript"

    if element.name == "link" and "stylesheet" in element.attrs.get("rel", []):
        return "text/css"

    return "any"


APPWRITE_KEY = conf_holder.api_key

INTERACTIVE_MODE = __name__ == "__main__"


def dprint(*args, **kwargs) -> None:
    if INTERACTIVE_MODE:
        print(*args, **kwargs)
    else:
        print(f"[blue bold][FROM WEBSERVER DBG MESSAGES][/blue bold]", *args, **kwargs)


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

    async def request_html_of_link(
        self, url: str, return_mimetype: bool = False
    ) -> tuple[httpx.Response, str]:
        response = await self.httpx_client.get(url)
        return (
            response.raise_for_status(),
            response.headers.get("Content-Type") if return_mimetype is True else False,
        )


async def main(
    url: str,
    user: User | None = None,
    job_task: JobTask | None = None,
    recursive: bool = False,
    asset_cache: AssetsCache = None,
) -> str:
    if asset_cache == None:
        asset_cache = AssetsCache()

    if recursive == False:
        dprint("TASK STARTED")
    scraper = GobackScraper(url)
    prepare_dummy_user()
    await scraper.load_html()

    db_session = Session(db_engine)

    original_summary_of_html = hashlib.sha256(
        str(scraper.main_html_content).encode()
    ).hexdigest()
    useful_elements = await scraper.walk_through_native()
    if asset_cache.exists(original_summary_of_html):
        return asset_cache.get_truncated_hash(original_summary_of_html)

    async with AppwriteSession() as session:
        for attributes, element in useful_elements:
            # an attempt to catch the mime type by html tag
            mimetype = findcorresponding_mimetype(element)

            for key, value in attributes.items():
                url_check = urlparse(value)
                if value.startswith(
                    "#"
                ):  # These are usually used to point-out to id's that are on the same page (e.g http://whereismybluetoothtoilet.com#about)
                    continue

                if (
                    len(url_check.scheme) == 0
                ):  # Doesnt have a scheme, and therefore is something like /here.jpg or here.jpg etc (./blahblah.mp3)
                    """
                    Quick note, /here.jpg and here.jpg ARE NOT THE SAME
                    for example, if user is in goback.com/foo/bar/nuts.html?krijgteentien=true, and if the document wants:
                    /here.jpg -> The browser will request to goback.com/here.jpg,
                    here.jpg -> The browser will request to goback.com/foo/bar/here.jpg
                    ./here.jpg _> browser will rewrite to goback.com/foo/bar/here.jpg
                    ./../labubu.jpg -> browser will rewrite to goback.com/foo/labubu.jpg

                    just so you know ^_^
                    PS: Query parameters also get removed
                    """
                    new_url = urlparse(url)._replace(query="").geturl()
                    new_url = urljoin(new_url, value)
                    url_check = urlparse(new_url)
                try:
                    asset_response, optional_mimetype = (
                        await scraper.request_html_of_link(
                            url_check.geturl(),
                            return_mimetype=(
                                mimetype == "any"
                            ),  # A second attempt on obtaining the mime-type by fetching the asset this time
                        )
                    )
                except httpx._exceptions.HTTPStatusError as e:
                    element.attrs[key] = "/media/000000000000000000000000000000000000"
                    asset_cache.add_to_cache(
                        original_summary_of_html, "000000000000000000000000000000000000"
                    )
                    if user == None:
                        dprint(
                            f"Error when trying to fetch (this element will therefore be skipped) {url_check}\t{e}"
                        )
                    else:
                        job_task.add_status_message(
                            f"Error when trying to fetch element, this element will be skipped. The url: {url_check} replied with {e.response.status_code}",
                            StatusTypesEnum.ERROR,
                        )
                        db_session.commit()
                    continue

                if optional_mimetype is not False:
                    mimetype = optional_mimetype

                sha256_hash = hash_sha256_to_36(asset_response.content)
                if mimetype.startswith("text/html"):

                    recursed_app_id: str = await main(
                        url_check.geturl(), user, job_task, True, asset_cache
                    )
                    element.attrs[key] = f"/media/{recursed_app_id}"
                    new_asset = AssetMetadata(
                        file_id=recursed_app_id, mimetype=mimetype
                    )
                    db_session.add(new_asset)
                    db_session.commit()
                    continue

                try:
                    await session.appwrite_publish_media(
                        sha256_hash, asset_response.content
                    )
                except (
                    Exception
                ):  # Already exists, and sha256 is already unique enough, why bother deleting?
                    ...

                element.attrs[key] = f"/media/{sha256_hash}"
                new_asset = AssetMetadata(file_id=sha256_hash, mimetype=mimetype)
                db_session.add(new_asset)
                db_session.commit()

        # Publishing the main root document (the whole damn rewrited HTML document)
        site_document_indentifier = hash_sha256_to_36(str(scraper.main_html_content))

        asset_cache.add_to_cache(original_summary_of_html, site_document_indentifier)

        try:
            await session.appwrite_publish_media(
                site_document_indentifier, str(scraper.main_html_content).encode()
            )
        except Exception:
            ...

        db_session.close()

        if recursive is True:
            return site_document_indentifier

        if INTERACTIVE_MODE:
            dprint("==========HTML_CONTENT==========")
            dprint(str(scraper.main_html_content))
            dprint("================================")

            dprint(
                "file id to access with through appwrite:", site_document_indentifier
            )
            dprint(
                f"To access this page, run the webserver using uvicorn, or docker, and then go to <webserver_socket>/media/{site_document_indentifier}"
            )
        else:
            dprint(f"TASK FINISHED FROM USER {user.username}")
        await insert_site_row(
            url,
            site_document_indentifier,
            -1 if user is None else user.user_id,
        )
        return site_document_indentifier


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
