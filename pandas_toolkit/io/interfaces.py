# pandas_toolkit/io/interfaces.py
from abc import ABC, abstractmethod
import pandas as pd
from pandas_toolkit.io.errors import FileEncodingError
from pandas.errors import ParserError



COMMON_ENCODINGS = [    
    "utf-8",
    "utf-8-sig",    
    "cp1252",
    "latin1",
    "iso-8859-1",
    "utf-16"
]

COMMON_DELIMITERS =[",",
                    ";",
                    "|",
                    "\t"]

class NormalizeMixin:
    def normalize(
        self,
        df: pd.DataFrame,
        *, # all arguments be named
        drop_empty_cols: bool = True,
        drop_empty_rows: bool = True,
        trim_strings: bool = True,
        convert_case: str = "lower",  # 'lower', 'upper', o None
    ) -> pd.DataFrame:

        """
        Normalize a DataFrame:
        - Drop columns and rows that are completely empty (if drop_empty_cols).
        - Trim whitespace from string values (if trim_strings).
        - Transform "" (empty strings) to None.
        - Convert string values to lowercase or uppercase (according to convert_case).

        :return: Normalized DataFrame.
        """
        df = df.copy()

        
        if drop_empty_cols:
            df = df.dropna(axis=1, how="all")

        if drop_empty_rows:
            df = df.dropna(axis=0, how="all")
        
        def normalize_str(val: str):
            if not isinstance(val, str):
                return val
            val = val.strip() if trim_strings else val
            if val == "":
                return None 
            if convert_case == "lower":
                val = val.lower()
            elif convert_case == "upper":
                val = val.upper()
            return val

        str_cols = df.select_dtypes(include=["object", "string"]).columns

        for col in str_cols:
            df[col] = df[col].apply(normalize_str)

        return df

class FileReader(ABC,NormalizeMixin):
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



class DelimitedTextReader(FileReaderEncoding):
    def __init__(self, encodings=None, delimiters=None):
        super().__init__(encodings)
        self.delimiters = delimiters  or COMMON_DELIMITERS

    def _read_with_encoding(self, filepath: str, encoding: str, **kwargs) -> pd.DataFrame:

        # def capturar_linea(bad_line):  
        #     # errores = []          
        #     errores.append(bad_line)
        #     print(f"[WARN] Línea defectuosa: {bad_line}")
        #     raise ValueError("Línea defectuosa descartada")

        for delim in self.delimiters:
            try:
                # print(f"[INFO] Probando encoding={encoding}, delimiter='{delim}'")
                df = pd.read_csv(filepath, 
                                 encoding=encoding, 
                                 delimiter=delim, 
                                #  on_bad_lines=capturar_linea,
                                 **kwargs)
                if df.shape[1] > 1:
                    return df
            except Exception as e:
                if isinstance(e, UnicodeDecodeError):
                    raise
                elif isinstance(e, (ParserError, ValueError)):
                    continue
                # try:
        raise FileEncodingError(
            f"We can't encode {filepath} with encodings {self.encodings} in _read_with_encoding"
        )
        # except FileEncodingError as e:
        #     print("Capturado error:", e)
