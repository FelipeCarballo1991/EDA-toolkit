import pandas as pd
from pandas_toolkit.io.base import FileReader
from pandas_toolkit.io.exporter import FileExporter


class ExcelReader(FileReader):
    """
    Excel file reader supporting both .xlsx and .xls formats.
    
    Features:
    - Read single or multiple sheets
    - Automatic sheet detection
    - Data normalization (column names and values)
    - Export to multiple formats
    
    Examples
    --------
    >>> reader = ExcelReader()
    >>> df = reader.read("data.xlsx")
    >>> df = reader.read("data.xlsx", sheet_name="Sheet2")
    >>> sheets = reader.read_multiple_sheets("data.xlsx")
    """
    
    def __init__(
        self,
        output_dir=".",
        verbose=False,
        exporter: FileExporter = None
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
        """
        super().__init__(output_dir=output_dir, verbose=verbose, exporter=exporter)

    def _read(self, filepath: str, sheet_name=0, **kwargs) -> pd.DataFrame:
        """
        Read an Excel file.
        
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
        
        Examples
        --------
        >>> reader = ExcelReader()
        >>> df = reader.read("data.xlsx", sheet_name="Sales")
        >>> df = reader.read("data.xlsx", sheet_name=1)  # Second sheet
        """
        if self.verbose:
            print(f"[INFO] Reading Excel file: {filepath}, sheet: {sheet_name}")
        
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)
            
            if self.verbose:
                print(f"[INFO] Successfully loaded {df.shape[0]} rows, {df.shape[1]} columns")
            
            return df
        
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {filepath}") from e
        except Exception as e:
            raise Exception(f"Error reading Excel file {filepath}: {e}") from e

    def read_sheet_names(self, filepath: str) -> list:
        """
        Get all sheet names from an Excel file without loading data.
        
        Parameters
        ----------
        filepath : str
            Path to the Excel file.
        
        Returns
        -------
        list
            List of sheet names in the workbook.
        
        Examples
        --------
        >>> reader = ExcelReader()
        >>> sheets = reader.read_sheet_names("data.xlsx")
        >>> print(sheets)
        ['Sales', 'Inventory', 'Customers']
        """
        try:
            xls = pd.ExcelFile(filepath)
            return xls.sheet_names
        except Exception as e:
            raise Exception(f"Error reading sheet names from {filepath}: {e}") from e

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
        if sheet_names is None:
            sheet_names = self.read_sheet_names(filepath)
        
        if self.verbose:
            print(f"[INFO] Reading {len(sheet_names)} sheets from {filepath}")
        
        sheets_dict = {}
        for sheet_name in sheet_names:
            try:
                df = self.read(filepath, sheet_name=sheet_name, **kwargs)
                sheets_dict[sheet_name] = df
                
                if self.verbose:
                    print(f"[INFO] Loaded sheet '{sheet_name}': {df.shape}")
            
            except Exception as e:
                if self.verbose:
                    print(f"[WARNING] Failed to read sheet '{sheet_name}': {e}")
                continue
        
        return sheets_dict

    def _get_file_extensions(self) -> list:
        """Get file extensions for Excel files."""
        return ['.xlsx', '.XLSX', '.xls', '.XLS']