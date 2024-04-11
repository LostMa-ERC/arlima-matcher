import bs4
from dataclasses import dataclass
from collections import namedtuple


Term = namedtuple("Term", field_names=["type", "text"])


@dataclass
class textClass:
    keywords: list

    @classmethod
    def validate(cls, profileDesc: bs4.element.Tag) -> list:
        keywords = []
        textClass = profileDesc.find("textClass")
        for term in textClass.find_all("keywords"):
            keywords.append(Term(type=term.get("type"), text=term.text))
        return keywords
