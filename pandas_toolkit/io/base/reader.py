from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import numpy as np
from pandas_toolkit.io.base.mixins import NormalizeMixin


class FileReader(ABC, NormalizeMixin):
    """
    Abstract base class defining the interface for all file readers.
    
    Uses Template Method pattern:
    - read() is the template method that calls _read()
    - Subclasses must implement _read()
    - Provides common functionality: normalization, export, batch operations
    
    Attributes
    ----------
    output_dir : str
        Directory for exporting files.
    verbose : bool
        Enable verbose output.
    exporter : FileExporter
        Instance for exporting DataFrames.
    """
    
    def __init__(self, output_dir=".", verbose=False, exporter=None):
        """
        Initialize the file reader.
        
        Parameters
        ----------
        output_dir : str, default "."
            Directory where exported files will be saved.
        verbose : bool, default False
            Enable verbose output for debugging.
        exporter : FileExporter, optional
            Custom FileExporter instance. If None, creates default.
        """
        self.output_dir = output_dir
        self.verbose = verbose
        
        # Import aquí solo si exporter es None para evitar imports al inicio
        if exporter is None:
            from pandas_toolkit.io.exporter import FileExporter
            self.exporter = FileExporter(output_dir=output_dir, verbose=verbose)
        else:
            self.exporter = exporter

    @abstractmethod
    def _read(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Abstract method to read a file. Must be implemented by subclasses.
        
        Parameters
        ----------
        filepath : str
            Path to the file to read.
        **kwargs : dict
            Format-specific arguments.
        
        Returns
        -------
        pd.DataFrame
            The loaded DataFrame.
        """
        pass

    def read(
        self, 
        filepath: str, 
        normalize: bool = False,
        normalize_columns: bool = False,
        skip_leading_empty_rows: bool = True,
        skip_trailing_empty_rows: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Read a file (Template Method).
        
        This is the main entry point. It:
        1. Calls _read() to load the file (implemented by subclasses)
        2. Skips leading/trailing empty rows if requested
        3. Normalizes column names if requested
        4. Normalizes cell values if requested
        
        Parameters
        ----------
        filepath : str
            Path to the file to read.
        normalize : bool, default False
            Normalize cell values (create "_norm" columns).
        normalize_columns : bool, default False
            Normalize column names.
        skip_leading_empty_rows : bool, default True
            Skip rows at the beginning that are completely empty.
            Useful for files with header information before data.
        skip_trailing_empty_rows : bool, default True
            Skip rows at the end that are completely empty.
        **kwargs : dict
            Additional arguments passed to _read().
        
        Returns
        -------
        pd.DataFrame
            The loaded (and optionally normalized) DataFrame.
        
        Examples
        --------
        >>> reader = CSVReader()
        >>> df = reader.read("file.csv")
        >>> df = reader.read("file.csv", normalize=True, normalize_columns=True)
        
        >>> # File with 5 empty rows before data starts
        >>> df = reader.read("messy_file.csv", skip_leading_empty_rows=True)
        """
        # Load the file using subclass implementation
        df = self._read(filepath, **kwargs)
        
        # Skip empty rows at the beginning
        if skip_leading_empty_rows:
            df = self.skip_leading_empty_rows(df)
        
        # Skip empty rows at the end
        if skip_trailing_empty_rows:
            df = self.skip_trailing_empty_rows(df)
        
        # Normalize column names if requested
        if normalize_columns:
            df = self.normalize_columns(df)
        
        # Normalize values if requested
        if normalize:
            df = self.normalize(df)
        
        return df

    @staticmethod
    def skip_leading_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove completely empty rows from the beginning of DataFrame.
        
        A row is considered empty if all values are NaN or empty strings.
        
        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with leading empty rows removed.
        
        Examples
        --------
        >>> # DataFrame with 3 empty rows at start
        >>> df = pd.DataFrame({
        ...     'A': [None, None, None, 1, 2],
        ...     'B': [None, None, None, 3, 4]
        ... })
        >>> clean_df = FileReader.skip_leading_empty_rows(df)
        >>> clean_df
           A  B
        0  1  3
        1  2  4
        """
        if df.empty:
            return df.copy()
        
        # Función para verificar si una fila está vacía
        def is_row_empty(row):
            """Check if a row is completely empty (all NaN or empty strings)."""
            return all(
                pd.isna(val) or (isinstance(val, str) and val.strip() == '')
                for val in row
            )
        
        # Encontrar el primer índice de fila que NO está vacía
        for idx, row_idx in enumerate(df.index):
            if not is_row_empty(df.iloc[idx]):
                # Retornar desde la primera fila no-vacía
                return df.iloc[idx:].reset_index(drop=True)
        
        # Si todas las filas están vacías, retornar DataFrame vacío
        return df.iloc[:0].reset_index(drop=True)

    @staticmethod
    def skip_trailing_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove completely empty rows from the end of DataFrame.
        
        A row is considered empty if all values are NaN or empty strings.
        
        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with trailing empty rows removed.
        
        Examples
        --------
        >>> # DataFrame with 2 empty rows at end
        >>> df = pd.DataFrame({
        ...     'A': [1, 2, None, None],
        ...     'B': [3, 4, None, None]
        ... })
        >>> clean_df = FileReader.skip_trailing_empty_rows(df)
        >>> clean_df
           A  B
        0  1  3
        1  2  4
        """
        if df.empty:
            return df.copy()
        
        # Función para verificar si una fila está vacía
        def is_row_empty(row):
            """Check if a row is completely empty (all NaN or empty strings)."""
            return all(
                pd.isna(val) or (isinstance(val, str) and val.strip() == '')
                for val in row
            )
        
        # Iterar desde el final hacia atrás
        for idx in range(len(df) - 1, -1, -1):
            if not is_row_empty(df.iloc[idx]):
                # Retornar hasta e incluyendo la última fila no-vacía
                return df.iloc[:idx + 1].reset_index(drop=True)
        
        # Si todas las filas están vacías
        return df.iloc[:0].reset_index(drop=True)

    @staticmethod
    def detect_header_row(
        df: pd.DataFrame, 
        max_rows_to_check: int = 10
    ) -> int:
        """
        Detect which row contains the actual header/column names.
        
        Useful when file has metadata or empty rows before the actual header.
        Looks for the first row with significant non-null values.
        
        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame (usually read with header=None).
        max_rows_to_check : int, default 10
            Maximum number of rows to inspect.
        
        Returns
        -------
        int
            Row index that contains the header (0-based).
        
        Examples
        --------
        >>> # File with 3 rows of metadata before header
        >>> df = pd.read_csv("file.csv", header=None)
        >>> header_row = FileReader.detect_header_row(df)
        >>> actual_header = df.iloc[header_row].values.tolist()
        >>> df_clean = df.iloc[header_row+1:].reset_index(drop=True)
        >>> df_clean.columns = actual_header
        """
        for idx in range(min(max_rows_to_check, len(df))):
            row = df.iloc[idx]
            
            # Count non-null and non-empty values
            non_null_count = sum(
                1 for val in row 
                if pd.notna(val) and (not isinstance(val, str) or val.strip() != '')
            )
            
            # If row has significant data (>50% non-null), it's likely the header
            if non_null_count >= len(row) * 0.5:
                return idx
        
        # If no header found, return first row
        return 0

    def read_with_metadata_rows(
        self,
        filepath: str,
        skip_rows: int = 0,
        **kwargs
    ) -> pd.DataFrame:
        """
        Read a file that has metadata or empty rows before the actual data.
        
        Combines skip_rows with automatic empty row removal for robustness.
        
        Parameters
        ----------
        filepath : str
            Path to the file to read.
        skip_rows : int, default 0
            Number of rows to skip from the beginning.
            Can be useful in combination with skip_leading_empty_rows.
        **kwargs : dict
            Additional arguments passed to read().
        
        Returns
        -------
        pd.DataFrame
            Cleaned DataFrame.
        
        Examples
        --------
        >>> reader = CSVReader()
        >>> # Skip first 2 rows of metadata, then skip empty rows
        >>> df = reader.read_with_metadata_rows("file.csv", skip_rows=2)
        """
        if skip_rows > 0:
            kwargs['skiprows'] = skip_rows
        
        return self.read(
            filepath,
            skip_leading_empty_rows=True,
            skip_trailing_empty_rows=True,
            **kwargs
        )

    def read_multiple_files(
        self, 
        folderpath: str, 
        skip_leading_empty_rows: bool = True,
        skip_trailing_empty_rows: bool = True,
        **kwargs
    ) -> dict:
        """
        Read all compatible files from a directory.
        
        Parameters
        ----------
        folderpath : str
            Path to the folder containing files.
        skip_leading_empty_rows : bool, default True
            Skip leading empty rows in each file.
        skip_trailing_empty_rows : bool, default True
            Skip trailing empty rows in each file.
        **kwargs : dict
            Arguments passed to read() (normalize, normalize_columns, etc.).
        
        Returns
        -------
        dict
            Dictionary mapping filenames (without extension) to DataFrames.
        
        Examples
        --------
        >>> reader = CSVReader()
        >>> files = reader.read_multiple_files("data_folder/")
        >>> for filename, df in files.items():
        ...     print(f"{filename}: {df.shape}")
        """
        folder = Path(folderpath)
        files_dict = {}
        
        if not folder.is_dir():
            raise ValueError(f"{folderpath} is not a valid directory")
        
        # Get files with appropriate extensions (subclasses define this)
        file_extensions = self._get_file_extensions()
        
        for filepath in folder.iterdir():
            if not filepath.is_file():
                continue
            
            if filepath.suffix.lower() not in file_extensions:
                continue
            
            try:
                filename = filepath.stem  # Name without extension
                df = self.read(
                    filepath,
                    skip_leading_empty_rows=skip_leading_empty_rows,
                    skip_trailing_empty_rows=skip_trailing_empty_rows,
                    **kwargs
                )
                files_dict[filename] = df
                
                if self.verbose:
                    print(f"[INFO] Loaded {filename}: {df.shape}")
            
            except Exception as e:
                if self.verbose:
                    print(f"[WARNING] Failed to read {filepath.name}: {e}")
                continue
        
        return files_dict

    def _get_file_extensions(self) -> list:
        """
        Get file extensions this reader supports.
        
        Must be overridden by subclasses.
        
        Returns
        -------
        list
            List of file extensions (e.g., ['.csv', '.CSV']).
        """
        raise NotImplementedError("Subclasses must implement _get_file_extensions()")

    def export(self, df: pd.DataFrame, method: str = "excel", **kwargs) -> None:
        """
        Export DataFrame to a file.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to export.
        method : str, default "excel"
            Export method: 'csv', 'excel', 'excel_parts', 'excel_sheets'.
        **kwargs : dict
            Format-specific arguments (filename, max_rows, etc.).
        
        Examples
        --------
        >>> reader = CSVReader(output_dir="exports")
        >>> reader.export(df, method="csv", filename="output.csv")
        >>> reader.export(df, method="excel", filename="output.xlsx")
        """
        self.exporter.export(df, method=method, **kwargs)