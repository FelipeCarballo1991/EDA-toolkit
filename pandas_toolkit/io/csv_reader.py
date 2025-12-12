# pandas_toolkit/io/readers.py
from pandas_toolkit.io.interfaces import DelimitedTextReader
from pandas_toolkit.io.exporter import FileExporter


class CSVReader(DelimitedTextReader):
    def __init__(self, encodings=None, 
                 delimiters=None, 
                 verbose=False,
                 capture_bad_lines=False,
                 output_dir=".",  # Nuevo parámetro
                 exporter: FileExporter = None):
        
        super().__init__(
            encodings=encodings,
            delimiters=delimiters,
            verbose=verbose,
            capture_bad_lines=capture_bad_lines
        )

        # Usa el exporter que pasen o crea uno con el output_dir especificado
        self.exporter = exporter or FileExporter(output_dir=output_dir, verbose=verbose)

    def normalize(self, df):
        return super().normalize(df)

    def read_and_normalize(self, filepath, **kwargs):
        df = self.read(filepath, **kwargs)
        return self.normalize(df)
    
    def export(self, df, method="excel", **kwargs):
        """Shortcut to export using the configured exporter."""
        if method == "excel":
            self.exporter.to_excel(df, **kwargs)
        elif method == "csv":
            self.exporter.to_csv(df, **kwargs)
        elif method == "excel_parts":
            self.exporter.to_excel_multiple_parts(df, **kwargs)
        elif method == "excel_sheets":
            self.exporter.to_excel_multiple_sheets_from_df(df, **kwargs)
        else:
            raise ValueError(f"Unknown export method: {method}")
