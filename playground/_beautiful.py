from bs4 import BeautifulSoup
import bs4
from bs4.element import PageElement


URL_TAGS = frozenset(("href", "src"))
with open("./_index.html", "r") as file:
    soup = BeautifulSoup(file.read(), "lxml")


def get_useful_attributes(attributes: dict[str, str]) -> dict[str, str] | None:
    keys = dict()
    for url_tag in URL_TAGS:
        if (
            corresponding_value := attributes.get(url_tag, None)
        ) is not None:  # Exists there
            # TODO: String validation
            keys[url_tag] = corresponding_value
    return keys


def traverse_through_tree(elements: list[PageElement]):
    for element in elements:
        match type(element):
            case bs4.element.Tag:
                element: bs4.element.Tag
                print("This is a tag =>", element.name)
                if useful_attrs := get_useful_attributes(
                    element.attrs
                ):  # If it isnt empty
                    print(useful_attrs)

                traverse_through_tree(element.children)
            case bs4.element.NavigableString:
                element: bs4.element.NavigableString
                if element != "\n":
                    print("This is a string =>", str(element.string))


traverse_through_tree(soup.children)
