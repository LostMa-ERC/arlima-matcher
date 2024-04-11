import unittest

from openstemmata.tei_parser import TEIParser
from tests import STEMMATA


class Models(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def all_stemmata(self):
        for lang in STEMMATA.iterdir():
            for project in lang.iterdir():
                for doc in project.iterdir():
                    yield doc

    def test_stemma_tei(self):
        for doc in self.all_stemmata():
            if ".tei" in doc.suffixes:
                tei = TEIParser(doc)

                # Test witnesses
                if tei.witnesses:
                    self.assertGreater(len(tei.witnesses), 0)

                # Test creation
                self.assertIsNotNone(tei.creation)

                # Test keywords
                self.assertGreater(len(tei.keywords), 0)

                # Test language
                self.assertIsNotNone(tei.lang)

    def test_date(self):
        for doc in self.all_stemmata():
            if ".tei" in doc.suffixes:
                tei = TEIParser(doc)
                date = tei.creation.origDate
                if date:
                    self.assertLessEqual(len(date), 2)


if __name__ == "__main__":
    unittest.main()
