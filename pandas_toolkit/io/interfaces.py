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
            *,
            drop_empty_cols: bool = True,
            drop_empty_rows: bool = True,
            trim_strings: bool = True,
            convert_case: str = "lower",  # 'lower', 'upper', o None
            # keep_original: bool = False,  # <--- NUEVO
        ) -> pd.DataFrame:
            """
            Normalize a DataFrame:
            - Drop columns and rows that are completely empty (if drop_empty_*).
            - Trim whitespace from string values (if trim_strings).
            - Transform "" (empty strings) to None.
            - Convert string values to lowercase or uppercase (according to convert_case).
            - If keep_original is True, creates new columns with '_norm' suffix instead of overwriting.

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
                normalized = df[col].apply(normalize_str)
                if f"{col}_norm" not in df.columns:
                    df[f"{col}_norm"] = normalized
                else:
                    continue
            

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
    def __init__(self, encodings=None, delimiters=None, verbose = False, capture_bad_lines = False):
        super().__init__(encodings)
        self.delimiters = delimiters  or COMMON_DELIMITERS
        self.success_encoding = None
        self.success_delimiter = None
        self.verbose = verbose
        self.capture_bad_lines = capture_bad_lines
        self.bad_lines = [] 

    def _read_with_encoding(self, filepath: str, encoding: str, **kwargs) -> pd.DataFrame:

        def capturar_linea(bad_line):
            self.bad_lines.append(bad_line)
            if self.verbose:
                print(f"[WARNING] Bad line: {bad_line}")

        for delim in self.delimiters:
            try:
                if self.verbose:
                    print(f"[🔍] Intentando: encoding='{encoding}', delimiter='{delim}'")
                
                if self.capture_bad_lines:                   
                    df = pd.read_csv(filepath, 
                                    encoding=encoding, 
                                    delimiter=delim,
                                     engine = "python", 
                                    on_bad_lines=capturar_linea,
                                    **kwargs)
                else:
                    if self.verbose:
                        print(f"[🔍] Detectando lineas erroneas (La ejecución puede durar más tiempo).")
                    df = pd.read_csv(filepath, 
                                    encoding=encoding, 
                                    delimiter=delim,
                                    # engine = "python", 
                                    on_bad_lines="warn",
                                    **kwargs)
                    
                if df.shape[1] > 1:
                    self.success_encoding = encoding
                    self.success_delimiter = delim
                    if self.verbose:
                        print(f"[✅] Lectura exitosa con encoding='{encoding}', delimiter='{delim}'")
                    return df
            except Exception as e:
                error_original = e
                if isinstance(e, UnicodeDecodeError):
                    raise
                elif isinstance(e, (ParserError, ValueError)):
                    if self.verbose:
                        print(f"[⚠️] Falló con encoding='{encoding}', delimiter='{delim}'")
                    continue
                # try:
        raise FileEncodingError(            
            f"Detalle Error: {error_original}"
        )
        # except FileEncodingError as e:
        #     print("Capturado error:", e)
