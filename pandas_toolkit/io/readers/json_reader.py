import pandas as pd
from pathlib import Path
from pandas_toolkit.io.base import FileReader
from pandas_toolkit.io.exporter import FileExporter


class JSONReader(FileReader):
    """
    JSON file reader supporting multiple JSON formats.
    
    Features:
    - Read standard JSON files
    - Read JSONL (JSON Lines) format
    - Configurable orientation (records, columns, index, split)
    - Data normalization
    - Export to multiple formats
    
    Examples
    --------
    >>> reader = JSONReader()
    >>> df = reader.read("data.json")
    >>> df = reader.read("data.jsonl")  # JSON Lines format
    >>> files = reader.read_multiple_files("data_folder/")
    """
    
    def __init__(
        self,
        output_dir=".",
        verbose=False,
        exporter: FileExporter = None
    ):
        """
        Initialize the JSON reader.
        
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

    def _read(self, filepath: str, orient='records', **kwargs) -> pd.DataFrame:
        """
        Read a JSON file.
        
        Parameters
        ----------
        filepath : str
            Path to the JSON or JSONL file.
        orient : str, default 'records'
            JSON orientation: 'records', 'columns', 'index', 'split', 'table'.
            - 'records': List of dictionaries (typical format)
            - 'columns': Dictionary with column names as keys
            - 'index': Dictionary with index as keys
            - 'split': Dictionary with 'columns' and 'data' keys
            - 'table': Table-schema format
        **kwargs : dict
            Additional pandas read_json arguments.
        
        Returns
        -------
        pd.DataFrame
            The loaded DataFrame.
        
        Examples
        --------
        >>> reader = JSONReader()
        >>> df = reader.read("data.json")
        >>> df = reader.read("data.json", orient="columns")
        >>> df = reader.read("data.jsonl", lines=True)
        """
        if self.verbose:
            print(f"[INFO] Reading JSON file: {filepath}, orient: {orient}")
        
        try:
            # Detect JSONL format
            is_jsonl = filepath.endswith('.jsonl') or kwargs.get('lines', False)
            
            if is_jsonl and 'lines' not in kwargs:
                kwargs['lines'] = True
                if self.verbose:
                    print(f"[INFO] Detected JSONL format, reading as lines")
            
            df = pd.read_json(filepath, orient=orient, **kwargs)
            
            if self.verbose:
                print(f"[INFO] Successfully loaded {df.shape[0]} rows, {df.shape[1]} columns")
            
            return df
        
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {filepath}") from e
        except Exception as e:
            raise Exception(f"Error reading JSON file {filepath}: {e}") from e

    def read_lines(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Read JSONL (JSON Lines) format file.
        
        Each line is a separate JSON object, useful for streaming data.
        
        Parameters
        ----------
        filepath : str
            Path to the JSONL file.
        **kwargs : dict
            Additional pandas read_json arguments.
        
        Returns
        -------
        pd.DataFrame
            The loaded DataFrame.
        
        Examples
        --------
        >>> reader = JSONReader()
        >>> df = reader.read_lines("streaming_data.jsonl")
        """
        if self.verbose:
            print(f"[INFO] Reading JSONL file: {filepath}")
        
        return self.read(filepath, lines=True, **kwargs)

    def _get_file_extensions(self) -> list:
        """Get file extensions for JSON files."""
        return ['.json', '.JSON', '.jsonl', '.JSONL']