from pathlib import Path

TMP = Path(__file__).parent.joinpath("tmp")
TMP.mkdir(exist_ok=True)


DB = Path(__file__).parent.joinpath("arlima.db")


def clean():
    for file in TMP.iterdir():
        file.unlink()
    TMP.rmdir()
