import unittest
from pprint import pprint

from requests import Session, adapters, request

from arlima.page import Page
from arlima.request_pages import Scraper
from arlima.witness import Witness


class ScrapingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.scraper = Scraper()

    def test_arlima_permalink(self):
        link = "https://www.arlima.net/ad/abuze_en_court.html"
        page = self.scraper(link=link)

    def test_witness_scraping(self):
        link = "https://www.arlima.net/eh/femmes_qui_demandent_les_arrerages_farce_des.html"
        page = self.scraper(link=link)
        # Problem: This page's "éditions anciennes" are being mistaken for manuscripts
        # and due to the miscategorization, the parsing of information is faulty.
        for li in page.mss.find_all("li"):
            if li.find("a"):
                print("")
                print(li)
                pprint(Witness(li=li, page="").__dict__())


if __name__ == "__main__":
    unittest.main()
