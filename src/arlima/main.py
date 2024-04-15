from pathlib import Path

import click
import duckdb
from arlima.request_index import request_index
from arlima.request_pages import request_pages

DB = Path(__file__).parent.joinpath("arlima.db")


@click.command()
@click.option("--restart", default=False, is_flag=True, show_default=True)
def main(restart: bool):
    conn = duckdb.connect(str(DB))
    tables = [tup[0] for tup in conn.execute("show tables;").fetchall()]
    if restart or ("arlima_index" not in tables or "pages" not in tables):
        # request_index(conn=conn)
        request_pages(conn=conn)


if __name__ == "__main__":
    main()
