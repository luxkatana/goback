from bs4.element import PageElement
from bs4 import BeautifulSoup
from appwrite_session import AppwriteSession, create_file_identifier
from urllib.parse import urlparse
from dotenv import load_dotenv
import asyncio, bs4, httpx, re, os

load_dotenv()
URL_TAGS = frozenset(("href", "src"))
APPWRITE_KEY = os.getenv("APPWRITE_KEY")
HOST_WEBSERVER_URL = "http://localhost:8000"


class GobackScraper:
    def __init__(self, url: str):
        self.url = url
        self.httpx_client: httpx.AsyncClient = httpx.AsyncClient(
            follow_redirects=True
        )  # TODO: Implement ContextManagers so that http_client also gets closed
        # Perhaps find a way to make __init__ also async so that we can call automatically self.load_html?

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
    async def walk_through(
        self, elements: list[PageElement]
    ) -> list[PageElement] | None:
        useful_elements = []
        for element in elements:
            match type(element):

                case bs4.element.Tag:
                    element: bs4.element.Tag
                    print("This is a tag =>", element.name)
                    if useful_attrs := self.get_useful_attributes(
                        element.attrs
                    ):  # If it isnt empty
                        useful_elements.append(element)

                    useful_elements.extend(await self.walk_through(element.children))

                case bs4.element.NavigableString:
                    if element != "\n":
                        print("This is a string =>", str(element.string))
        return useful_elements

    async def request_html_of_link(self, url: str) -> httpx.Response:
        response = await self.httpx_client.get(url)
        return response.raise_for_status()


async def main(url: str) -> None:
    scraper = GobackScraper(url)
    await scraper.load_html()
    useful_element = await scraper.walk_through_native()
    if len(useful_element) == 0:
        print("Nothing to save")
        exit(0)

    regex_valid_urls = re.compile(
        r"^(?:\/[\w\-./%~]+|(?:\.\.\/|\./)?[\w\-./%~]+|\?[^\s]+)$"
    )
    session = AppwriteSession()
    for attributes, element in useful_element:
        for key, value in attributes.items():
            if re.fullmatch(regex_valid_urls, value) is not None:
                if value.startswith("/"):  # Path
                    url_obj = urlparse(url)._replace(query=None, path=value)
                    element_response = await scraper.request_html_of_link(
                        url_obj.geturl()
                    )
                    unique_identifier = create_file_identifier(
                        element_response.text, url_obj.hostname
                    )
                    savedfile = await session.appwrite_publish_media(
                        unique_identifier, element_response.text
                    )
                    element.attrs[key] = (
                        f"{HOST_WEBSERVER_URL}/media/{savedfile.appwrite_file_id}"
                    )


if (
    __name__ == "__main__"
):  # Directly ran using the python3 interpreter, prevents accidental runs for example as importing this module
    url = input("Enter url to retrieve (live mode or something): ")
    url = (
        "https://cooletaseen.hondsrugcollege.com/basic_document.html"
        if url == ""
        else url
    )  # Test url
    asyncio.run(main(url))
