# pandas_toolkit/io/exporters.py
import pandas as pd
from pathlib import Path

class FileExporter:
    """
    Exporter for saving DataFrames to various file formats.
    
    Supports multiple export methods:
    - csv: Single CSV file
    - excel: Single Excel file (single sheet)
    - excel_parts: Multiple Excel files (split by max_rows)
    - excel_sheets: Single Excel file with multiple sheets (split by max_rows)
    
    Examples
    --------
    >>> exporter = FileExporter(output_dir="exports")
    >>> exporter.export(df, method="csv", filename="data.csv")
    >>> exporter.export(df, method="excel", filename="data.xlsx")
    >>> exporter.export(df, method="excel_parts", filename_prefix="data", max_rows=1000)
    """
    
    def __init__(self, output_dir=".", verbose=False):
        """
        Initialize the file exporter.
        
        Parameters
        ----------
        output_dir : str, default "."
            Directory where exported files will be saved.
        verbose : bool, default False
            Enable verbose output for debugging.
        """
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self, 
        df: pd.DataFrame, 
        method: str = "excel",
        **kwargs
    ) -> None:
        """
        Export DataFrame to a file using the specified method.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to export.
        method : str, default "excel"
            Export method: 'csv', 'excel', 'excel_parts', 'excel_sheets'.
        **kwargs : dict
            Format-specific arguments (filename, max_rows, etc.).
        
        Raises
        ------
        ValueError
            If method is not recognized.
        
        Examples
        --------
        >>> exporter = FileExporter(output_dir="exports")
        >>> exporter.export(df, method="csv", filename="data.csv")
        >>> exporter.export(df, method="excel", filename="report.xlsx")
        >>> exporter.export(df, method="excel_parts", filename_prefix="report", max_rows=5000)
        >>> exporter.export(df, method="excel_sheets", filename="report.xlsx", max_rows=5000)
        """
        if method == "csv":
            self._export_csv(df, **kwargs)
        elif method == "excel":
            self._export_excel(df, **kwargs)
        elif method == "excel_parts":
            self._export_excel_parts(df, **kwargs)
        elif method == "excel_sheets":
            self._export_excel_sheets(df, **kwargs)
        else:
            raise ValueError(
                f"Unknown export method: '{method}'. "
                f"Supported methods: 'csv', 'excel', 'excel_parts', 'excel_sheets'"
            )

    def export_tables(
        self,
        tables: list | pd.DataFrame,
        filename: str,
        method: str = "excel",
        max_rows_per_sheet: int = 1000000,
        **kwargs
    ) -> None:
        """
        Export one or multiple DataFrames with intelligent handling.
        
        This is a high-level method that handles complex export scenarios:
        - Single table: exports as single file (splitting if exceeds max_rows)
        - Multiple tables: exports to single Excel file with multiple sheets
        - Large tables: automatically splits into multiple sheets/files
        
        Parameters
        ----------
        tables : list[pd.DataFrame] or pd.DataFrame
            Single DataFrame or list of DataFrames to export.
        filename : str
            Base filename for output file(s).
            For Excel: "report.xlsx" or "report" (extension added automatically).
            For CSV: only single table supported.
        method : str, default "excel"
            Export method: 'excel' or 'csv'.
            CSV only supports single table export.
        max_rows_per_sheet : int, default 1000000
            Maximum rows per Excel sheet. When exceeded, splits into multiple sheets.
        **kwargs : dict
            Additional arguments passed to underlying export methods.
        
        Raises
        ------
        ValueError
            If method is 'csv' and multiple tables provided.
        
        Examples
        --------
        >>> exporter = FileExporter(output_dir="exports")
        >>> 
        >>> # Single DataFrame - simple export
        >>> exporter.export_tables(df, filename="report.xlsx")
        >>> 
        >>> # Single large DataFrame - auto-split into sheets
        >>> large_df = pd.DataFrame(...)  # 2M rows
        >>> exporter.export_tables(large_df, filename="large_report.xlsx")
        >>> # Creates: large_report.xlsx with Sheet1, Sheet2
        >>> 
        >>> # Multiple DataFrames - one sheet per table
        >>> tables = [df1, df2, df3]
        >>> exporter.export_tables(tables, filename="multi_table.xlsx")
        >>> # Creates: multi_table.xlsx with Table1, Table2, Table3
        >>> 
        >>> # List with one DataFrame (common from HTML readers)
        >>> tables = reader.read_all("file.html")  # Returns [df]
        >>> exporter.export_tables(tables, filename="output.xlsx")
        >>> 
        >>> # CSV export (single table only)
        >>> exporter.export_tables(df, filename="data.csv", method="csv")
        
        Notes
        -----
        Excel limitations:
        - Maximum 1,048,576 rows per sheet
        - Maximum 16,384 columns
        - Recommended max_rows_per_sheet: 1,000,000 (default)
        
        Strategy:
        - Single table that fits: One file, one sheet
        - Single table that exceeds: One file, multiple sheets (Sheet1, Sheet2, ...)
        - Multiple small tables: One file, multiple sheets (Table1, Table2, ...)
        - Multiple large tables: One file, sheets named (Table1_part1, Table1_part2, Table2, ...)
        """
        # Normalize input: convert single DataFrame to list
        if isinstance(tables, pd.DataFrame):
            tables = [tables]
        
        if not tables:
            raise ValueError("No tables provided for export")
        
        # Ensure filename has proper extension
        if method == "excel" and not filename.endswith('.xlsx'):
            filename = f"{filename}.xlsx"
        elif method == "csv" and not filename.endswith('.csv'):
            filename = f"{filename}.csv"
        
        # CSV only supports single table
        if method == "csv":
            if len(tables) > 1:
                raise ValueError(
                    f"CSV export only supports single table. "
                    f"Received {len(tables)} tables. "
                    f"Use method='excel' for multiple tables."
                )
            self._export_csv(tables[0], filename=filename, **kwargs)
            return
        
        # Excel export logic
        if method == "excel":
            self._export_tables_to_excel(
                tables=tables,
                filename=filename,
                max_rows_per_sheet=max_rows_per_sheet,
                **kwargs
            )
        else:
            raise ValueError(
                f"Unknown export method: '{method}'. "
                f"Supported methods: 'excel', 'csv'"
            )

    def _export_tables_to_excel(
        self,
        tables: list,
        filename: str,
        max_rows_per_sheet: int = 1000000,
        **kwargs
    ) -> None:
        """
        Internal method to export multiple tables to Excel with intelligent sheet naming.
        
        Parameters
        ----------
        tables : list[pd.DataFrame]
            List of DataFrames to export.
        filename : str
            Output filename (should end with .xlsx).
        max_rows_per_sheet : int
            Maximum rows per sheet.
        **kwargs : dict
            Additional pandas arguments.
        """
        filepath = self.output_dir / filename
        
        if self.verbose:
            total_rows = sum(len(df) for df in tables)
            print(
                f"[INFO] Exporting {len(tables)} table(s) with {total_rows} total rows "
                f"to {filename}"
            )
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for table_idx, df in enumerate(tables, start=1):
                    # Determine if table needs splitting
                    if len(df) <= max_rows_per_sheet:
                        # Table fits in one sheet
                        if len(tables) == 1:
                            sheet_name = kwargs.pop("sheet_name", "Sheet1")
                        else:
                            sheet_name = f"Table{table_idx}"
                        
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        if self.verbose:
                            print(
                                f"[INFO] Created {sheet_name}: {df.shape[0]} rows, "
                                f"{df.shape[1]} columns"
                            )
                    else:
                        # Table needs splitting into multiple sheets
                        num_parts = (len(df) + max_rows_per_sheet - 1) // max_rows_per_sheet
                        
                        if self.verbose:
                            print(
                                f"[INFO] Table {table_idx} has {len(df)} rows, "
                                f"splitting into {num_parts} sheets"
                            )
                        
                        for part_idx in range(num_parts):
                            start_idx = part_idx * max_rows_per_sheet
                            end_idx = min((part_idx + 1) * max_rows_per_sheet, len(df))
                            part_df = df.iloc[start_idx:end_idx]
                            
                            # Sheet naming strategy
                            if len(tables) == 1:
                                # Single table split: Sheet1, Sheet2, ...
                                sheet_name = f"Sheet{part_idx + 1}"
                            else:
                                # Multiple tables with splits: Table1_part1, Table1_part2, ...
                                sheet_name = f"Table{table_idx}_part{part_idx + 1}"
                            
                            # Excel sheet name limit is 31 characters
                            sheet_name = sheet_name[:31]
                            
                            part_df.to_excel(writer, sheet_name=sheet_name, index=False)
                            
                            if self.verbose:
                                print(
                                    f"[INFO] Created {sheet_name}: {part_df.shape[0]} rows"
                                )
            
            if self.verbose:
                print(f"[INFO] Successfully exported to {filepath}")
        
        except Exception as e:
            raise Exception(f"Error exporting tables to Excel {filepath}: {e}") from e

    def _export_csv(self, df: pd.DataFrame, filename: str, **kwargs) -> None:
        """
        Export DataFrame to a single CSV file.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to export.
        filename : str
            Name of the output CSV file.
        **kwargs : dict
            Additional arguments passed to pandas.to_csv().
        
        Examples
        --------
        >>> exporter.export(df, method="csv", filename="data.csv")
        >>> exporter.export(df, method="csv", filename="data.csv", index=False)
        """
        if not filename:
            raise ValueError("filename is required for CSV export")
        
        filepath = self.output_dir / filename
        
        try:
            df.to_csv(filepath, index=False, **kwargs)
            
            if self.verbose:
                print(f"[INFO] Exported {df.shape[0]} rows to CSV: {filepath}")
        
        except Exception as e:
            raise Exception(f"Error exporting to CSV {filepath}: {e}") from e

    def _export_excel(self, df: pd.DataFrame, filename: str, **kwargs) -> None:
        """
        Export DataFrame to a single Excel file (single sheet).
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to export.
        filename : str
            Name of the output Excel file (.xlsx).
        **kwargs : dict
            Additional arguments passed to pandas.to_excel().
        
        Examples
        --------
        >>> exporter.export(df, method="excel", filename="report.xlsx")
        >>> exporter.export(df, method="excel", filename="report.xlsx", sheet_name="Data")
        """
        if not filename:
            raise ValueError("filename is required for Excel export")
        
        filepath = self.output_dir / filename
        
        try:
            # Default sheet name is "Sheet1" if not provided
            sheet_name = kwargs.pop("sheet_name", "Sheet1")
            
            df.to_excel(filepath, sheet_name=sheet_name, index=False, **kwargs)
            
            if self.verbose:
                print(f"[INFO] Exported {df.shape[0]} rows to Excel: {filepath}")
        
        except Exception as e:
            raise Exception(f"Error exporting to Excel {filepath}: {e}") from e

    def _export_excel_parts(
        self, 
        df: pd.DataFrame, 
        filename_prefix: str,
        max_rows: int = 1000000,
        **kwargs
    ) -> None:
        """
        Export DataFrame to multiple Excel files (split by max_rows).
        
        Useful when DataFrame exceeds Excel's row limit (1,048,576 rows).
        Creates multiple files with pattern: {prefix}_part1.xlsx, _part2.xlsx, etc.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to export.
        filename_prefix : str
            Prefix for output files (e.g., "report" creates "report_part1.xlsx").
        max_rows : int, default 1000000
            Maximum number of rows per Excel file.
        **kwargs : dict
            Additional arguments passed to pandas.to_excel().
        
        Examples
        --------
        >>> exporter.export(
        ...     df, 
        ...     method="excel_parts", 
        ...     filename_prefix="large_report", 
        ...     max_rows=5000
        ... )
        # Creates: large_report_part1.xlsx, large_report_part2.xlsx, etc.
        """
        if not filename_prefix:
            raise ValueError("filename_prefix is required for excel_parts export")
        
        try:
            # Split DataFrame into chunks
            num_parts = (len(df) + max_rows - 1) // max_rows
            
            if self.verbose:
                print(
                    f"[INFO] Exporting {df.shape[0]} rows into {num_parts} Excel files"
                )
            
            sheet_name = kwargs.pop("sheet_name", "Sheet1")
            
            for i in range(num_parts):
                start_idx = i * max_rows
                end_idx = min((i + 1) * max_rows, len(df))
                part_df = df.iloc[start_idx:end_idx]
                
                # Create filename with part number (1-indexed)
                filename = f"{filename_prefix}_part{i + 1}.xlsx"
                filepath = self.output_dir / filename
                
                part_df.to_excel(
                    filepath, 
                    sheet_name=sheet_name, 
                    index=False, 
                    **kwargs
                )
                
                if self.verbose:
                    print(
                        f"[INFO] Created part {i + 1}/{num_parts}: "
                        f"{filename} ({part_df.shape[0]} rows)"
                    )
        
        except Exception as e:
            raise Exception(f"Error exporting excel_parts: {e}") from e

    def _export_excel_sheets(
        self, 
        df: pd.DataFrame, 
        filename: str,
        max_rows: int = 1000000,
        **kwargs
    ) -> None:
        """
        Export DataFrame to single Excel file with multiple sheets (split by max_rows).
        
        Creates a single Excel file with multiple worksheets, each containing
        up to max_rows. Useful for keeping all data in one file while staying
        within Excel's limitations.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to export.
        filename : str
            Name of the output Excel file (.xlsx).
        max_rows : int, default 1000000
            Maximum number of rows per sheet.
        **kwargs : dict
            Additional arguments passed to pandas.ExcelWriter().
        
        Examples
        --------
        >>> exporter.export(
        ...     df, 
        ...     method="excel_sheets", 
        ...     filename="report.xlsx", 
        ...     max_rows=5000
        ... )
        # Creates: report.xlsx with Sheet1, Sheet2, etc.
        """
        if not filename:
            raise ValueError("filename is required for excel_sheets export")
        
        try:
            filepath = self.output_dir / filename
            
            # Calculate number of sheets needed
            num_sheets = (len(df) + max_rows - 1) // max_rows
            
            if self.verbose:
                print(
                    f"[INFO] Exporting {df.shape[0]} rows into {num_sheets} sheets "
                    f"in {filename}"
                )
            
            # Use ExcelWriter to write multiple sheets
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for i in range(num_sheets):
                    start_idx = i * max_rows
                    end_idx = min((i + 1) * max_rows, len(df))
                    sheet_df = df.iloc[start_idx:end_idx]
                    
                    # Sheet names: Sheet1, Sheet2, etc. (Excel limit: 31 chars)
                    sheet_name = f"Sheet{i + 1}"
                    
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    if self.verbose:
                        print(
                            f"[INFO] Created {sheet_name}: "
                            f"{sheet_df.shape[0]} rows"
                        )
            
            if self.verbose:
                print(f"[INFO] Successfully exported to {filepath}")
        
        except Exception as e:
            raise Exception(f"Error exporting excel_sheets: {e}") from e

    def get_output_dir(self) -> Path:
        """
        Get the output directory path.
        
        Returns
        -------
        Path
            Path object pointing to the output directory.
        """
        return self.output_dir

    def set_output_dir(self, output_dir: str) -> None:
        """
        Set a new output directory.
        
        Parameters
        ----------
        output_dir : str
            New output directory path.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.verbose:
            print(f"[INFO] Output directory set to: {self.output_dir}")
