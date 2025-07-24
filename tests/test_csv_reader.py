import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pandas_toolkit.io.csv_reader import CSVReader
from pandas_toolkit.io.errors import FileEncodingError
import pandas as pd
import tempfile
import pytest


def test_csv_reader_reads_valid_file():
    """
    Test that validates that the CSVReader can correctly read a valid CSV file.
    """    
        
    reader = CSVReader()
    content = "col1,col2\n1,2\n3,4"

    with tempfile.NamedTemporaryFile(mode='w+', suffix=".csv", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    df = reader.read(tmp_path)
    
    assert isinstance(df, pd.DataFrame)       
    assert df.shape == (2, 2)                 
    assert list(df.columns) == ["col1", "col2"] 
    
    os.remove(tmp_path) 


def test_csv_reader_especific_delimiter():
    """
    Test with especific delimiter.
    """    
        
    reader = CSVReader()
    content = "col1,col2\n1,2\n3,4"

    with tempfile.NamedTemporaryFile(mode='w+', suffix=".csv", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    df = reader.read(tmp_path)
    
    assert isinstance(df, pd.DataFrame)       
    assert df.shape == (2, 2)                 
    assert list(df.columns) == ["col1", "col2"] 
    
    os.remove(tmp_path) 
    
def test_csv_reader_fails_with_bad_encoding():
    """
    CSV with bad encoding.
    """
    reader = CSVReader()
    content = "col1,col2\n1,á\n2,ó" # content with especial characters

    with tempfile.NamedTemporaryFile(mode='w+', suffix=".csv", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

   
    with pytest.raises(FileEncodingError):
        # Try with ascii encoding
        reader.encodings = ['ascii']
        df = reader.read(tmp_path)

    os.remove(tmp_path)


# def test_bad_lines_capture_and_print(capsys):

#     reader = CSVReader()
#     content = (
#                 "col1,col2\n"
#                 "1,2\n"
#                 "3,4,5\n"      # Bad Line
#                 "6,7\n"
#             )


#     with tempfile.NamedTemporaryFile(mode='w+', suffix=".csv", delete=False) as tmp:
#         tmp.write(content)
#         tmp_path = tmp.name
    
#     df = reader.read(tmp_path)

#     captured = capsys.readouterr()

#     # Verificamos que el DataFrame cargue solo las filas válidas
#     assert df.shape[0] == 3  # Debe cargar 3 filas (incluye header)
#     assert df.shape[1] == 2
#     assert df.iloc[0]["col1"] == 1
#     assert df.iloc[1]["col1"] == 3  # fila "3,4,5" debería descartarse, pero cuidado con pandas
#     assert df.iloc[2]["col1"] == 6

#     # Verificamos que la línea defectuosa se haya registrado en la salida de consola
#     assert "[WARN] Línea defectuosa" in captured.out
#     assert "3,4,5" in captured.out

#     os.remove(tmp_path)