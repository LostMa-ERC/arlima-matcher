from dataclasses import dataclass
from typing import Generator

import bs4

from arlima.page import Page


@dataclass
class Witness:
    li: bs4.element.Tag
    page: str

    def dict(self) -> dict:
        return {field: self.__getattribute__(field) for field in self.fields()}

    @classmethod
    def fields(cls):
        return ["page", "archive_href", "archive", "resource"]

    @property
    def archive_href(self) -> str:
        return self.li.find("a").get("href")

    @property
    def archive(self) -> str:
        return self.li.find("a").text

    @property
    def resource(self) -> str:
        text = self.li.text.split(self.archive)[-1]
        text = text.removeprefix(", ")
        text = text.removesuffix("[⇛ Description]")
        return text.strip()


def yield_witnesses(page: Page) -> Generator[dict, None, None]:
    if page.mss:
        for li in page.mss.find_all("li"):
            if li.find("a"):
                wit = Witness(li=li, page=page.link)
                yield wit.dict()
