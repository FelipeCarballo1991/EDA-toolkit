import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pandas_toolkit.io.interfaces import NormalizeMixin
import pandas as pd
import numpy as np

def test_normalize_df():
    """
    Test that validate all normalization from NormalizeMixin
    """    

    df = pd.DataFrame({
    "nombre": [" Felipe ", "MARÍA", None,None],
    "edad": [30, 25, 40, np.nan],
    "ciudad": [" caba ", "rosario", "",None],
    "vacía": [None, None, None, None]
    })

    normalizador = NormalizeMixin()
    df_norm = normalizador.normalize(df, convert_case="lower")

    assert isinstance(df_norm, pd.DataFrame)       
    assert df_norm.shape == (3,5)        

    assert list(df_norm.columns) == ["nombre", "edad","ciudad","nombre_norm","ciudad_norm"] 

    
    assert df_norm.loc[0, "nombre_norm"] == "felipe"     # String Capitalize with spaces
    assert df_norm.loc[1, "nombre_norm"] == "maría"      # Upper String
    assert pd.isna(df_norm.loc[2, "nombre"])        # None value

    assert df_norm.loc[0, "ciudad_norm"] == "caba"       # Lower string with spaces
    assert df_norm.loc[2, "ciudad_norm"] == None           # Empty string = None value

    assert df_norm["edad"].tolist() == [30, 25, 40]
