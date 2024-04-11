from pathlib import Path

from openstemmata.utils import parse_xml
from openstemmata.components.fileDesc import ListWit
from openstemmata.components.profileDesc import Creation, textClass, langUsage


class TEIParser:
    def __init__(self, fp: str | Path | bytes) -> None:
        self.soup = parse_xml(input=fp)

        # File / Source Description
        source_desc = self.soup.find("sourceDesc")
        self.witnesses = ListWit.validate(sourceDesc=source_desc)

        # Profile Description
        profile_desc = self.soup.find("profileDesc")
        self.creation = Creation.validate(profileDesc=profile_desc)
        self.keywords = textClass.validate(profileDesc=profile_desc)
        self.lang = langUsage.validate(profileDesc=profile_desc)
