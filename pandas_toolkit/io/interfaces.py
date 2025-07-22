# pandas_toolkit/io/interfaces.py
from abc import ABC, abstractmethod
import pandas as pd

class FileReader(ABC):
    @abstractmethod
    def read(self, filepath: str, **kwargs) -> pd.DataFrame:
        pass
