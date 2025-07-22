import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pandas_toolkit.io.csv_reader import CSVReader
import pandas as pd
import tempfile
import os


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
    
