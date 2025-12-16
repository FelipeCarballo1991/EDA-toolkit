import pandas as pd
from pandas_toolkit.io.base import DelimitedTextReader
from pandas_toolkit.io.exporter import FileExporter


class CSVReader(DelimitedTextReader):
    """
    CSV file reader with automatic encoding and delimiter detection.
    
    Inherits all functionality from DelimitedTextReader including:
    - Automatic encoding detection
    - Automatic delimiter detection
    - Data normalization (column names and cell values)
    - Export to multiple formats
    
    Examples
    --------
    >>> reader = CSVReader(verbose=True, output_dir="exports")
    >>> df = reader.read("data.csv")
    >>> df_normalized = reader.read("data.csv", normalize=True, normalize_columns=True)
    >>> reader.export(df, method="excel", filename="output.xlsx")
    """
    
    def __init__(
        self, 
        encodings=None, 
        delimiters=None, 
        verbose=False,
        capture_bad_lines=False,
        output_dir=".",
        exporter: FileExporter = None
    ):
        """
        Initialize the CSV reader.
        
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
            Custom FileExporter instance. If None, creates one with output_dir.
        
        Examples
        --------
        >>> reader = CSVReader(verbose=True, output_dir="exports")
        >>> df = reader.read("data.csv")
        """
        super().__init__(
            encodings=encodings,
            delimiters=delimiters,
            verbose=verbose,
            capture_bad_lines=capture_bad_lines,
            output_dir=output_dir,
            exporter=exporter or FileExporter(output_dir=output_dir, verbose=verbose)
        )