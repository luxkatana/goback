import httpx
from bs4 import BeautifulSoup
import asyncio


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
        html_content = response.content.decode()
        self.main_html_content = BeautifulSoup(html_content, "lxml")

    async def walk_through(self) -> None:
        pass


async def main(url: str) -> None:
    scraper = GobackScraper(url)
    await scraper.load_html()
    print(scraper.main_html_content)


if __name__ == "__main__":  # Directly ran using the python3 interpreter
    url = input("Enter url to retrieve (live mode or something): ")
    url = "https://guthib.com" if url == "" else url
    asyncio.run(main(url))
