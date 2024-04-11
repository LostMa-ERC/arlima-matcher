import bs4
from dataclasses import dataclass


@dataclass
class langUsage:
    language: str

    @classmethod
    def validate(cls, profileDesc: bs4.element.Tag) -> str:
        language = profileDesc.find("langUsage").find("language")
        return language.get("ident")
