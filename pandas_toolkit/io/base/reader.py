from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
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
        **kwargs
    ) -> pd.DataFrame:
        """
        Read a file (Template Method).
        
        This is the main entry point. It:
        1. Calls _read() to load the file (implemented by subclasses)
        2. Normalizes column names if requested
        3. Normalizes cell values if requested
        
        Parameters
        ----------
        filepath : str
            Path to the file to read.
        normalize : bool, default False
            Normalize cell values (create "_norm" columns).
        normalize_columns : bool, default False
            Normalize column names.
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
        """
        # Load the file using subclass implementation
        df = self._read(filepath, **kwargs)
        
        # Normalize column names if requested
        if normalize_columns:
            df = self.normalize_columns(df)
        
        # Normalize values if requested
        if normalize:
            df = self.normalize(df)
        
        return df

    def read_multiple_files(
        self, 
        folderpath: str, 
        **kwargs
    ) -> dict:
        """
        Read all compatible files from a directory.
        
        Parameters
        ----------
        folderpath : str
            Path to the folder containing files.
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
                df = self.read(filepath, **kwargs)
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