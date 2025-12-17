import pandas as pd
import pytest
from pathlib import Path
from pandas_toolkit.io import CSVReader
from pandas_toolkit.io.base.reader import FileReader
import warnings


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def csv_with_leading_empty_rows(tmp_path):
    """
    Create a CSV file with empty rows at the beginning.
    
    File structure:
    [Empty row]
    [Empty row]
    [Empty row]
    Name,Age,City
    John,30,NYC
    Jane,25,LA
    """
    # Crear el archivo con líneas realmente vacías
    filepath = tmp_path / "leading_empty.csv"
    with open(filepath, 'w', newline='') as f:
        f.write("\n")  # Línea completamente vacía
        f.write("\n")  # Línea completamente vacía
        f.write("\n")  # Línea completamente vacía
        f.write("Name,Age,City\n")
        f.write("John,30,NYC\n")
        f.write("Jane,25,LA\n")
    
    return filepath


@pytest.fixture
def csv_with_trailing_empty_rows(tmp_path):
    """
    Create a CSV file with empty rows at the end.
    """
    filepath = tmp_path / "trailing_empty.csv"
    with open(filepath, 'w', newline='') as f:
        f.write("Name,Age,City\n")
        f.write("John,30,NYC\n")
        f.write("Jane,25,LA\n")
        f.write("\n")  # Línea completamente vacía
        f.write("\n")  # Línea completamente vacía
    
    return filepath


@pytest.fixture
def csv_with_both_empty_rows(tmp_path):
    """
    Create a CSV file with empty rows at beginning and end.
    """
    filepath = tmp_path / "both_empty.csv"
    with open(filepath, 'w', newline='') as f:
        f.write("\n")
        f.write("\n")
        f.write("Name,Age,City\n")
        f.write("John,30,NYC\n")
        f.write("Jane,25,LA\n")
        f.write("\n")
        f.write("\n")
    
    return filepath


@pytest.fixture
def csv_with_metadata(tmp_path):
    """
    Create a CSV file with metadata rows before data.
    """
    filepath = tmp_path / "with_metadata.csv"
    with open(filepath, 'w', newline='') as f:
        f.write("Report Title\n")
        f.write("Generated: 2025-01-01\n")
        f.write("\n")  # Línea vacía
        f.write("Name,Age,City\n")
        f.write("John,30,NYC\n")
        f.write("Jane,25,LA\n")
    
    return filepath


# =====================================================================
# Test: Skip Leading Empty Rows (Static Method)
# =====================================================================

def test_skip_leading_empty_rows_basic():
    """
    Test basic leading empty rows removal.
    
    Verifies that:
    - Empty rows at beginning are removed
    - Data rows are preserved
    - DataFrame is correctly reset
    """
    df = pd.DataFrame({
        'A': [None, None, None, 1, 2],
        'B': [None, None, None, 3, 4]
    })
    
    result = FileReader.skip_leading_empty_rows(df)
    
    assert result.shape == (2, 2)
    assert result.iloc[0]['A'] == 1
    assert result.iloc[0]['B'] == 3


def test_skip_leading_empty_rows_with_strings():
    """
    Test leading empty rows with empty strings.
    
    Empty strings should be treated as empty values.
    """
    df = pd.DataFrame({
        'A': ['', '', '', 'John', 'Jane'],
        'B': ['', '', '', '30', '25']
    })
    
    result = FileReader.skip_leading_empty_rows(df)
    
    assert result.shape == (2, 2)
    assert result.iloc[0]['A'] == 'John'


def test_skip_leading_empty_rows_empty_dataframe():
    """
    Test with completely empty DataFrame.
    """
    df = pd.DataFrame({
        'A': [None, None, None],
        'B': [None, None, None]
    })
    
    result = FileReader.skip_leading_empty_rows(df)
    
    assert result.empty
    assert isinstance(result, pd.DataFrame)


def test_skip_leading_empty_rows_no_empty_rows():
    """
    Test when there are no leading empty rows.
    
    DataFrame should be unchanged (except index reset).
    """
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })
    
    result = FileReader.skip_leading_empty_rows(df)
    
    assert result.shape == (3, 2)
    assert result.iloc[0]['A'] == 1


def test_skip_leading_empty_rows_partial_empty():
    """
    Test with partially empty rows (some columns have data).
    
    Rows with ANY data should not be removed.
    """
    df = pd.DataFrame({
        'A': [None, 'X', None, 'John'],
        'B': [None, None, None, '30']
    })
    
    result = FileReader.skip_leading_empty_rows(df)
    
    # Row with 'X' is not empty, so starts there
    assert result.shape == (3, 2)
    assert result.iloc[0]['A'] == 'X'


# =====================================================================
# Test: Skip Trailing Empty Rows (Static Method)
# =====================================================================

def test_skip_trailing_empty_rows_basic():
    """
    Test basic trailing empty rows removal.
    """
    df = pd.DataFrame({
        'A': [1, 2, None, None],
        'B': [3, 4, None, None]
    })
    
    result = FileReader.skip_trailing_empty_rows(df)
    
    assert result.shape == (2, 2)
    assert result.iloc[-1]['A'] == 2


def test_skip_trailing_empty_rows_with_strings():
    """
    Test trailing empty rows with empty strings.
    """
    df = pd.DataFrame({
        'A': ['John', 'Jane', '', ''],
        'B': ['30', '25', '', '']
    })
    
    result = FileReader.skip_trailing_empty_rows(df)
    
    assert result.shape == (2, 2)
    assert result.iloc[-1]['A'] == 'Jane'


def test_skip_trailing_empty_rows_empty_dataframe():
    """
    Test with completely empty DataFrame.
    """
    df = pd.DataFrame({
        'A': [None, None, None],
        'B': [None, None, None]
    })
    
    result = FileReader.skip_trailing_empty_rows(df)
    
    assert result.empty
    assert isinstance(result, pd.DataFrame)


# =====================================================================
# Test: Both Leading and Trailing
# =====================================================================

def test_skip_both_leading_and_trailing():
    """
    Test removing both leading and trailing empty rows.
    """
    df = pd.DataFrame({
        'A': [None, None, 1, 2, 3, None, None],
        'B': [None, None, 4, 5, 6, None, None]
    })
    
    result = FileReader.skip_leading_empty_rows(df)
    result = FileReader.skip_trailing_empty_rows(result)
    
    assert result.shape == (3, 2)
    assert result.iloc[0]['A'] == 1
    assert result.iloc[-1]['A'] == 3


# =====================================================================
# Test: Detect Header Row
# =====================================================================

def test_detect_header_row_at_start():
    """
    Test detecting header when it's at the first row.
    """
    df = pd.DataFrame({
        0: ['Name', 'John', 'Jane'],
        1: ['Age', '30', '25']
    })
    
    header_row = FileReader.detect_header_row(df)
    
    assert header_row == 0


def test_detect_header_row_after_metadata():
    """
    Test detecting header after metadata rows.
    """
    df = pd.DataFrame({
        0: [None, None, 'Name', 'John'],
        1: [None, None, 'Age', '30']
    })
    
    header_row = FileReader.detect_header_row(df)
    
    assert header_row == 2


def test_detect_header_row_sparse():
    """
    Test detecting header in sparse data.
    """
    df = pd.DataFrame({
        0: [None, None, 'Name', 'John', 'Jane'],
        1: [None, None, 'Age', '30', '25'],
        2: [None, None, 'City', 'NYC', 'LA']
    })
    
    header_row = FileReader.detect_header_row(df, max_rows_to_check=4)
    
    assert header_row == 2


# =====================================================================
# Test: Integration with CSV Reader
# =====================================================================

def test_csv_reader_with_leading_empty_rows(csv_with_leading_empty_rows):
    """
    Test reading CSV with leading empty rows.
    
    Verifies that:
    - Leading empty rows are automatically skipped
    - Headers are correctly detected
    - Data is intact
    """
    reader = CSVReader()
    df = reader.read(csv_with_leading_empty_rows)
    
    assert df.shape == (2, 3), f"Expected (2, 3) but got {df.shape}"
    assert list(df.columns) == ['Name', 'Age', 'City']
    assert df.iloc[0]['Name'] == 'John'


def test_csv_reader_without_skip_empty_rows(csv_with_leading_empty_rows):
    """
    Test that skip_leading_empty_rows parameter doesn't cause errors.
    
    Note: pandas.read_csv() automatically skips completely blank lines
    at the beginning of files, so both settings may produce identical results.
    This test verifies that both work correctly without errors.
    """
    reader = CSVReader()
    
    # Both should work without errors
    df_skip = reader.read(csv_with_leading_empty_rows, skip_leading_empty_rows=True)
    df_no_skip = reader.read(csv_with_leading_empty_rows, skip_leading_empty_rows=False)
    
    # Both should have valid data
    assert df_skip.shape[0] >= 2, "Expected at least 2 data rows with skip"
    assert df_no_skip.shape[0] >= 2, "Expected at least 2 data rows without skip"
    
    # Both should have the correct columns
    assert 'Name' in df_skip.columns
    assert 'Name' in df_no_skip.columns
    
    # Both should have the correct data
    assert df_skip.iloc[0]['Name'] == 'John'
    assert df_no_skip.iloc[0]['Name'] == 'John'


def test_csv_reader_with_trailing_empty_rows(csv_with_trailing_empty_rows):
    """
    Test reading CSV with trailing empty rows.
    """
    reader = CSVReader()
    df = reader.read(csv_with_trailing_empty_rows)
    
    assert df.shape == (2, 3)
    assert df.iloc[-1]['Name'] == 'Jane'


def test_csv_reader_with_both_empty_rows(csv_with_both_empty_rows):
    """
    Test reading CSV with both leading and trailing empty rows.
    """
    reader = CSVReader()
    df = reader.read(csv_with_both_empty_rows)
    
    assert df.shape == (2, 3), f"Expected (2, 3) but got {df.shape}"
    assert df.iloc[0]['Name'] == 'John'
    assert df.iloc[-1]['Name'] == 'Jane'


# =====================================================================
# Test: read_with_metadata_rows
# =====================================================================

def test_read_with_metadata_rows(csv_with_metadata):
    """
    Test read_with_metadata_rows method with skip_rows.
    
    Verifies that:
    - Skip rows works correctly
    - Empty row removal works after skip_rows
    - Final DataFrame is clean
    """
    reader = CSVReader()
    df = reader.read_with_metadata_rows(csv_with_metadata, skip_rows=2)
    
    # After skipping 2 rows and removing empty rows
    assert df.shape == (2, 3), f"Expected (2, 3) but got {df.shape}"
    assert list(df.columns) == ['Name', 'Age', 'City']
    assert df.iloc[0]['Name'] == 'John'


def test_read_with_metadata_rows_auto_clean(csv_with_metadata):
    """
    Test that read_with_metadata_rows cleans empty rows automatically.
    """
    reader = CSVReader()
    
    # Suprimir ParserWarning que ocurre cuando se prueban delimitadores incorrectos
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=pd.errors.ParserWarning)
        
        # Sin skip_rows: debería limpiar líneas vacías pero mantener metadata
        df_auto = reader.read_with_metadata_rows(csv_with_metadata)
        assert not df_auto.empty
        
        # Con skip_rows=2: debería saltar las dos líneas de metadata
        # y dejar limpio con 'Name' como header
        df_clean = reader.read_with_metadata_rows(csv_with_metadata, skip_rows=2)
        assert 'Name' in df_clean.columns, \
            f"Expected 'Name' in columns, got {list(df_clean.columns)}"


# =====================================================================
# Test: read_multiple_files with Empty Rows
# =====================================================================

def test_read_multiple_files_with_empty_rows(tmp_path):
    """
    Test that read_multiple_files handles empty rows in all files.
    """
    # Create multiple CSVs with empty rows
    for i in range(3):
        filepath = tmp_path / f"file{i}.csv"
        with open(filepath, 'w', newline='') as f:
            f.write("\n")  # Leading empty row
            f.write("Name,Value,Code\n")
            f.write(f"Item{i},100,{i}\n")
            f.write(f"Item{i+1},200,{i+1}\n")
            f.write("\n")  # Trailing empty row
    
    reader = CSVReader()
    files = reader.read_multiple_files(str(tmp_path))
    
    assert len(files) == 3
    for filename, df in files.items():
        assert df.shape == (2, 3), f"{filename}: Expected (2, 3) but got {df.shape}"
        assert 'Name' in df.columns


# =====================================================================
# Test: Edge Cases
# =====================================================================

def test_single_row_after_empty_rows():
    """
    Test DataFrame with only one data row after empty rows.
    """
    df = pd.DataFrame({
        'A': [None, None, 'Value'],
        'B': [None, None, '123']
    })
    
    result = FileReader.skip_leading_empty_rows(df)
    
    assert result.shape == (1, 2)
    assert result.iloc[0]['A'] == 'Value'


def test_mixed_nulls_and_empty_strings():
    """
    Test with mix of NaN, None, and empty strings.
    """
    df = pd.DataFrame({
        'A': [None, '', None, 'Data'],
        'B': [pd.NA, '', None, '456']
    })
    
    result = FileReader.skip_leading_empty_rows(df)
    
    assert result.shape[0] == 1
    assert result.iloc[0]['A'] == 'Data'


def test_whitespace_only_treated_as_empty():
    """
    Test that whitespace-only values are treated as empty.
    """
    df = pd.DataFrame({
        'A': ['   ', '  \t  ', 'Real Data'],
        'B': [' ', '\n', '789']
    })
    
    result = FileReader.skip_leading_empty_rows(df)
    
    assert result.shape[0] == 1
    assert result.iloc[0]['A'] == 'Real Data'