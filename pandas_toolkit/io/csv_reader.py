# pandas_toolkit/io/readers.py
from pandas_toolkit.io.interfaces import FileReader
from pandas_toolkit.io.encoding import EncodingGuesser
import pandas as pd

class CSVReader(FileReader):
    def __init__(self, encoding_guesser=None):
        self.encoding_guesser = encoding_guesser or EncodingGuesser()

    def read(self, filepath: str, **kwargs) -> pd.DataFrame:
        return self.encoding_guesser.read_csv(filepath, **kwargs)
