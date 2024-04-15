import csv
from concurrent.futures import ThreadPoolExecutor
import io
import duckdb
import requests
import requests.adapters
from rich.progress import (
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from typing import Generator
from arlima.fm import TMP
from arlima.page import Page
from arlima.witness import Witness, yield_witnesses
from contextlib import contextmanager


works_file_path = TMP.joinpath("works.csv")
witnesses_file_path = TMP.joinpath("witnesses.csv")


@contextmanager
def csv_contexts() -> Generator[tuple[io.TextIOWrapper, io.TextIOWrapper], None, None]:
    f1 = works_file_path.open(mode="w")
    f2 = witnesses_file_path.open(mode="w")
    try:
        yield f1, f2
    finally:
        f1.close()
        f2.close()


def setup_writers(
    f1: io.TextIOWrapper, f2: io.TextIOWrapper
) -> tuple[csv.DictWriter, csv.DictWriter]:
    works = csv.DictWriter(f1, fieldnames=Page.fields())
    manuscripts = csv.DictWriter(f2, fieldnames=Witness.fields())
    works.writeheader()
    manuscripts.writeheader()
    return works, manuscripts


ProgressBar = Progress(
    TextColumn("{task.description}"),
    SpinnerColumn(),
    MofNCompleteColumn(),
    TimeElapsedColumn(),
)


def setup_pages_table(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("DROP TABLE IF EXISTS pages;")
    conn.execute(
        "CREATE TABLE pages (link VARCHAR, form VARCHAR, genre VARCHAR, arlima_permalink VARCHAR, jonas_permalink VARCHAR, simple_title VARCHAR, canonic_title VARCHAR, language VARCHAR, date_description VARCHAR, year_earliest BIGINT, year_latest BIGINT)"
    )


def setup_witnesses_table(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("DROP TABLE IF EXISTS manuscripts;")
    conn.execute(
        "CREATE TABLE manuscripts (page VARCHAR, archive_href VARCHAR, archive VARCHAR, resource VARCHAR)"
    )


def get_unique_links(conn: duckdb.DuckDBPyConnection) -> list:
    return [
        tup[0]
        for tup in duckdb.table("arlima_index", connection=conn)
        .aggregate("link")
        .fetchall()
    ]


def request_pages(conn: duckdb.DuckDBPyConnection):
    # Set up the database for new tables
    setup_pages_table(conn)
    setup_witnesses_table(conn)
    links = get_unique_links(conn)

    with csv_contexts() as (f1, f2), ProgressBar as p, ThreadPoolExecutor() as executor:
        # Set up the CSV writers
        works, manuscripts = setup_writers(f1, f2)

        # Set up the progress bar's task
        t = p.add_task(description="requesting pages", total=len(links))

        # Set up the scraper
        scraper = Scraper()

        # Run multi-threaded requests
        for result in executor.map(scraper, links):
            # Regardless the scraping success, advance the progress bar
            p.advance(t)

            # Ignore incorrectly scraped pages
            if not result:
                continue

            # Write the page's results to the works CSV
            works.writerow(result.dict())

            # Write the page's manuscripts to the manuscripts CSV
            for mss_row in yield_witnesses(result):
                manuscripts.writerow(mss_row)

    # Insert into the new tables the scraping results
    conn.execute("INSERT INTO pages SELECT * FROM '{}'".format(works_file_path))
    conn.execute("INSERT INTO witnesses SELECT * FROM '{}'".format(witnesses_file_path))


class Scraper:
    def __init__(self) -> None:
        session = requests.Session()
        session.mount(
            "https://",
            requests.adapters.HTTPAdapter(
                max_retries=requests.adapters.Retry(total=5, status_forcelist=[500])
            ),
        )
        self.session = session

    def __call__(self, link: str) -> Page | None:
        try:
            response = self.session.get(link)
            page = Page(content=response.content, link=link)
            if page._soup:
                return page
        except Exception as e:
            print("Failed to parse URL: ", link)
