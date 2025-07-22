# pandas_toolkit/io/readers.py
from pandas_toolkit.io.interfaces import FileReaderEncoding
import pandas as pd

class CSVReader(FileReaderEncoding):
    def _read_with_encoding(self, filepath: str, encoding: str, **kwargs):
        return pd.read_csv(filepath, encoding=encoding, **kwargs)

