# pandas_toolkit/io/exporters.py
import pandas as pd
import os
from typing import Dict, List

class FileExporter:
    def __init__(self, output_dir: str = ".", verbose: bool = False):
        self.output_dir = output_dir
        self.verbose = verbose
        os.makedirs(self.output_dir, exist_ok=True)

    def _log(self, msg: str):
        if self.verbose:
            print(f"[EXPORT] {msg}")

    def to_excel(self, df: pd.DataFrame, filename: str, **kwargs):
        """Export a DataFrame to a single-sheet Excel file."""
        path = os.path.join(self.output_dir, filename)
        df.to_excel(path, index=False, **kwargs)
        self._log(f"Saved single-sheet Excel to: {path}")

    def to_excel_multiple_parts(self, df: pd.DataFrame, filename_prefix: str, max_rows: int = 1000000, **kwargs):
        """
        Split a DataFrame into multiple Excel files with up to max_rows per file.
        Useful for Excel's row limit or large files.
        """
        total_rows = len(df)
        num_parts = (total_rows // max_rows) + int(total_rows % max_rows > 0)
        for i in range(num_parts):
            part_df = df.iloc[i * max_rows: (i + 1) * max_rows]
            part_filename = f"{filename_prefix}_part{i+1}.xlsx"
            self.to_excel(part_df, part_filename, **kwargs)

    def to_excel_multiple_sheets(self, dfs: Dict[str, pd.DataFrame], filename: str, **kwargs):
        """
        Export multiple DataFrames into one Excel file using sheet names as keys.
        """
        path = os.path.join(self.output_dir, filename)
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False, **kwargs)
        self._log(f"Saved multi-sheet Excel to: {path}")

    def to_csv(self, df: pd.DataFrame, filename: str, **kwargs):
        """Export a DataFrame to a CSV file."""
        path = os.path.join(self.output_dir, filename)
        df.to_csv(path, index=False, **kwargs)
        self._log(f"Saved CSV to: {path}")
