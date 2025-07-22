# pandas_toolkit/io/interfaces.py
from abc import ABC, abstractmethod
import pandas as pd
from pandas_toolkit.io.errors import FileEncodingError

COMMON_ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "latin1",
    "cp1252",
    "iso-8859-1",
    "utf-16"
]

class FileReader(ABC):
    @abstractmethod
    def read(self, filepath: str, **kwargs) -> pd.DataFrame:
        pass




class FileReaderEncoding(FileReader):   

    def __init__(self, encodings=None):
        self.encodings = encodings or COMMON_ENCODINGS

    @abstractmethod
    def _read_with_encoding(self, filepath: str, encoding: str, **kwargs) -> pd.DataFrame:
        """Try read with encoding"""
        pass

    def read(self, filepath: str, **kwargs) -> pd.DataFrame:
        for enc in self.encodings:
            try:
                return self._read_with_encoding(filepath, enc, **kwargs) # for example read_csv  == _read_with_encoding (from csv_reader) 
            except UnicodeDecodeError:
                continue
        raise FileEncodingError(f"We can't encode {filepath} with encodings {self.encodings}")
