import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# tests/test_imports.py

def test_imports():
    try:
        import pandas_toolkit
        from pandas_toolkit.io import CSVReader
    except ImportError as e:
        assert False, f"Falló la importación: {e}"
