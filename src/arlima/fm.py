from pathlib import Path

TMP = Path(__file__).parent.joinpath("tmp")
TMP.mkdir(exist_ok=True)


def clean():
    for file in TMP.iterdir():
        file.unlink()
    TMP.rmdir()
