# pandas_toolkit/io/excel_reader.py
from pandas_toolkit.io.interfaces import FileReader
from pandas_toolkit.io.exporter import FileExporter
import pandas as pd
from pathlib import Path


ENGINE_BY_EXTENSION = {
    ".xlsx": "openpyxl",
    ".xlsm": "openpyxl",
    ".xls": "xlrd",
    ".ods": "odf",
    ".xlsb": "pyxlsb"
}

class ExcelReader(FileReader):

    def detect_engine_from_extension(filepath) -> str:
        ext = Path(filepath).suffix.lower()
        return ENGINE_BY_EXTENSION.get(ext, None)
    

    def read(self,filepath,**kwargs) -> pd.DataFrame:


        eng = self.detect_engine_from_extension(filepath)
        df = pd.read_excel(filepath,engine=eng)

        return df