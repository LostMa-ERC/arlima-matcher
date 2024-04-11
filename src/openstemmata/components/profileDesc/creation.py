import bs4
from dataclasses import dataclass


@dataclass
class Creation:
    title: str
    title_ref: str
    author_name: str
    author_ref: str
    origDate: list
    origPlace: str

    @staticmethod
    def parse_date(origDate: bs4.element.Tag) -> list | None:
        if origDate.text:
            dates = []
            for d in origDate.text.split("-"):
                d = d.strip()
                try:
                    d = int(d)
                except ValueError:
                    pass
                dates.append(d)
            return dates

    @classmethod
    def validate(cls, profileDesc: bs4.element.Tag) -> "Creation":
        c = profileDesc.find("creation")
        author_name = None
        author_ref = None
        if c.find("persName") and c.persName.get("role") == "author":
            author_name = c.persName.text
            author_ref = c.persName.get("ref")
        return Creation(
            title=c.title.text.strip(),
            title_ref=c.title.get("ref"),
            author_name=author_name,
            author_ref=author_ref,
            origDate=cls.parse_date(c.origDate),
            origPlace=c.origPlace.text,
        )
