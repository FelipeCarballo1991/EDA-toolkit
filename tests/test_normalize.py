import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pandas_toolkit.io.interfaces import NormalizeMixin
import pandas as pd


def test_normalize_df():
    """
    Test that validate all normalization from NormalizeMixin
    """    

    df = pd.DataFrame({
    "nombre": [" Felipe ", "MARÍA", None],
    "edad": [30, 25, 40],
    "ciudad": [" caba ", "rosario", ""],
    "vacía": [None, None, None]
    })

    normalizador = NormalizeMixin()
    df_norm = normalizador.normalize(df, convert_case="lower")

    assert isinstance(df_norm, pd.DataFrame)       
    assert df_norm.shape == (3,3)                 
    assert list(df_norm.columns) == ["nombre", "edad","ciudad"] 

    
    assert df_norm.loc[0, "nombre"] == "felipe"     # String Capitalize with spaces
    assert df_norm.loc[1, "nombre"] == "maría"      # Upper String
    assert pd.isna(df_norm.loc[2, "nombre"])        # None value

    assert df_norm.loc[0, "ciudad"] == "caba"       # Lower string with spaces
    assert df_norm.loc[2, "ciudad"] == None           # Empty string = None value

    assert df_norm["edad"].tolist() == [30, 25, 40]
