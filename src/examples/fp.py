from pathlib import Path


EXAMPLES = Path(__file__).parent


ARLIMA_MORT_ARTU_FILE = EXAMPLES.joinpath("arlima.html")
with open(ARLIMA_MORT_ARTU_FILE) as f:
    ARLIMA_MORT_ARTU = f.read()


STEMMA_BEDIER_TRISTAN_FILE = EXAMPLES.joinpath("Bedier_1902_Tristan.tei.xml")
with open(STEMMA_BEDIER_TRISTAN_FILE) as f:
    STEMMA_BEDIER_TRISTAN = f.read()
