import csv
from string import ascii_lowercase

import duckdb
import requests
from bs4 import BeautifulSoup
from rich.progress import track

from arlima.fm import TMP


def request_index(conn: duckdb.DuckDBPyConnection):
    API = "https://www.arlima.net/{}.html"

    conn.execute("DROP TABLE IF EXISTS arlima_index;")
    conn.execute("CREATE TABLE arlima_index (title VARCHAR, link VARCHAR);")

    for letter in track(ascii_lowercase, total=len(ascii_lowercase)):
        temp_file = TMP.joinpath("index_{}.csv".format(letter))
        api = API.format(letter)
        response = requests.get(api)
        soup = BeautifulSoup(response.content, features="lxml")
        header = soup.find("h3", string=letter.capitalize())
        with open(temp_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["title", "link"])
            for i in header.parent.find_all("a"):
                title = i.text.strip()
                href = i.get("href")
                link = "https://www.arlima.net" + href
                writer.writerow([title, link])
        conn.execute("INSERT INTO arlima_index SELECT * FROM '{}'".format(temp_file))
        temp_file.unlink()
