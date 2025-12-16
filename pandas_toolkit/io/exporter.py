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
        max_rows: int = 10000,
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
        max_rows : int, default 10000
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
        max_rows: int = 10000,
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
        max_rows : int, default 10000
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
