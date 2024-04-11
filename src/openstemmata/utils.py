from pathlib import Path
from bs4 import BeautifulSoup
from io import TextIOWrapper
from datetime import datetime


def parse_xml(input: str | TextIOWrapper | Path):
    # Parse opened file
    if isinstance(input, TextIOWrapper):
        return BeautifulSoup(input, features="xml")
    # Parse closed file
    elif isinstance(input, Path):
        with open(input) as f:
            return BeautifulSoup(f, features="xml")
    # Try to read string input
    elif isinstance(input, str):
        # Try to read the input as a file
        try:
            with open(input) as f:
                return BeautifulSoup(f, features="xml")
        # If the string is not a file,
        except Exception:
            if isinstance(input, str):
                return BeautifulSoup(input, features="xml")
    else:
        raise TypeError(type(input))
