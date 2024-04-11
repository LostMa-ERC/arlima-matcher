from pathlib import Path

from openstemmata.utils import parse_xml
from openstemmata.components.fileDesc import ListWit


class TEIParser:
    def __init__(self, fp: str | Path | bytes) -> None:
        self.soup = parse_xml(input=fp)

        # Source Description
        source_desc = self.soup.find("sourceDesc")
        self.witnesses = ListWit.validate(sourceDesc=source_desc)
