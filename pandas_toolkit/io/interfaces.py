# pandas_toolkit/io/interfaces.py

from abc import ABC, abstractmethod
import pandas as pd
from pandas_toolkit.io.errors import FileEncodingError
from pandas.errors import ParserError

# ----------------------------------------------------------------------
# Common encoding options to try when reading files
# ----------------------------------------------------------------------
COMMON_ENCODINGS = [
    "utf-8",          # Most common encoding, compatible with ASCII
    "utf-8-sig",      # UTF-8 with BOM (Byte Order Mark), useful for Excel compatibility
    "cp1252",         # Windows-1252, common Western European Windows encoding
    "latin1",         # ISO-8859-1 alias, also used in Western Europe
    "iso-8859-1",     # ISO Latin-1, nearly identical to cp1252
    "utf-16",         # Unicode 16-bit, with BOM (autodetects endianness)    
    "utf-16-le",      # UTF-16 little-endian without BOM
    "utf-16-be",      # UTF-16 big-endian without BOM
    "utf-32",         # Unicode 32-bit (rare but possible)
    "utf-32-le",      # UTF-32 little-endian
    "utf-32-be",      # UTF-32 big-endian
    "cp1250",         # Central European Windows encoding
    "cp1251",         # Cyrillic Windows encoding (Russian, Bulgarian, etc.)
    "cp1253",         # Greek Windows encoding
    "cp1254",         # Turkish Windows encoding
    "cp932",          # Japanese encoding (Shift JIS variant)
    "shift_jis",      # Standard Japanese Shift JIS encoding
    "euc-jp",         # Japanese EUC encoding
    "euc-kr",         # Korean EUC encoding
    "big5",           # Traditional Chinese (Taiwan, Hong Kong)
    "gb2312",         # Simplified Chinese encoding
    "mac_roman",      # Old Mac OS Western encoding
    "ascii",          # Very basic, 7-bit encoding (fails with accents or special chars)
]

# ----------------------------------------------------------------------
# Common delimiters used in delimited text files (CSV, TSV, logs, etc.)
# ----------------------------------------------------------------------
COMMON_DELIMITERS = [
    ",",    # Comma
    ";",    # Semicolon
    "\t",   # Tab
    "|",    # Pipe (vertical bar)
    ":",    # Colon
    "~",    # Tilde
    "^",    # Caret
    "#",    # Hash
    " ",    # Space
    "_",    # Underscore
    "-",    # Dash / Hyphen
    "/",    # Forward slash
    "\\",   # Backslash
    "*",    # Asterisk
    "=",    # Equal sign
    "'",    # Single quote
    "\"",   # Double quote
]

# ----------------------------------------------------------------------
# Mixin class that adds normalization methods for cleaning DataFrames
# ----------------------------------------------------------------------
class NormalizeMixin:
    def normalize(
        self,
        df: pd.DataFrame,
        *,
        drop_empty_cols: bool = True,
        drop_empty_rows: bool = True,
        trim_strings: bool = True,
        convert_case: str = "lower",  # 'lower', 'upper', or None
    ) -> pd.DataFrame:
        """
        Normalize a DataFrame:
        - Drop empty rows/columns.
        - Strip whitespace from string values.
        - Convert empty strings to None.
        - Change casing of string values (lower/upper).
        - Creates new columns with "_norm" suffix instead of overwriting.
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

# ----------------------------------------------------------------------
# Abstract base class defining the interface for all file readers
# ----------------------------------------------------------------------
class FileReader(ABC, NormalizeMixin):
    @abstractmethod
    def read(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Abstract method for reading a file into a DataFrame.
        Must be implemented by subclasses.
        """
        pass

# ----------------------------------------------------------------------
# Base class for file readers that support multiple encodings
# ----------------------------------------------------------------------
class FileReaderEncoding(FileReader):
    def __init__(self, encodings=None):
        # Set encoding list (or default to COMMON_ENCODINGS)
        self.encodings = encodings or COMMON_ENCODINGS

    @abstractmethod
    def _read_with_encoding(self, filepath: str, encoding: str, **kwargs) -> pd.DataFrame:
        """
        Abstract method to try reading a file using a specific encoding.
        Should be implemented by subclasses.
        """
        pass

    def read(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Attempts to read the file using each encoding until one works.
        """
        for enc in self.encodings:
            try:
                return self._read_with_encoding(filepath, enc, **kwargs)
            except UnicodeDecodeError:
                continue

        raise FileEncodingError(f"We can't encode {filepath} with encodings {self.encodings}")

# ----------------------------------------------------------------------
# Reader for delimited text files (.csv, .tsv, etc.) that tries different
# encodings and delimiters until it finds a successful combination.
# ----------------------------------------------------------------------
class DelimitedTextReader(FileReaderEncoding):
    def __init__(self, encodings=None, delimiters=None, verbose=False, capture_bad_lines=False):
        super().__init__(encodings)
        self.delimiters = delimiters or COMMON_DELIMITERS
        self.success_encoding = None  # Stores the encoding that worked
        self.success_delimiter = None  # Stores the delimiter that worked
        self.verbose = verbose
        self.capture_bad_lines = capture_bad_lines
        self.bad_lines = []  # List of lines that could not be parsed (optional)

    def _read_with_encoding(self, filepath: str, encoding: str, **kwargs) -> pd.DataFrame:
        """
        Tries to read the file using a specific encoding and all possible delimiters.
        Returns the DataFrame once a successful read is achieved.
        Raises FileEncodingError if all attempts fail.
        """
        def capturar_linea(bad_line):
            self.bad_lines.append(bad_line)
            if self.verbose:
                print(f"[WARNING] Bad line: {bad_line}")

        for delim in self.delimiters:
            try:
                if self.verbose:
                    print(f"[DEBUG] Try with: encoding='{encoding}', delimiter='{delim}'")

                if self.capture_bad_lines:
                    if self.verbose:
                        print(f"[DEBUG] Detecting bad lines (Execution will be longer).")

                    df = pd.read_csv(
                        filepath,
                        encoding=encoding,
                        delimiter=delim,
                        engine="python",
                        on_bad_lines=capturar_linea,
                        **kwargs
                    )
                else:
                    df = pd.read_csv(
                        filepath,
                        encoding=encoding,
                        delimiter=delim,
                        on_bad_lines="warn",
                        **kwargs
                    )

                # Basic heuristic: valid file should have more than one column
                if df.shape[1] > 1:
                    self.success_encoding = encoding
                    self.success_delimiter = delim
                    if self.verbose:
                        print(f"[INFO] Success with encoding='{encoding}', delimiter='{delim}'")
                    return df
            
            except FileNotFoundError as fnf_error:
                raise FileNotFoundError(f"[ERROR] Archivo no encontrado: {filepath}") from fnf_error

            except Exception as e:
                error_original = e
                if isinstance(e, UnicodeDecodeError):
                    raise
                elif isinstance(e, (ParserError, ValueError)):
                    if self.verbose:
                        print(f"[DEBUG] Fail with encoding='{encoding}', delimiter='{delim}'")
                    continue

        # If all attempts failed, raise a custom error
        raise Exception(f"Error: {error_original}")
