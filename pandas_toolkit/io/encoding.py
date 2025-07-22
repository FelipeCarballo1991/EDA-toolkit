# pandas_toolkit/io/encoding.py
import pandas as pd

COMMON_ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "latin1",
    "cp1252",
    "iso-8859-1",
    "utf-16"
]

class EncodingGuesser:
    def __init__(self, encodings=None):
        self.encodings = encodings or COMMON_ENCODINGS

    def read_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        for enc in self.encodings:
            try:
                return pd.read_csv(filepath, encoding=enc, **kwargs)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"No se pudo decodificar el archivo con los encodings: {self.encodings}")
