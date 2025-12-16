import pandas as pd
from pandas_toolkit.io.base.encoding_reader import FileReaderEncoding
from pandas_toolkit.io.base.constants import COMMON_DELIMITERS
from pandas_toolkit.io.exporter import FileExporter


class DelimitedTextReader(FileReaderEncoding):
    """
    Reader for delimited text files (CSV, TSV, etc.) with automatic encoding and delimiter detection.
    
    Tries different encoding and delimiter combinations until a valid DataFrame is produced.
    """
    
    def __init__(
        self, 
        encodings=None, 
        delimiters=None, 
        verbose=False, 
        capture_bad_lines=False,
        output_dir=".",
        exporter=None
    ):
        """
        Initialize the delimited text reader.
        
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
            Custom FileExporter instance.
        """
        super().__init__(
            encodings=encodings,
            output_dir=output_dir,
            verbose=verbose,
            exporter=exporter
        )
        
        self.delimiters = delimiters or COMMON_DELIMITERS
        self.success_delimiter = None
        self.capture_bad_lines = capture_bad_lines
        self.bad_lines = []

    def _read_with_encoding(
        self, 
        filepath: str, 
        encoding: str, 
        **kwargs
    ) -> pd.DataFrame:
        """
        Read delimited text file with a specific encoding and delimiter detection.
        
        This method tries all delimiters until finding one that produces a valid DataFrame.
        Prefers delimiters that produce more columns (better data structure).
        
        Parameters
        ----------
        filepath : str
            Path to the delimited text file.
        encoding : str
            The encoding to attempt.
        **kwargs : dict
            Additional pandas read_csv arguments (skiprows, nrows, dtype, etc.).
        
        Returns
        -------
        pd.DataFrame
            The loaded DataFrame.
        
        Raises
        ------
        UnicodeDecodeError
            If the encoding doesn't match the file's actual encoding.
        Exception
            If no valid delimiter is found or file reading fails.
        """
        def capture_bad_line(bad_line):
            """Callback to capture bad lines if enabled."""
            self.bad_lines.append(bad_line)
            if self.verbose:
                print(f"[WARNING] Bad line: {bad_line}")

        best_df = None
        best_delim = None
        best_col_count = 0
        error_original = None
        encoding_error = None

        for delim in self.delimiters:
            try:
                if self.verbose:
                    print(f"[DEBUG] Trying encoding='{encoding}', delimiter='{repr(delim)}'")

                if self.capture_bad_lines:
                    if self.verbose:
                        print(f"[DEBUG] Capturing bad lines (may take longer).")

                    df = pd.read_csv(
                        filepath,
                        encoding=encoding,
                        delimiter=delim,
                        engine="python",
                        on_bad_lines=capture_bad_line,
                        **kwargs
                    )
                else:
                    df = pd.read_csv(
                        filepath,
                        encoding=encoding,
                        delimiter=delim,
                        on_bad_lines="warn",
                        **kwargs
                    )

                # Keep track of the best result (most columns)
                if df.shape[0] > 0 and df.shape[1] > best_col_count:
                    best_df = df
                    best_delim = delim
                    best_col_count = df.shape[1]
                    
                    if self.verbose:
                        print(
                            f"[DEBUG] Better result with delimiter='{repr(delim)}': "
                            f"{df.shape[0]} rows, {df.shape[1]} columns"
                        )
                
                # Early exit if we find 2+ columns (likely correct)
                if df.shape[1] >= 2:
                    self.success_encoding = encoding
                    self.success_delimiter = delim
                    if self.verbose:
                        print(
                            f"[INFO] Success! encoding='{encoding}', delimiter='{repr(delim)}'"
                        )
                        print(
                            f"[INFO] Loaded {df.shape[0]} rows and {df.shape[1]} columns"
                        )
                    return df
            
            except FileNotFoundError as fnf_error:
                raise FileNotFoundError(f"File not found: {filepath}") from fnf_error

            except UnicodeDecodeError as ude:
                encoding_error = ude
                if self.verbose:
                    print(
                        f"[DEBUG] Encoding error with encoding='{encoding}', delimiter='{repr(delim)}'"
                    )
                continue

            except (pd.errors.ParserError, ValueError) as e:
                error_original = e
                if self.verbose:
                    print(
                        f"[DEBUG] Failed with encoding='{encoding}', delimiter='{repr(delim)}'"
                    )
                continue

        # If we found any valid result, return the best one
        if best_df is not None:
            self.success_encoding = encoding
            self.success_delimiter = best_delim
            if self.verbose:
                print(
                    f"[INFO] Success (best match)! encoding='{encoding}', delimiter='{repr(best_delim)}'"
                )
                print(
                    f"[INFO] Loaded {best_df.shape[0]} rows and {best_df.shape[1]} columns"
                )
            return best_df

        # If we got a UnicodeDecodeError and nothing worked, re-raise it
        if encoding_error is not None:
            raise encoding_error

        # If all attempts failed, raise error
        raise Exception(
            f"Could not read {filepath} with any delimiter combination. "
            f"Last error: {error_original}"
        )

    def _get_file_extensions(self) -> list:
        """Get file extensions for delimited text files."""
        return ['.csv', '.CSV', '.tsv', '.TSV', '.txt', '.TXT', '.dat', '.DAT']