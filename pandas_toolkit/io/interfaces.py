# pandas_toolkit/io/interfaces.py

from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path
import re
import unicodedata
from collections import defaultdict

from pandas_toolkit.io.errors import FileEncodingError
from pandas_toolkit.io.exporter import FileExporter
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
    ",",      # Comma (most common)
    ";",      # Semicolon (common in European CSVs)
    "\t",     # Tab (TSV files)
    "|",      # Pipe
    ":",      # Colon
    "~",      # Tilde
    "^",      # Caret
    "#",      # Hash
    " ",      # Space
    "_",      # Underscore
    "-",      # Hyphen
    "/",      # Forward slash
    "\\",     # Backslash
    "*",      # Asterisk
    "=",      # Equals
    "'",      # Single quote
    "\"",     # Double quote
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

    def normalize_columns(
            self,
            df: pd.DataFrame,
            convert_case: str = "lower",
            empty_col_name: str = "unnamed",
        ) -> pd.DataFrame:
        """
        Normalize DataFrame column names by applying standardization transformations.
        
        This method cleans and standardizes all column names in a DataFrame by:
        1. Converting to lowercase/uppercase or keeping original case
        2. Removing accents and diacritical marks from characters
        3. Replacing spaces and special characters with underscores
        4. Removing duplicate consecutive underscores
        5. Trimming leading/trailing underscores
        6. Handling empty column names by renaming to a specified placeholder
        7. Appending numeric suffixes to duplicate column names
        
        The original DataFrame is not modified; a copy with normalized columns is returned.
        
        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame whose column names need to be normalized.
        convert_case : str, default 'lower'
            Case conversion option: 'lower', 'upper', or None to keep original case.
        empty_col_name : str, default 'unnamed'
            Name to use for empty or unnamed columns.
        
        Returns
        -------
        pd.DataFrame
            New DataFrame with standardized column names. Original DataFrame remains unchanged.
        
        Examples
        --------
        df = pd.DataFrame({
            "First Name": [1, 2, 3],
            "Last  Name": [4, 5, 6],
            "Émployee-ID": [7, 8, 9],
            "Department Code": [10, 11, 12],
            "": [13, 14, 15],
            "First Name": [16, 17, 18]
        })
        normalized = reader.normalize_columns(df)
        print(normalized.columns.tolist())
        ['first_name', 'last_name', 'employee_id', 'department_code', 'unnamed', 'first_name_1']
        """
        df = df.copy()

        def clean(col: str) -> str:
            col = str(col).strip()

            # Apply case conversion
            if convert_case == "lower":
                col = col.lower()
            elif convert_case == "upper":
                col = col.upper()

            # Remove accents
            col = unicodedata.normalize("NFKD", col)
            col = col.encode("ascii", "ignore").decode("utf-8")

            # Replace spaces and special characters with underscores
            col = re.sub(r"[^\w]+", "_", col)

            # Remove duplicate underscores
            col = re.sub(r"_+", "_", col)

            return col.strip("_")

        cleaned_cols = [clean(c) for c in df.columns]

        # Handle empty + duplicated column names
        final_cols = []
        seen = defaultdict(int)

        for col in cleaned_cols:
            # Empty column name
            if not col:
                col = empty_col_name

            count = seen[col]
            if count > 0:
                final_cols.append(f"{col}_{count}")
            else:
                final_cols.append(col)

            seen[col] += 1

        df.columns = final_cols
        return df
# ----------------------------------------------------------------------
# Abstract base class defining the interface for all file readers
# with Template Method pattern for extensibility
# ----------------------------------------------------------------------
class FileReader(ABC, NormalizeMixin):
    """
    Abstract base class for file readers implementing the Template Method pattern.
    
    Provides a common interface for reading files with optional data normalization
    and exporting capabilities. Subclasses must implement _read() to handle 
    format-specific reading logic.
    """
    
    def __init__(self, output_dir=".", verbose=False, exporter: FileExporter = None):
        """
        Initialize the file reader.
        
        Parameters
        ----------
        output_dir : str, default "."
            Directory for exporting files.
        verbose : bool, default False
            Enable verbose output.
        exporter : FileExporter, optional
            Custom FileExporter instance.
        """
        self.output_dir = output_dir
        self.verbose = verbose
        self.exporter = exporter or FileExporter(output_dir=output_dir, verbose=verbose)
    
    def read(
        self, 
        filepath: str, 
        normalize: bool = False,
        normalize_columns: bool = False,
        **kwargs
    ) -> pd.DataFrame:
        """
        Read a file into a DataFrame with optional normalization.
        
        This method implements the Template Method pattern:
        1. Calls _read() to load the file (implemented by subclasses)
        2. Optionally normalizes column names
        3. Optionally normalizes cell values
        4. Returns the processed DataFrame
        
        Parameters
        ----------
        filepath : str
            Path to the file to read.
        normalize : bool, default False
            If True, normalize cell values (trim whitespace, convert to lowercase, etc.).
        normalize_columns : bool, default False
            If True, normalize column names (remove accents, replace spaces, handle duplicates).
        **kwargs : dict
            Additional keyword arguments passed to the specific _read() implementation.
        
        Returns
        -------
        pd.DataFrame
            The loaded and optionally normalized DataFrame.
        
        Examples
        --------
        >>> reader = CSVReader()
        >>> df = reader.read("data.csv")
        >>> df_normalized = reader.read("data.csv", normalize=True, normalize_columns=True)
        """
        # Step 1: Call the subclass-specific read implementation
        df = self._read(filepath, **kwargs)
        
        # Step 2: Normalize column names if requested
        if normalize_columns:
            df = self.normalize_columns(df)
        
        # Step 3: Normalize cell values if requested
        if normalize:
            df = self.normalize(df)
        
        return df

    @abstractmethod
    def _read(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Abstract method for reading a file into a DataFrame.
        Must be implemented by subclasses (CSVReader, ExcelReader, JSONReader, etc.).
        
        Parameters
        ----------
        filepath : str
            Path to the file to read.
        **kwargs : dict
            Format-specific keyword arguments.
        
        Returns
        -------
        pd.DataFrame
            The raw DataFrame loaded from the file.
        """
        pass

    def read_multiple_files(self, folderpath: str, **kwargs) -> dict:
        """
        Read multiple files from a directory using the read method.
        
        Parameters
        ----------
        folderpath : str
            Path to the directory containing files to read.
        **kwargs : dict
            Additional arguments passed to read() (including normalize and normalize_columns).
        
        Returns
        -------
        dict
            Dictionary mapping filenames (without extension) to DataFrames.
        
        Examples
        --------
        >>> reader = CSVReader()
        >>> files_dict = reader.read_multiple_files("data_folder/")
        >>> for filename, df in files_dict.items():
        ...     print(f"{filename}: {df.shape}")
        """
        loaded_tables = {}
        working_dir = Path(folderpath)

        for archivo in working_dir.iterdir():
            # Skip directories
            if archivo.is_dir():
                continue
            
            nombre_archivo = archivo.stem
            try:
                table = self.read(str(archivo), **kwargs)
                loaded_tables[nombre_archivo] = table
            except Exception as e:
                if self.verbose:
                    print(f"[WARNING] Could not read {archivo.name}: {e}")
                continue

        return loaded_tables

    def export(self, df, method="excel", **kwargs):
        """
        Export a DataFrame to various formats.
        
        This method is common to all FileReader subclasses and provides
        a unified interface for exporting data.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to export.
        method : str, default "excel"
            Export method. Options depend on the configured exporter:
            - 'csv': Export to CSV format
            - 'excel': Export to single Excel file
            - 'excel_parts': Split across multiple Excel files
            - 'excel_sheets': Split into multiple sheets in one file
        **kwargs : dict
            Additional arguments passed to the export method.
            Common kwargs:
            - filename : str - Output filename
            - filename_prefix : str - Prefix for multi-part exports
            - max_rows : int - Maximum rows per file/sheet
        
        Raises
        ------
        ValueError
            If an unknown export method is specified.
        
        Examples
        --------
        >>> reader = CSVReader(output_dir="exports")
        >>> df = reader.read("data.csv")
        >>> reader.export(df, method="excel", filename="output.xlsx")
        >>> reader.export(df, method="excel_parts", filename_prefix="report", max_rows=1000000)
        >>> reader.export(df, method="csv", filename="output.csv")
        """
        if method == "excel":
            self.exporter.to_excel(df, **kwargs)
        elif method == "csv":
            self.exporter.to_csv(df, **kwargs)
        elif method == "excel_parts":
            self.exporter.to_excel_multiple_parts(df, **kwargs)
        elif method == "excel_sheets":
            self.exporter.to_excel_multiple_sheets_from_df(df, **kwargs)
        else:
            raise ValueError(
                f"Unknown export method: '{method}'. "
                f"Supported methods: 'csv', 'excel', 'excel_parts', 'excel_sheets'"
            )

# ----------------------------------------------------------------------
# Base class for file readers that support multiple encodings
# ----------------------------------------------------------------------
class FileReaderEncoding(FileReader):
    """
    Base class for readers that handle files with multiple possible encodings.
    
    Tries different encodings sequentially until one successfully reads the file.
    Tracks which encoding and delimiter were successful.
    """
    
    def __init__(self, encodings=None, output_dir=".", verbose=False, exporter=None):
        """
        Initialize the reader with a list of encodings to try.
        
        Parameters
        ----------
        encodings : list, optional
            List of encodings to attempt. Defaults to COMMON_ENCODINGS.
        output_dir : str, default "."
            Directory for exporting files.
        verbose : bool, default False
            Enable verbose output.
        exporter : FileExporter, optional
            Custom FileExporter instance.
        """
        super().__init__(output_dir=output_dir, verbose=verbose, exporter=exporter)
        self.encodings = encodings or COMMON_ENCODINGS
        self.success_encoding = None

    @abstractmethod
    def _read_with_encoding(
        self, 
        filepath: str, 
        encoding: str, 
        **kwargs
    ) -> pd.DataFrame:
        """
        Abstract method to read a file with a specific encoding.
        Must be implemented by subclasses.
        
        Parameters
        ----------
        filepath : str
            Path to the file.
        encoding : str
            The encoding to use.
        **kwargs : dict
            Additional arguments.
        
        Returns
        -------
        pd.DataFrame
            The loaded DataFrame.
        
        Raises
        ------
        UnicodeDecodeError
            If the encoding doesn't match the file's actual encoding.
        """
        pass

    def _read(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Try reading the file with each encoding until one succeeds.
        
        Parameters
        ----------
        filepath : str
            Path to the file to read.
        **kwargs : dict
            Additional arguments passed to _read_with_encoding().
        
        Returns
        -------
        pd.DataFrame
            The successfully loaded DataFrame.
        
        Raises
        ------
        FileEncodingError
            If no encoding in the list can successfully read the file.
        """
        for enc in self.encodings:
            try:
                return self._read_with_encoding(filepath, enc, **kwargs)
            except UnicodeDecodeError:
                continue

        raise FileEncodingError(
            f"Could not read {filepath} with any of the following encodings: {self.encodings}"
        )

# ----------------------------------------------------------------------
# Reader for delimited text files (.csv, .tsv, etc.)
# ----------------------------------------------------------------------
class DelimitedTextReader(FileReaderEncoding):
    """
    Reader for delimited text files (CSV, TSV, etc.) with automatic encoding and delimiter detection.
    
    Tries different encoding and delimiter combinations until a valid DataFrame is produced.
    """
    
    def __init__(
        self, 
        encodings=None, 
        delimiters=None, 
        verbose=False, 
        capture_bad_lines=False,
        output_dir=".",
        exporter=None
    ):
        """
        Initialize the delimited text reader.
        
        Parameters
        ----------
        encodings : list, optional
            List of encodings to try. Defaults to COMMON_ENCODINGS.
        delimiters : list, optional
            List of delimiters to try. Defaults to COMMON_DELIMITERS.
        verbose : bool, default False
            Enable verbose output for debugging.
        capture_bad_lines : bool, default False
            Capture malformed lines for inspection.
        output_dir : str, default "."
            Output directory for exported files.
        exporter : FileExporter, optional
            Custom FileExporter instance.
        """
        super().__init__(
            encodings=encodings,
            output_dir=output_dir,
            verbose=verbose,
            exporter=exporter
        )
        self.delimiters = delimiters or COMMON_DELIMITERS
        self.success_delimiter = None
        self.capture_bad_lines = capture_bad_lines
        self.bad_lines = []

    def _read_with_encoding(
        self, 
        filepath: str, 
        encoding: str, 
        **kwargs
    ) -> pd.DataFrame:
        """
        Read delimited text file with a specific encoding and delimiter detection.
        
        This method tries all delimiters until finding one that produces a valid DataFrame.
        Prefers delimiters that produce more columns (better data structure).
        
        Parameters
        ----------
        filepath : str
            Path to the delimited text file.
        encoding : str
            The encoding to attempt.
        **kwargs : dict
            Additional pandas read_csv arguments (skiprows, nrows, dtype, etc.).
        
        Returns
        -------
        pd.DataFrame
            The loaded DataFrame.
        
        Raises
        ------
        UnicodeDecodeError
            If the encoding doesn't match the file's actual encoding.
        Exception
            If no valid delimiter is found or file reading fails.
        """
        def capture_bad_line(bad_line):
            """Callback to capture bad lines if enabled."""
            self.bad_lines.append(bad_line)
            if self.verbose:
                print(f"[WARNING] Bad line: {bad_line}")

        best_df = None
        best_delim = None
        best_col_count = 0
        error_original = None
        encoding_error = None

        for delim in self.delimiters:
            try:
                if self.verbose:
                    print(f"[DEBUG] Trying encoding='{encoding}', delimiter='{repr(delim)}'")

                if self.capture_bad_lines:
                    if self.verbose:
                        print(f"[DEBUG] Capturing bad lines (may take longer).")

                    df = pd.read_csv(
                        filepath,
                        encoding=encoding,
                        delimiter=delim,
                        engine="python",
                        on_bad_lines=capture_bad_line,
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

                # Keep track of the best result (most columns)
                if df.shape[0] > 0 and df.shape[1] > best_col_count:
                    best_df = df
                    best_delim = delim
                    best_col_count = df.shape[1]
                    
                    if self.verbose:
                        print(
                            f"[DEBUG] Better result with delimiter='{repr(delim)}': "
                            f"{df.shape[0]} rows, {df.shape[1]} columns"
                        )
                
                # Early exit if we find 2+ columns (likely correct)
                if df.shape[1] >= 2:
                    self.success_encoding = encoding
                    self.success_delimiter = delim
                    if self.verbose:
                        print(
                            f"[INFO] Success! encoding='{encoding}', delimiter='{repr(delim)}'"
                        )
                        print(
                            f"[INFO] Loaded {df.shape[0]} rows and {df.shape[1]} columns"
                        )
                    return df
            
            except FileNotFoundError as fnf_error:
                raise FileNotFoundError(f"File not found: {filepath}") from fnf_error

            except UnicodeDecodeError as ude:
                # Store the encoding error but continue to next delimiter
                # If NO delimiter works with this encoding, we'll raise UnicodeDecodeError
                # to signal the parent to try next encoding
                encoding_error = ude
                if self.verbose:
                    print(
                        f"[DEBUG] Encoding error with encoding='{encoding}', delimiter='{repr(delim)}'"
                    )
                continue

            except (pd.errors.ParserError, ValueError) as e:
                error_original = e
                if self.verbose:
                    print(
                        f"[DEBUG] Failed with encoding='{encoding}', delimiter='{repr(delim)}'"
                    )
                continue

        # If we found any valid result, return the best one even if it's just 1 column
        if best_df is not None:
            self.success_encoding = encoding
            self.success_delimiter = best_delim
            if self.verbose:
                print(
                    f"[INFO] Success (best match)! encoding='{encoding}', delimiter='{repr(best_delim)}'"
                )
                print(
                    f"[INFO] Loaded {best_df.shape[0]} rows and {best_df.shape[1]} columns"
                )
            return best_df

        # If we got a UnicodeDecodeError and nothing worked, re-raise it
        # so the parent FileReaderEncoding._read() tries the next encoding
        if encoding_error is not None:
            raise encoding_error

        # If all attempts failed, raise error
        raise Exception(
            f"Could not read {filepath} with any delimiter combination. "
            f"Last error: {error_original}"
        )