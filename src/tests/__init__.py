from pathlib import Path


TESTS_DIR = Path(__file__).parent
SRC_DIR = TESTS_DIR.parent


STEMMATA = SRC_DIR.parent.joinpath("data").joinpath("openstemmata-data")
