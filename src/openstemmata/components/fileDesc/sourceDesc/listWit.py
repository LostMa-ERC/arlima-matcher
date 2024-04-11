from dataclasses import dataclass
import bs4
from collections import namedtuple


POINTER = namedtuple("POINTER", field_names=["type", "target"])
LABEL = namedtuple("LABEL", field_names=["type", "text"])


@dataclass
class Witness:
    label: LABEL
    idno: str
    origDate: str
    origPlace: str
    note: str
    ptr: list[POINTER]

    @classmethod
    def validate(cls, wit: bs4.element.Tag):
        pointers = []
        for ptr in wit.find_all("ptr"):
            pointers.append(POINTER(type=ptr.get("type"), target=ptr.get("target")))
        return Witness(
            label=LABEL(type=wit.label.get("type"), text=wit.label.text.strip()),
            idno=wit.idno.text.strip(),
            origDate=wit.origDate.text.strip(),
            origPlace=wit.origPlace.text.strip(),
            note=wit.note.text.strip(),
            ptr=pointers,
        )


@dataclass
class ListWit:
    witnesses: list

    @classmethod
    def validate(cls, sourceDesc: bs4.element.Tag) -> list[Witness] | None:
        if sourceDesc.find("listWit"):
            witnesses = []
            for wit in sourceDesc.find("listWit").find_all("witness"):
                witnesses.append(Witness.validate(wit))
        else:
            witnesses = None
        return witnesses
