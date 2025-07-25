# pandas_toolkit/io/readers.py
from pandas_toolkit.io.interfaces import DelimitedTextReader
import pandas as pd

# class CSVReader(FileReaderEncoding):
#     def _read_with_encoding(self, filepath: str, encoding: str, **kwargs):
#         return pd.read_csv(filepath, encoding=encoding, **kwargs)

class CSVReader(DelimitedTextReader):
    def __init__(self, encodings=None, delimiters=None, verbose=False):
        super().__init__(
            encodings=encodings,
            delimiters=delimiters,
            verbose=verbose
        )

    def read_and_normalize(self, filepath, **kwargs):
        df = self.read(filepath, **kwargs)
        return self.normalize(df)
