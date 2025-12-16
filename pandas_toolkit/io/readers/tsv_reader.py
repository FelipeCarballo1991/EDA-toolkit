import pandas as pd
from pandas_toolkit.io.base import DelimitedTextReader
from pandas_toolkit.io.exporter import FileExporter


class TSVReader(DelimitedTextReader):
    """
    Tab-Separated Values (TSV) file reader.
    
    Extends DelimitedTextReader with tab as the primary delimiter.
    Still supports automatic encoding detection and delimiter fallback.
    
    Examples
    --------
    >>> reader = TSVReader()
    >>> df = reader.read("data.tsv")
    >>> df = reader.read("data.tsv", normalize=True, normalize_columns=True)
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
        Initialize the TSV reader.
        
        TSV reader prioritizes tab delimiter but can fallback to others.
        
        Parameters
        ----------
        encodings : list, optional
            List of encodings to try. Defaults to COMMON_ENCODINGS.
        delimiters : list, optional
            List of delimiters to try. Defaults to ["\t", ",", ";", "|"].
        verbose : bool, default False
            Enable verbose output for debugging.
        capture_bad_lines : bool, default False
            Capture malformed lines for inspection.
        output_dir : str, default "."
            Output directory for exported files.
        exporter : FileExporter, optional
            Custom FileExporter instance.
        """
        # Default delimiters: tab first, then fallback options
        if delimiters is None:
            delimiters = ["\t", ",", ";", "|"]
        
        super().__init__(
            encodings=encodings,
            delimiters=delimiters,
            verbose=verbose,
            capture_bad_lines=capture_bad_lines,
            output_dir=output_dir,
            exporter=exporter or FileExporter(output_dir=output_dir, verbose=verbose)
        )