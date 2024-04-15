class BiblioException(Exception):
    def __init__(self, link: str) -> None:
        message = f"Find bib table\t{link}\tNo bib table"
        super().__init__(message)


class BiblioContentException(Exception):
    def __init__(self, link: str, entry: str) -> None:
        message = f"Bib table row\t{link}\t{entry}"
        super().__init__(message)


class DateException(Exception):
    def __init__(self, link: str) -> None:
        message = f"Date description\t{link}\tNo date description"
        super().__init__(message)


class DateParsingException(Exception):
    def __init__(self, link: str, entry: str) -> None:
        message = f"Date parsing\t{link}\t{entry}"
        super().__init__(message)


class SimpleTitleException(Exception):
    def __init__(self, link: str) -> None:
        message = f"Simple title\t{link}\tNothing in <h2>"
        super().__init__(message)
