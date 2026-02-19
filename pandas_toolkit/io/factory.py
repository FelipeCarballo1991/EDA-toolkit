from pathlib import Path
from pandas_toolkit.io.readers import CSVReader, TSVReader, PipeReader, ExcelReader, JSONReader, HTMLReader
from pandas_toolkit.io.base import FileReader


class ReaderFactory:
    """
    Factory for creating appropriate file readers based on file extension.
    
    This factory simplifies reader selection by automatically choosing the
    correct reader class based on the file's extension.
    
    Examples
    --------
    >>> factory = ReaderFactory()
    >>> reader = factory.create_reader("data.csv")
    >>> df = reader.read("data.csv")
    
    >>> reader = factory.create_reader("data.xlsx")
    >>> df = reader.read("data.xlsx")
    """
    
    # Mapping of file extensions to reader classes
    READER_MAP = {
        ".csv": CSVReader,
        ".tsv": TSVReader,
        ".txt": CSVReader,  # Default to CSV for .txt
        ".dat": CSVReader,  # Default to CSV for .dat
        ".xlsx": ExcelReader,
        ".xls": ExcelReader,
        ".json": JSONReader,
        ".jsonl": JSONReader,
        ".pipe": PipeReader,
        ".html": HTMLReader,
        ".htm": HTMLReader,
    }
    
    @classmethod
    def create_reader(
        cls, 
        filepath: str, 
        output_dir: str = ".",
        verbose: bool = False,
        **kwargs
    ) -> FileReader:
        """
        Create a reader instance based on file extension.
        
        Parameters
        ----------
        filepath : str
            Path to the file.
        output_dir : str, default "."
            Output directory for exports.
        verbose : bool, default False
            Enable verbose output.
        **kwargs : dict
            Additional arguments passed to the reader (encoding, delimiters, etc.).
        
        Returns
        -------
        FileReader
            Appropriate reader instance for the file type.
        
        Raises
        ------
        ValueError
            If file extension is not supported.
        
        Examples
        --------
        >>> factory = ReaderFactory()
        >>> reader = factory.create_reader("data.csv", verbose=True)
        >>> df = reader.read("data.csv")
        
        >>> reader = factory.create_reader("report.xlsx")
        >>> df = reader.read("report.xlsx")
        """
        filepath = Path(filepath)
        extension = filepath.suffix.lower()
        
        if extension not in cls.READER_MAP:
            supported = ", ".join(cls.READER_MAP.keys())
            raise ValueError(
                f"Unsupported file extension: {extension}\n"
                f"Supported extensions: {supported}"
            )
        
        reader_class = cls.READER_MAP[extension]
        return reader_class(output_dir=output_dir, verbose=verbose, **kwargs)
    
    @classmethod
    def get_supported_extensions(cls) -> list:
        """
        Get list of supported file extensions.
        
        Returns
        -------
        list
            List of supported file extensions (e.g., ['.csv', '.xlsx', '.json']).
        
        Examples
        --------
        >>> factory = ReaderFactory()
        >>> extensions = factory.get_supported_extensions()
        >>> print(extensions)
        ['.csv', '.tsv', '.xlsx', '.xls', '.json', '.jsonl', '.pipe']
        """
        return sorted(cls.READER_MAP.keys())
    
    @classmethod
    def register_reader(cls, extension: str, reader_class):
        """
        Register a custom reader for a file extension.
        
        Parameters
        ----------
        extension : str
            File extension (e.g., '.parquet').
        reader_class : type
            Reader class (must inherit from FileReader).
        
        Examples
        --------
        >>> from pandas_toolkit.io.parquet_reader import ParquetReader
        >>> factory = ReaderFactory()
        >>> factory.register_reader(".parquet", ParquetReader)
        >>> reader = factory.create_reader("data.parquet")
        """
        if not issubclass(reader_class, FileReader):
            raise TypeError(f"{reader_class} must inherit from FileReader")
        
        cls.READER_MAP[extension.lower()] = reader_class