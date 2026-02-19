import pandas as pd
from pathlib import Path
from pandas_toolkit.io.base import FileReader
from pandas_toolkit.io.exporter import FileExporter


class HTMLReader(FileReader):
    """
    HTML file reader supporting multiple tables extraction.
    
    Features:
    - Read single or multiple tables from HTML files
    - Automatic table detection using pandas read_html
    - Support for Oracle exports and other HTML table formats
    - Data normalization (column names and values)
    - Export to multiple formats
    
    The reader uses pandas read_html which automatically detects and extracts
    all <table> elements from HTML files.
    
    Examples
    --------
    >>> reader = HTMLReader()
    >>> # Read first table by default
    >>> df = reader.read("oracle_export.html")
    >>> 
    >>> # Read specific table by index
    >>> df2 = reader.read("oracle_export.html", table_index=2)
    >>> 
    >>> # Read all tables
    >>> tables = reader.read_all_tables("oracle_export.html")
    >>> df0 = tables[0]
    >>> df1 = tables[1]
    """
    
    def __init__(
        self,
        output_dir=".",
        verbose=False,
        exporter: FileExporter = None
    ):
        """
        Initialize the HTML reader.
        
        Parameters
        ----------
        output_dir : str, default "."
            Output directory for exported files.
        verbose : bool, default False
            Enable verbose output for debugging.
        exporter : FileExporter, optional
            Custom FileExporter instance.
        
        Examples
        --------
        >>> reader = HTMLReader()
        >>> reader = HTMLReader(verbose=True, output_dir="exports")
        """
        super().__init__(output_dir=output_dir, verbose=verbose, exporter=exporter)
        self.tables_count = None

    def _read(self, filepath: str, table_index: int = 0, **kwargs) -> pd.DataFrame:
        """
        Read a specific table from an HTML file.
        
        By default reads the first table (index 0). Uses pandas read_html
        which extracts all <table> elements from the HTML document.
        
        Parameters
        ----------
        filepath : str
            Path to the HTML file.
        table_index : int, default 0
            Index of the table to read (0 for first table).
        **kwargs : dict
            Additional pandas read_html arguments (header, skiprows, etc.).
            See pandas.read_html documentation for all options.
        
        Returns
        -------
        pd.DataFrame
            The loaded DataFrame from the specified table.
        
        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If no tables are found or table_index is out of range.
        
        Examples
        --------
        >>> reader = HTMLReader()
        >>> df = reader.read("oracle_export.html")
        >>> df = reader.read("oracle_export.html", table_index=1)  # Second table
        >>> 
        >>> # With additional pandas options
        >>> df = reader.read("data.html", table_index=0, header=0)
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            if self.verbose:
                print(f"[DEBUG] Reading HTML file: {filepath}")
            
            # pd.read_html returns a list of all tables in the HTML
            tables = pd.read_html(filepath, **kwargs)
            self.tables_count = len(tables)
            
            if not tables:
                raise ValueError(f"No tables found in HTML file: {filepath}")
            
            if self.verbose:
                print(f"[INFO] Found {self.tables_count} table(s) in HTML file")
            
            # Validate table index
            if table_index < 0 or table_index >= self.tables_count:
                raise ValueError(
                    f"Table index {table_index} is out of range. "
                    f"Found {self.tables_count} table(s) (valid indices: 0-{self.tables_count-1})"
                )
            
            df = tables[table_index]
            
            if self.verbose:
                print(
                    f"[INFO] Successfully read table {table_index}: "
                    f"{df.shape[0]} rows, {df.shape[1]} columns"
                )
            
            return df
        
        except ValueError as ve:
            # Re-raise ValueError as is
            raise ve
        
        except Exception as e:
            if self.verbose:
                print(f"[ERROR] Failed to read HTML file: {type(e).__name__}: {e}")
            raise Exception(
                f"Could not read HTML file {filepath}. "
                f"Error: {type(e).__name__}: {e}"
            )

    def get_tables_count(self, filepath: str, **kwargs) -> int:
        """
        Get the number of tables in an HTML file without loading data.
        
        Parameters
        ----------
        filepath : str
            Path to the HTML file.
        **kwargs : dict
            Additional pandas read_html arguments.
        
        Returns
        -------
        int
            Number of tables found in the HTML file.
        
        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        
        Examples
        --------
        >>> reader = HTMLReader()
        >>> count = reader.get_tables_count("oracle_export.html")
        >>> print(f"Found {count} tables")
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            if self.verbose:
                print(f"[DEBUG] Counting tables in: {filepath}")
            
            tables = pd.read_html(filepath, **kwargs)
            count = len(tables)
            
            if self.verbose:
                print(f"[INFO] Found {count} table(s)")
            
            return count
        
        except Exception as e:
            if self.verbose:
                print(f"[ERROR] Failed to count tables: {type(e).__name__}: {e}")
            raise

    def read_all_tables(
        self, 
        filepath: str,
        normalize: bool = False,
        normalize_columns: bool = False,
        skip_leading_empty_rows: bool = True,
        skip_trailing_empty_rows: bool = True,
        **kwargs
    ) -> list:
        """
        Read all tables from an HTML file.
        
        Returns a list of DataFrames, one for each table found in the HTML.
        Similar to how pd.read_html returns multiple tables.
        
        Parameters
        ----------
        filepath : str
            Path to the HTML file.
        normalize : bool, default False
            Normalize cell values (create "_norm" columns).
        normalize_columns : bool, default False
            Normalize column names.
        skip_leading_empty_rows : bool, default True
            Skip rows at the beginning that are completely empty.
        skip_trailing_empty_rows : bool, default True
            Skip rows at the end that are completely empty.
        **kwargs : dict
            Additional pandas read_html arguments.
        
        Returns
        -------
        list
            List of DataFrames, one for each table in the HTML file.
        
        Examples
        --------
        >>> reader = HTMLReader()
        >>> tables = reader.read_all_tables("oracle_export.html")
        >>> df0 = tables[0]  # Primera tabla
        >>> df1 = tables[1]  # Segunda tabla
        >>> df2 = tables[2]  # Tercera tabla
        >>> 
        >>> # With normalization
        >>> tables = reader.read_all_tables(
        ...     "oracle_export.html",
        ...     normalize=True,
        ...     normalize_columns=True
        ... )
        >>> 
        >>> # Process all tables
        >>> for i, df in enumerate(tables):
        ...     print(f"Table {i}: {df.shape}")
        ...     reader.export(df, method="csv", filename=f"table_{i}.csv")
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        count = self.get_tables_count(filepath, **kwargs)
        
        if self.verbose:
            print(f"[INFO] Reading {count} table(s) from {filepath}")
        
        tables_list = []
        for idx in range(count):
            try:
                # Use the regular read method which handles normalization
                df = self.read(
                    filepath,
                    table_index=idx,
                    normalize=normalize,
                    normalize_columns=normalize_columns,
                    skip_leading_empty_rows=skip_leading_empty_rows,
                    skip_trailing_empty_rows=skip_trailing_empty_rows,
                    **kwargs
                )
                tables_list.append(df)
                
                if self.verbose:
                    print(f"[INFO] Loaded table {idx}: {df.shape}")
            
            except Exception as e:
                if self.verbose:
                    print(f"[WARNING] Failed to read table {idx}: {e}")
                # Continue with next table instead of failing completely
                continue
        
        if not tables_list:
            raise ValueError(f"Could not read any tables from {filepath}")
        
        return tables_list

    def read_multiple_tables(
        self, 
        filepath: str,
        table_indices: list = None,
        normalize: bool = False,
        normalize_columns: bool = False,
        skip_leading_empty_rows: bool = True,
        skip_trailing_empty_rows: bool = True,
        **kwargs
    ) -> dict:
        """
        Read specific tables from an HTML file.
        
        Returns a dictionary mapping table indices to DataFrames.
        Similar to ExcelReader's read_multiple_sheets.
        
        Parameters
        ----------
        filepath : str
            Path to the HTML file.
        table_indices : list, optional
            List of table indices to read. If None, reads all tables.
        normalize : bool, default False
            Normalize cell values (create "_norm" columns).
        normalize_columns : bool, default False
            Normalize column names.
        skip_leading_empty_rows : bool, default True
            Skip rows at the beginning that are completely empty.
        skip_trailing_empty_rows : bool, default True
            Skip rows at the end that are completely empty.
        **kwargs : dict
            Additional pandas read_html arguments.
        
        Returns
        -------
        dict
            Dictionary mapping table index to DataFrame.
        
        Examples
        --------
        >>> reader = HTMLReader()
        >>> # Read all tables as dictionary
        >>> tables = reader.read_multiple_tables("oracle_export.html")
        >>> df0 = tables[0]
        >>> df1 = tables[1]
        >>> 
        >>> # Read specific tables
        >>> tables = reader.read_multiple_tables(
        ...     "oracle_export.html",
        ...     table_indices=[0, 2, 5]
        ... )
        >>> 
        >>> # Iterate over tables
        >>> for idx, df in tables.items():
        ...     print(f"Table {idx}: {df.shape}")
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Get all table indices if not provided
        if table_indices is None:
            count = self.get_tables_count(filepath, **kwargs)
            table_indices = list(range(count))
        
        if self.verbose:
            print(f"[INFO] Reading {len(table_indices)} table(s) from {filepath}")
        
        tables_dict = {}
        for idx in table_indices:
            try:
                df = self.read(
                    filepath,
                    table_index=idx,
                    normalize=normalize,
                    normalize_columns=normalize_columns,
                    skip_leading_empty_rows=skip_leading_empty_rows,
                    skip_trailing_empty_rows=skip_trailing_empty_rows,
                    **kwargs
                )
                tables_dict[idx] = df
                
                if self.verbose:
                    print(f"[INFO] Loaded table {idx}: {df.shape}")
            
            except Exception as e:
                if self.verbose:
                    print(f"[WARNING] Failed to read table {idx}: {e}")
                continue
        
        if not tables_dict:
            raise ValueError(
                f"Could not read any of the requested tables from {filepath}"
            )
        
        return tables_dict

    def _get_file_extensions(self) -> list:
        """Get file extensions for HTML files."""
        return ['.html', '.HTML', '.htm', '.HTM']
