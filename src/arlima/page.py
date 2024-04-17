import logging
from dataclasses import dataclass

import bs4
from bs4 import BeautifulSoup

from arlima.date_parser import DateParser
from arlima.exceptions import *
from arlima.fm import TMP

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=TMP.joinpath("page_errors.log"),
    filemode="w",
    encoding="utf-8",
    level=logging.CRITICAL,
    format="%(asctime)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


@dataclass
class Page:
    link: str
    content: bytes | str
    parser: DateParser = DateParser()

    def __post_init__(self) -> None:
        soup = BeautifulSoup(self.content, features="lxml")
        self._soup = None
        if self.is_text(soup):
            self._soup = soup
        self.link = self.link

        if self._soup:
            # Permalinks
            perma_div = self._soup.find("div", attrs={"id": "permalien"})
            self.permalinks = []
            if perma_div:
                for a in perma_div.find_all("a"):
                    self.permalinks.append(a.get("href"))

            # Bibliography
            self.biblio_table = self.find_bib_table(soup)
            if not self.biblio_table:
                logging.critical(BiblioException(link=self.link))

            # Manuscripts
            self.mss = self.find_mss_list(soup)

            # Date description
            self.date_description = self.get_biblio_row("date")
            if not self.date_description:
                logging.critical(DateException(link=self.link))

    @classmethod
    def find_mss_list(cls, soup: bs4.element.Tag) -> bs4.element.Tag | None:
        mss_span = soup.find("span", attrs={"id": "mss"}, string="Manuscrits")
        if mss_span:
            return mss_span.parent.find_next("ol")
        mss_list = soup.find("b", string="Manuscrits")
        if mss_list:
            return mss_list.parent.find_next("ol")

    @classmethod
    def is_text(cls, soup: bs4.element.Tag) -> bool:
        # Author
        if soup.find("h3") and soup.find("h3").find("a", attrs={"id": "bio"}):
            return False
        elif soup.find("a", attrs={"id": "oeu"}):
            return False
        # Feast day / Saint
        elif soup.find("div", attrs={"id": "fete"}):
            return False
        # Concept
        elif soup.find("a", attrs={"id": "aut"}):
            return False
        # Work (currently not supported)
        elif not cls.find_bib_table(soup) and (
            soup.find("h3", string="Versions")
            or soup.find("div", attrs={"id": "versions"})
            or soup.find("a", string="Version A")
            or soup.find("b", string="Généralités")
        ):
            return False
        else:
            return True

    @classmethod
    def find_bib_table(cls, soup: bs4.element.Tag) -> bs4.element.Tag | None:
        bib_div = soup.find("div", attrs={"class": "bib"})
        if bib_div:
            table = cls.simple_biblio_pos(bib_div)
        else:
            table = cls.simple_biblio_pos(soup)
        return table

    @classmethod
    def simple_biblio_pos(cls, soup: bs4.element.Tag) -> bs4.element.Tag | None:
        table = soup.find("table", attrs={"class": "desc"})
        return table

    def get_biblio_row(self, content_class) -> str | None:
        if self.biblio_table:
            elem = self.biblio_table.find(
                "td", attrs={"class": f"cont {content_class}"}
            )
            if elem:
                return elem.text
            else:
                logging.critical(
                    BiblioContentException(link=self.link, entry=content_class)
                )

    def dict(self) -> dict | None:
        if self._soup:
            return {field: self.__getattribute__(field) for field in self.fields()}

    @classmethod
    def fields(cls) -> list:
        return [
            "link",
            "form",
            "genre",
            "arlima_permalink",
            "jonas_permalink",
            "simple_title",
            "canonic_title",
            "language",
            "date_description",
            "date_earliest",
            "date_latest",
        ]

    @property
    def genre(self) -> str:
        return self.get_biblio_row("genre")

    @property
    def form(self) -> str:
        return self.get_biblio_row("forme")

    @property
    def arlima_permalink(self) -> str | None:
        for href in self.permalinks:
            if href.startswith("https://arlima.net/"):
                return href

    @property
    def jonas_permalink(self) -> str | None:
        for href in self.permalinks:
            if href.startswith("https://jonas.irht.cnrs.fr/"):
                return href

    @property
    def simple_title(self) -> str:
        h2 = self._soup.find("h2")
        if h2:
            return h2.text
        else:
            logging.critical(SimpleTitleException(link=self.link))

    @property
    def canonic_title(self) -> str:
        return self.get_biblio_row("titre")

    @property
    def language(self) -> str:
        return self.get_biblio_row("langue")

    @property
    def date_earliest(self) -> str:
        if self.date_description:
            date_range = self.parser(self.date_description)
            if len(date_range) > 0:
                return date_range[0]
            else:
                logging.critical(
                    DateParsingException(link=self.link, entry=self.date_description)
                )

    @property
    def date_latest(self) -> str:
        if self.date_description:
            date_range = self.parser(self.date_description)
            if len(date_range) > 1:
                return date_range[-1]
