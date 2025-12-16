import pandas as pd
from pathlib import Path
from pandas_toolkit.io.base import FileReader
from pandas_toolkit.io.base.constants import EXCEL_ENGINES, EXCEL_ENGINES_BY_FORMAT
from pandas_toolkit.io.exporter import FileExporter


class ExcelReader(FileReader):
    """
    Excel file reader supporting both .xlsx and .xls formats.
    
    Features:
    - Read single or multiple sheets
    - Automatic engine detection and fallback
    - Automatic sheet detection
    - Data normalization (column names and values)
    - Export to multiple formats
    
    The reader attempts different pandas engines (openpyxl, xlrd) 
    to maximize compatibility with various Excel file formats and versions.
    
    Examples
    --------
    >>> reader = ExcelReader()
    >>> df = reader.read("data.xlsx")
    >>> df = reader.read("data.xlsx", sheet_name="Sheet2")
    >>> sheets = reader.read_multiple_sheets("data.xlsx")
    >>> print(reader.success_engine)  # Track which engine was used
    """
    
    def __init__(
        self,
        output_dir=".",
        verbose=False,
        exporter: FileExporter = None,
        engines=None
    ):
        """
        Initialize the Excel reader.
        
        Parameters
        ----------
        output_dir : str, default "."
            Output directory for exported files.
        verbose : bool, default False
            Enable verbose output for debugging.
        exporter : FileExporter, optional
            Custom FileExporter instance.
        engines : dict, optional
            Custom engine mapping {file_extension: [engine_list]}.
            Defaults to EXCEL_ENGINES.
        
        Examples
        --------
        >>> reader = ExcelReader()
        >>> reader = ExcelReader(verbose=True)
        >>> custom_engines = {
        ...     ".xlsx": ["openpyxl"],
        ...     ".xls": ["xlrd"]
        ... }
        >>> reader = ExcelReader(engines=custom_engines)
        """
        super().__init__(output_dir=output_dir, verbose=verbose, exporter=exporter)
        
        self.engines = engines or EXCEL_ENGINES
        self.success_engine = None

    def _get_engines_for_file(self, filepath: str) -> list:
        """
        Get list of engines to try for a specific file.
        
        Parameters
        ----------
        filepath : str
            Path to the Excel file.
        
        Returns
        -------
        list
            List of engines to try in order.
        
        Examples
        --------
        >>> reader = ExcelReader()
        >>> engines = reader._get_engines_for_file("data.xlsx")
        >>> print(engines)
        ['openpyxl', 'xlrd']
        """
        filepath_obj = Path(filepath)
        extension = filepath_obj.suffix.lower()
        
        # Get engines for this file type, or use default
        return self.engines.get(extension, self.engines.get("default", ["openpyxl"]))

    def _read(self, filepath: str, sheet_name=0, **kwargs) -> pd.DataFrame:
        """
        Read an Excel file with automatic engine detection and fallback.
        
        This method tries different pandas engines until one successfully
        reads the file. Useful for handling files created with different
        Excel versions or with corrupted formatting.
        
        Parameters
        ----------
        filepath : str
            Path to the Excel file (.xlsx or .xls).
        sheet_name : str or int, default 0
            Name of sheet to read, or 0 for first sheet.
        **kwargs : dict
            Additional pandas read_excel arguments (header, skiprows, usecols, etc.).
        
        Returns
        -------
        pd.DataFrame
            The loaded DataFrame.
        
        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        Exception
            If no engine can successfully read the file.
        
        Examples
        --------
        >>> reader = ExcelReader()
        >>> df = reader.read("data.xlsx", sheet_name="Sales")
        >>> df = reader.read("data.xlsx", sheet_name=1)  # Second sheet
        >>> print(f"Read with engine: {reader.success_engine}")
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        engines_to_try = self._get_engines_for_file(filepath)
        last_error = None
        
        for engine in engines_to_try:
            try:
                if self.verbose:
                    print(
                        f"[DEBUG] Trying to read Excel with engine='{engine}', "
                        f"sheet={sheet_name}"
                    )
                
                df = pd.read_excel(
                    filepath,
                    sheet_name=sheet_name,
                    engine=engine,
                    **kwargs
                )
                
                # Success!
                self.success_engine = engine
                
                if self.verbose:
                    print(
                        f"[INFO] Successfully read with engine='{engine}': "
                        f"{df.shape[0]} rows, {df.shape[1]} columns"
                    )
                
                return df
            
            except ImportError as ie:
                last_error = ie
                if self.verbose:
                    print(
                        f"[DEBUG] Engine '{engine}' not available: {ie}"
                    )
                continue
            
            except Exception as e:
                last_error = e
                if self.verbose:
                    print(
                        f"[DEBUG] Failed with engine '{engine}': {type(e).__name__}: {e}"
                    )
                continue
        
        # If all engines failed, provide helpful error message
        raise Exception(
            f"Could not read Excel file {filepath} with any of the following engines: "
            f"{engines_to_try}. Last error: {last_error}"
        )

    def read_sheet_names(self, filepath: str) -> list:
        """
        Get all sheet names from an Excel file without loading data.
        
        This method tries different engines to detect sheet names.
        
        Parameters
        ----------
        filepath : str
            Path to the Excel file.
        
        Returns
        -------
        list
            List of sheet names in the workbook.
        
        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        Exception
            If no engine can read the file.
        
        Examples
        --------
        >>> reader = ExcelReader()
        >>> sheets = reader.read_sheet_names("data.xlsx")
        >>> print(sheets)
        ['Sales', 'Inventory', 'Customers']
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        engines_to_try = self._get_engines_for_file(filepath)
        last_error = None
        
        for engine in engines_to_try:
            try:
                if self.verbose:
                    print(f"[DEBUG] Getting sheet names with engine='{engine}'")
                
                xls = pd.ExcelFile(filepath, engine=engine)
                
                if self.verbose:
                    print(f"[INFO] Found {len(xls.sheet_names)} sheets")
                
                return xls.sheet_names
            
            except ImportError as ie:
                last_error = ie
                if self.verbose:
                    print(f"[DEBUG] Engine '{engine}' not available: {ie}")
                continue
            
            except Exception as e:
                last_error = e
                if self.verbose:
                    print(f"[DEBUG] Failed with engine '{engine}': {type(e).__name__}")
                continue
        
        raise Exception(
            f"Could not read sheet names from {filepath} with any of the following engines: "
            f"{engines_to_try}. Last error: {last_error}"
        )

    def read_multiple_sheets(
        self, 
        filepath: str, 
        sheet_names=None,
        **kwargs
    ) -> dict:
        """
        Read multiple sheets from an Excel file.
        
        Parameters
        ----------
        filepath : str
            Path to the Excel file.
        sheet_names : list, optional
            List of sheet names to read. If None, reads all sheets.
        **kwargs : dict
            Additional arguments (normalize, normalize_columns, etc.).
        
        Returns
        -------
        dict
            Dictionary mapping sheet names to DataFrames.
        
        Examples
        --------
        >>> reader = ExcelReader()
        >>> sheets = reader.read_multiple_sheets("data.xlsx")
        >>> for sheet_name, df in sheets.items():
        ...     print(f"{sheet_name}: {df.shape}")
        
        >>> # Read specific sheets
        >>> sheets = reader.read_multiple_sheets(
        ...     "data.xlsx", 
        ...     sheet_names=["Sales", "Inventory"]
        ... )
        """
        # Get sheet names if not provided
        if sheet_names is None:
            sheet_names = self.read_sheet_names(filepath)
        
        if self.verbose:
            print(
                f"[INFO] Reading {len(sheet_names)} sheets from {filepath}"
            )
        
        sheets_dict = {}
        for sheet_name in sheet_names:
            try:
                df = self.read(filepath, sheet_name=sheet_name, **kwargs)
                sheets_dict[sheet_name] = df
                
                if self.verbose:
                    print(f"[INFO] Loaded sheet '{sheet_name}': {df.shape}")
            
            except Exception as e:
                if self.verbose:
                    print(
                        f"[WARNING] Failed to read sheet '{sheet_name}': {e}"
                    )
                continue
        
        return sheets_dict

    def _get_file_extensions(self) -> list:
        """Get file extensions for Excel files."""
        return ['.xlsx', '.XLSX', '.xls', '.XLS']