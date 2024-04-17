import re
from dataclasses import dataclass, field
from typing import Generator

import bs4

from arlima.page import Page

example = """
<li>
    <a href="https://www.bl.uk">London, British Library</a>
    , Royal, 20. D. XI, f. 77rc-79ra
    <a href="/mss/united_kingdom/london/british_library/royal/20_D_XI.html#F77">[⇛ Description]</a>
</li>
"""


@dataclass
class Witness:
    li: bs4.element.Tag
    page: str
    fields: list = field(default_factory=list)

    def __dict__(self) -> dict:
        return {field: self.__getattribute__(field) for field in self.fields()}

    @classmethod
    def fields(cls) -> list:
        return [
            "page",
            "archive_href",
            "settlement",
            "repository",
            "collection",
            "idno",
        ]

    @property
    def archive_href(self) -> str:
        """_summary_

        Examples:
        >>> li = bs4.BeautifulSoup(example, features="lxml")
        >>> witness = Witness(li=li, page="www.arlima.com/no/test")
        >>> witness.archive_href
        'https://www.bl.uk'

        Returns:
            str: _description_
        """

        return self.li.find("a").get("href")

    @property
    def settlement(self) -> str | None:
        """_summary_

        Examples:
        >>> li = bs4.BeautifulSoup(example, features="lxml")
        >>> witness = Witness(li=li, page="www.arlima.com/no/test")
        >>> witness.settlement
        'London'

        Returns:
            str | None: _description_
        """

        return self.get_settlement(self.a_link_text())

    @property
    def repository(self) -> str:
        """_summary_

        Examples:
        >>> li = bs4.BeautifulSoup(example, features="lxml")
        >>> witness = Witness(li=li, page="www.arlima.com/no/test")
        >>> witness.repository
        'British Library'

        Returns:
            str: _description_
        """

        return self.get_repository(self.a_link_text())

    @property
    def collection(self) -> str | None:
        """_summary_

        Examples:
        >>> li = bs4.BeautifulSoup(example, features="lxml")
        >>> witness = Witness(li=li, page="www.arlima.com/no/test")
        >>> witness.collection
        'Royal'

        Returns:
            str | None: _description_
        """

        return self.get_collection(self.li_text_without_a_text())

    @property
    def idno(self) -> str:
        """_summary_

        Examples:
        >>> li = bs4.BeautifulSoup(example, features="lxml")
        >>> witness = Witness(li=li, page="www.arlima.com/no/test")
        >>> witness.idno
        '20. D. XI, f. 77rc-79ra'

        Returns:
            str: _description_
        """

        return self.get_idno(self.li_text_without_a_text())

    def a_link_text(self) -> str:
        return self.li.find("a").text

    def li_text_without_a_text(self) -> str:
        # Remove the <a> element text from the rest of <li>
        full_li_element_text = self.li.text.strip()
        text_inside_embedded_a_element = self.a_link_text()
        text = full_li_element_text.split(text_inside_embedded_a_element)[-1]
        # Remove the comma that immediately follows the <a> text
        parts = text.split(",")
        parts.pop(0)
        text = ",".join(parts)
        # Remove the second <a> link in the text
        text = text.replace("[⇛ Description]", "")
        text = text.replace("  ", " ")
        # Remove any trailing white space
        return text.strip()

    @classmethod
    def get_settlement(cls, a_link_text: str) -> str | None:
        """Extractthe location (settlement) before a comma.

        Examples:
        >>> Witness.get_settlement("Lincoln, Cathedral Library")
        'Lincoln'
        >>> Witness.get_settlement("EA2218")
        >>> Witness.get_settlement("Liège, Bibliothèque du Grand Séminaire")
        'Liège'

        Args:
            repo_text (str): _description_

        Returns:
            str | None: _description_
        """

        rep_parts = a_link_text.split(",")
        if len(rep_parts) > 1:
            return rep_parts[0]

    @classmethod
    def get_repository(cls, a_link_text: str) -> str:
        """Extract the repository or, in the case of no settlement, the sole identifier.

        Examples:
        >>> Witness.get_repository("Lincoln, Cathedral Library")
        'Cathedral Library'
        >>> Witness.get_repository("EA2218")
        'EA2218'
        >>> Witness.get_repository("Liège, Bibliothèque du Grand Séminaire")
        'Bibliothèque du Grand Séminaire'
        >>> Witness.get_repository("Heiligenkreuz, Stiftsbibliothek, etc.")
        'Stiftsbibliothek, etc.'

        Args:
            a_link_text (str): _description_

        Returns:
            str: _description_
        """

        rep_parts = a_link_text.split(",")
        if len(rep_parts) > 1:
            rep_parts.pop(0)
            return ",".join(rep_parts).strip()
        else:
            return a_link_text.strip()

    @classmethod
    def get_collection(cls, li_text_without_a_text: str) -> str | None:
        """When the resource's description is prefaced by a word and comma,
        extract the collection name.

        Examples:
        >>> Witness.get_collection("Codices latini monacenses, 17139 (Q)")
        'Codices latini monacenses'
        >>> Witness.get_collection("A. I. 32, f. 163r, 2/2 XV")
        >>> Witness.get_collection("Santa Cruz de Coimbra, 69, f. 268v-273v (Q)")
        'Santa Cruz de Coimbra'
        >>> Witness.get_collection("9176-9177, f, 1r-24v, XV, XIV")

        Args:
            li_text_without_a_text (str): _description_

        Returns:
            str | None: _description_
        """

        resource_parts = li_text_without_a_text.split(",")
        if len(resource_parts) > 1 and re.match(
            r"^[^\d\W]{3,}", li_text_without_a_text
        ):
            return resource_parts[0].strip()

    @classmethod
    def get_idno(cls, li_text_without_a_text: str) -> str:
        """_summary_

        Examples:
        >>> Witness.get_idno("Codices latini monacenses, 17139 (Q)")
        '17139 (Q)'
        >>> Witness.get_idno("A. I. 32, f. 163r, 2/2 XV")
        'A. I. 32, f. 163r, 2/2 XV'
        >>> Witness.get_idno("Santa Cruz de Coimbra, 69, f. 268v-273v (Q)")
        '69, f. 268v-273v (Q)'
        >>> Witness.get_idno("9176-9177, f, 1r-24v, XV, XIV")
        '9176-9177, f, 1r-24v, XV, XIV'

        Args:
            li_text_without_a_text (str): _description_

        Returns:
            str: _description_
        """

        resource_parts = li_text_without_a_text.split(",")
        if len(resource_parts) > 1 and re.match(
            r"^[^\d\W]{3,}", li_text_without_a_text
        ):
            resource_parts.pop(0)
            return ",".join(resource_parts).strip()
        else:
            return li_text_without_a_text.strip()


def yield_witnesses(page: Page) -> Generator[dict, None, None]:
    if page.mss:
        for li in page.mss.find_all("li"):
            if li.find("a"):
                wit = Witness(li=li, page=page.link)
                yield wit.__dict__()
