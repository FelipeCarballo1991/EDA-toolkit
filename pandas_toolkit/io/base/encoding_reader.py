from abc import abstractmethod
import pandas as pd
from pandas_toolkit.io.errors import FileEncodingError
from pandas_toolkit.io.base.reader import FileReader
from pandas_toolkit.io.base.constants import COMMON_ENCODINGS


class FileReaderEncoding(FileReader):
    """
    Base class for readers that handle files with multiple possible encodings.
    
    Tries different encodings sequentially until one successfully reads the file.
    Tracks which encoding was successful.
    """
    
    def __init__(self, encodings=None, output_dir=".", verbose=False, exporter=None):
        """
        Initialize the reader with a list of encodings to try.
        
        Parameters
        ----------
        encodings : list, optional
            List of encodings to attempt. Defaults to COMMON_ENCODINGS.
        output_dir : str, default "."
            Directory for exporting files.
        verbose : bool, default False
            Enable verbose output.
        exporter : FileExporter, optional
            Custom FileExporter instance.
        """
        super().__init__(output_dir=output_dir, verbose=verbose, exporter=exporter)
        self.encodings = encodings or COMMON_ENCODINGS
        self.success_encoding = None

    @abstractmethod
    def _read_with_encoding(
        self, 
        filepath: str, 
        encoding: str, 
        **kwargs
    ) -> pd.DataFrame:
        """
        Abstract method to read a file with a specific encoding.
        Must be implemented by subclasses.
        
        Parameters
        ----------
        filepath : str
            Path to the file.
        encoding : str
            The encoding to use.
        **kwargs : dict
            Additional arguments.
        
        Returns
        -------
        pd.DataFrame
            The loaded DataFrame.
        
        Raises
        ------
        UnicodeDecodeError
            If the encoding doesn't match the file's actual encoding.
        """
        pass

    def _read(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Try reading the file with each encoding until one succeeds.
        
        Parameters
        ----------
        filepath : str
            Path to the file to read.
        **kwargs : dict
            Additional arguments passed to _read_with_encoding().
        
        Returns
        -------
        pd.DataFrame
            The successfully loaded DataFrame.
        
        Raises
        ------
        FileEncodingError
            If no encoding in the list can successfully read the file.
        """
        for enc in self.encodings:
            try:
                return self._read_with_encoding(filepath, enc, **kwargs)
            except UnicodeDecodeError:
                continue

        raise FileEncodingError(
            f"Could not read {filepath} with any of the following encodings: {self.encodings}"
        )