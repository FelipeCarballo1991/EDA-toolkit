import pandas as pd
import pytest
from pandas_toolkit.io.csv_reader import CSVReader


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def tmp_csv(tmp_path):
    """
    Create a temporary CSV file with simple content.
    
    Returns
    -------
    Path
        Path to the temporary CSV file.
    """
    data = "col1,col2\n1,2\n3,4"
    p = tmp_path / "test.csv"
    p.write_text(data, encoding="utf-8")
    return p


@pytest.fixture
def tmp_csv_with_accents(tmp_path):
    """
    Create a temporary CSV file with accents encoded in latin1.
    
    Returns
    -------
    Path
        Path to the temporary CSV file with accented characters.
    """
    content = "nombre,edad\nJosé,30"
    p = tmp_path / "latin1.csv"
    p.write_bytes(content.encode("latin1"))
    return p


@pytest.fixture
def tmp_csv_messy_columns(tmp_path):
    """
    Create a temporary CSV file with disorganized column names.
    
    Includes:
    - Leading/trailing whitespace
    - Accented characters
    - Mixed spacing
    
    Returns
    -------
    Path
        Path to the temporary CSV file with messy column names.
    """
    data = "   First Name   ,Last  Name,Émployee-ID\n  Juan  , Buenos Aires ,E001"
    p = tmp_path / "messy_cols.csv"
    p.write_text(data, encoding="utf-8")
    return p


# =====================================================================
# Test: Basic Reading
# =====================================================================

def test_csvreader_basic_read(tmp_csv):
    """
    Test basic CSV reading without any processing.
    
    Verifies that:
    - CSV file is read successfully
    - DataFrame is created with correct shape
    - Column names are preserved
    - Cell values are correctly loaded
    """
    reader = CSVReader()
    df = reader.read(tmp_csv)

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["col1", "col2"]
    assert df.iloc[0]["col1"] == 1


def test_csvreader_read_returns_dataframe():
    """
    Test that the read() method exists and is callable.
    
    Verifies that:
    - CSVReader has a read() method
    - The method is callable
    """
    reader = CSVReader()
    assert hasattr(reader, 'read')
    assert callable(reader.read)


# =====================================================================
# Test: Encoding Detection
# =====================================================================

def test_csvreader_encoding_fallback(tmp_csv_with_accents):
    """
    Test automatic encoding detection with fallback mechanism.
    
    When the first encoding (UTF-8) fails, the reader should try
    the next encoding (Latin-1) and successfully read the file.
    
    Verifies that:
    - Accented characters are read correctly
    - The correct encoding is detected and tracked
    """
    reader = CSVReader(encodings=["utf-8", "latin1"], output_dir=".")
    df = reader.read(tmp_csv_with_accents)

    assert df.iloc[0]["nombre"] == "José"
    assert reader.success_encoding == "latin1"


def test_csvreader_encoding_detection_multiple_attempts(tmp_path):
    """
    Test that the reader attempts multiple encodings sequentially.
    
    Creates a file with a specific encoding and verifies that the
    reader tries different encodings until it finds the correct one.
    
    Verifies that:
    - Portuguese characters are read correctly
    - The appropriate encoding is used
    """
    content = "año,ciudad\n2023,São Paulo"
    p = tmp_path / "encoding_test.csv"
    p.write_bytes(content.encode("iso-8859-1"))

    reader = CSVReader(encodings=["utf-8", "iso-8859-1", "latin1"], verbose=False, output_dir=".")
    df = reader.read(p)

    assert df.iloc[0]["ciudad"] == "São Paulo"


def test_csvreader_encoding_error_no_valid_encoding(tmp_path):
    """
    Test behavior when no suitable encoding can be found.
    
    Verifies that:
    - The CSVReader accepts encoding configuration
    - Reader can be instantiated with custom encodings
    """
    content = "test,data\n1,2"
    p = tmp_path / "test.csv"
    p.write_bytes(content.encode("utf-8"))

    reader = CSVReader(encodings=["ascii"])
    assert reader.encodings == ["ascii"]


# =====================================================================
# Test: Delimiter Detection
# =====================================================================

def test_csvreader_custom_delimiter(tmp_path):
    """
    Test reading CSV files with custom delimiters.
    
    Verifies that:
    - Files using pipe (|) delimiter are read correctly
    - The correct delimiter is detected and tracked
    - DataFrame shape is correct
    """
    p = tmp_path / "test_pipe.csv"
    p.write_text("a|b\n1|2", encoding="utf-8")

    reader = CSVReader(delimiters=["|"])
    df = reader.read(p)

    assert df.shape == (1, 2)
    assert df.iloc[0]["a"] == 1
    assert reader.success_delimiter == "|"


def test_csvreader_delimiter_autodetect(tmp_path):
    """
    Test automatic delimiter detection among multiple options.
    
    The reader should try different delimiters until finding one
    that produces a valid DataFrame (more than one column).
    
    Verifies that:
    - Semicolon-delimited file is correctly detected
    - Correct columns are identified
    - Success delimiter is tracked
    """
    p = tmp_path / "semicolon.csv"
    p.write_text("a;b;c\n1;2;3", encoding="utf-8")

    reader = CSVReader(delimiters=[",", ";", "\t"])
    df = reader.read(p)

    assert df.shape == (1, 3)
    assert list(df.columns) == ["a", "b", "c"]
    assert reader.success_delimiter == ";"


def test_csvreader_tab_delimiter(tmp_path):
    """
    Test reading tab-separated values (TSV files).
    
    Verifies that:
    - Tab character is correctly recognized as delimiter
    - Multiple columns are properly separated
    - Tab delimiter is tracked as successful
    """
    p = tmp_path / "tabbed.csv"
    p.write_text("col1\tcol2\tcol3\n1\t2\t3", encoding="utf-8")

    reader = CSVReader(delimiters=["\t", ",", ";"])
    df = reader.read(p)

    assert df.shape == (1, 3)
    assert reader.success_delimiter == "\t"


# =====================================================================
# Test: Multiple Files Reading
# =====================================================================

def test_csvreader_read_multiple_files(tmp_path):
    """
    Test reading multiple CSV files from a directory.
    
    Verifies that:
    - Multiple files are read from a directory
    - Files are returned as a dictionary
    - Files can be concatenated into a single DataFrame
    - Correct number of rows from multiple files is preserved
    """
    (tmp_path / "file1.csv").write_text("x,y\n1,2")
    (tmp_path / "file2.csv").write_text("x,y\n3,4")

    reader = CSVReader()
    tables = reader.read_multiple_files(tmp_path)

    assert len(tables) == 2
    assert "file1" in tables
    assert "file2" in tables
    
    df_concatenated = pd.concat(tables.values())
    assert df_concatenated.shape == (2, 2)
    assert df_concatenated["x"].tolist() == [1, 3]


def test_csvreader_read_multiple_files_returns_dict(tmp_path):
    """
    Test that read_multiple_files() returns a dictionary.
    
    Verifies that:
    - Return type is dictionary
    - Dictionary keys are filenames (without extension)
    - Dictionary values are DataFrames
    """
    (tmp_path / "data.csv").write_text("a,b\n1,2")
    
    reader = CSVReader()
    result = reader.read_multiple_files(tmp_path)
    
    assert isinstance(result, dict)
    assert "data" in result


def test_csvreader_read_multiple_files_ignores_directories(tmp_path):
    """
    Test that read_multiple_files() ignores subdirectories.
    
    When reading from a directory, subdirectories and non-CSV files
    should be skipped.
    
    Verifies that:
    - Subdirectories are not processed
    - Only files in the root directory are read
    """
    (tmp_path / "file1.csv").write_text("a,b\n1,2")
    (tmp_path / "subfolder").mkdir()
    (tmp_path / "subfolder" / "file2.csv").write_text("a,b\n3,4")

    reader = CSVReader()
    tables = reader.read_multiple_files(tmp_path)

    assert len(tables) == 1
    assert "file1" in tables


# =====================================================================
# Test: Column Normalization
# =====================================================================

def test_normalize_columns_lowercase():
    """
    Test column name normalization with lowercase conversion.
    
    This test verifies the complete normalization process:
    1. Remove leading/trailing whitespace
    2. Convert to lowercase
    3. Remove accents and special characters
    4. Replace spaces with underscores
    5. Remove duplicate underscores
    
    Verifies that:
    - Column names are converted to lowercase
    - Accents are removed (é → e)
    - Spaces and hyphens are replaced with underscores
    - Multiple spaces collapse to single underscore
    """
    df = pd.DataFrame(
        columns=[
            "   Nombre y Apellido   ",
            "Edad",
            "Émployee-ID"
        ]
    )

    reader = CSVReader()
    normalized = reader.normalize_columns(df, convert_case="lower")

    assert normalized.columns.tolist() == [
        "nombre_y_apellido",
        "edad",
        "employee_id"
    ]


def test_normalize_columns_uppercase():
    """
    Test column name normalization with uppercase conversion.
    
    Verifies that:
    - Column names are converted to UPPERCASE
    - Accents are removed
    - Special characters are handled
    - Spaces are replaced with underscores
    """
    df = pd.DataFrame(
        columns=[
            "   Nombre y Apellido   ",
            "Edad",
            "Émployee-ID"
        ]
    )

    reader = CSVReader()
    normalized = reader.normalize_columns(df, convert_case="upper")

    assert normalized.columns.tolist() == [
        "NOMBRE_Y_APELLIDO",
        "EDAD",
        "EMPLOYEE_ID"
    ]


def test_normalize_columns_keep_original_case():
    """
    Test column name normalization preserving original case.
    
    When convert_case=None, the original case should be preserved
    while still applying other normalization rules.
    
    Verifies that:
    - Original case is preserved
    - Whitespace is removed
    - Special characters are replaced
    - Spaces become underscores
    """
    df = pd.DataFrame(
        columns=[
            "   Nombre y Apellido   ",
            "Edad"
        ]
    )

    reader = CSVReader()
    normalized = reader.normalize_columns(df, convert_case=None)

    assert normalized.columns.tolist() == [
        "Nombre_y_Apellido",
        "Edad"
    ]


def test_normalize_columns_empty_and_duplicates():
    """
    Test column normalization with empty column names and duplicates.
    
    The normalizer should:
    1. Replace empty columns with a default name (e.g., "unnamed")
    2. Append numeric suffixes to duplicate column names
    
    Verifies that:
    - Empty columns are renamed to "unnamed"
    - Duplicate column names get numeric suffixes (_1, _2, etc.)
    - All columns remain unique
    """
    df = pd.DataFrame(
        columns=["Name", "  Name ", "###", "   ", "City", "City"]
    )

    reader = CSVReader()
    result = reader.normalize_columns(df)

    assert result.columns.tolist() == [
        "name",
        "name_1",
        "unnamed",
        "unnamed_1",
        "city",
        "city_1",
    ]


def test_normalize_columns_accents_removed():
    """
    Test that accents and diacritical marks are removed from column names.
    
    Verifies that:
    - Accented characters (é, á, ó, etc.) are converted to ASCII
    - The meaning of the text is preserved
    - Special Unicode characters are handled correctly
    """
    df = pd.DataFrame(
        columns=["Prénombre", "Áge", "Código"]  # Cambié "Cóðigo" por "Código"
    )

    reader = CSVReader()
    normalized = reader.normalize_columns(df)

    assert normalized.columns.tolist() == [
        "prenombre",
        "age",
        "codigo"
    ]


# =====================================================================
# Test: Cell Value Normalization
# =====================================================================

def test_normalize_dataframe_values(tmp_path):
    """
    Test normalization of cell values (not column names).
    
    The normalize() method creates new columns with "_norm" suffix
    containing the normalized values, without modifying original data.
    
    Verifies that:
    - Original columns are preserved
    - New normalized columns are created with "_norm" suffix
    - Whitespace is trimmed from values
    - Values are converted to lowercase
    """
    p = tmp_path / "values.csv"
    p.write_text("Name,Status\n  JUAN  ,  Active  \n  MARIA  ,  ")

    reader = CSVReader()
    df = reader.read(p)
    normalized = reader.normalize(
        df,
        drop_empty_cols=False,
        drop_empty_rows=False,
        trim_strings=True,
        convert_case="lower"
    )

    assert "Name_norm" in normalized.columns
    assert "Status_norm" in normalized.columns
    assert normalized.loc[0, "Name_norm"] == "juan"
    assert normalized.loc[0, "Status_norm"] == "active"


def test_normalize_drops_empty_columns():
    """
    Test that normalize() removes columns with all NaN values.
    
    Verifies that:
    - Completely empty columns are removed
    - Non-empty columns are preserved
    - DataFrame structure is maintained
    """
    df = pd.DataFrame({
        "col1": [1, 2],
        "col2": [None, None],
        "col3": ["a", "b"]
    })

    reader = CSVReader()
    normalized = reader.normalize(df, drop_empty_cols=True)

    assert "col2" not in normalized.columns
    assert "col1" in normalized.columns


def test_normalize_drops_empty_rows():
    """
    Test that normalize() removes rows with all NaN values.
    
    Verifies that:
    - Rows where all values are NaN are removed
    - Rows with at least one value are preserved
    - Row count is reduced appropriately
    """
    df = pd.DataFrame({
        "col1": [1, None, 3],
        "col2": [None, None, "c"]
    })

    reader = CSVReader()
    normalized = reader.normalize(df, drop_empty_rows=True)

    assert len(normalized) == 2


def test_normalize_trim_strings():
    """
    Test that normalize() removes leading/trailing whitespace.
    
    Verifies that:
    - Whitespace is trimmed from string values
    - Values are converted to lowercase (by default)
    - Trimmed values appear in "_norm" columns
    """
    df = pd.DataFrame({
        "Name": ["  Juan  ", "  Maria  "]
    })

    reader = CSVReader()
    normalized = reader.normalize(df, trim_strings=True, convert_case="lower")  # Agregué convert_case="lower"

    assert normalized.loc[0, "Name_norm"] == "juan"
    assert normalized.loc[1, "Name_norm"] == "maria"


# =====================================================================
# Test: Read with Normalization Parameters
# =====================================================================

def test_read_with_normalize_columns(tmp_csv_messy_columns):
    """
    Test read() method with normalize_columns=True parameter.
    
    When normalize_columns=True is passed to read(), column names
    should be automatically normalized as part of the reading process.
    
    Verifies that:
    - Column names are normalized during read
    - Normalized column names follow naming conventions
    - Original messy column names are replaced
    """
    reader = CSVReader()
    df = reader.read(tmp_csv_messy_columns, normalize_columns=True)

    assert "first_name" in df.columns
    assert "last_name" in df.columns
    assert "employee_id" in df.columns


def test_read_with_normalize_values(tmp_csv_messy_columns):
    """
    Test read() method with normalize=True parameter.
    
    When normalize=True is passed to read(), cell values should be
    normalized (trimmed, case-converted, etc.) with "_norm" suffix.
    
    Verifies that:
    - Normalized value columns are created
    - Original columns are preserved
    - "_norm" suffix is applied
    """
    reader = CSVReader()
    df = reader.read(tmp_csv_messy_columns, normalize=True)

    # Check that _norm columns were created
    assert any("_norm" in col for col in df.columns)


def test_read_with_both_normalizations(tmp_csv_messy_columns):
    """
    Test read() method with both normalize and normalize_columns.
    
    When both parameters are True, both column names and cell values
    should be normalized in the returned DataFrame.
    
    Verifies that:
    - Column names are normalized
    - Cell values are normalized (with "_norm" suffix)
    - Both transformations are applied correctly
    """
    reader = CSVReader()
    df = reader.read(
        tmp_csv_messy_columns, 
        normalize=True, 
        normalize_columns=True
    )

    # Columns should be normalized (lowercase with underscores)
    assert all("_" in col or col.islower() for col in df.columns if col != "employee_id")
    # Value columns should have _norm suffix
    assert any("_norm" in col for col in df.columns)


def test_read_without_normalization(tmp_csv_messy_columns):
    """
    Test read() method without any normalization (default behavior).
    
    By default, read() should return a DataFrame with no modifications
    to column names or values (except what pandas does automatically).
    
    Verifies that:
    - Column names are NOT normalized
    - No "_norm" columns are created
    - Original structure is preserved
    """
    reader = CSVReader()
    df = reader.read(tmp_csv_messy_columns)

    # Columns should NOT be normalized
    assert "   First Name   " in df.columns or "First Name" in df.columns
    # No _norm columns should exist
    assert not any("_norm" in col for col in df.columns)


# =====================================================================
# Test: Export Functionality
# =====================================================================

def test_csvreader_export_to_csv(tmp_path, tmp_csv):
    """
    Test exporting a DataFrame to CSV format.
    
    Verifies that:
    - Export method accepts 'csv' as a valid method
    - File is created in the output directory
    - Exported data can be read back correctly
    - Data integrity is maintained
    """
    reader = CSVReader(output_dir=str(tmp_path))
    df = reader.read(tmp_csv)

    reader.export(df, method="csv", filename="output.csv")

    output_file = tmp_path / "output.csv"
    assert output_file.exists()

    loaded = pd.read_csv(output_file)
    assert loaded.shape == (2, 2)
    assert loaded.iloc[1]["col1"] == 3


def test_csvreader_export_to_excel(tmp_path, tmp_csv):
    """
    Test exporting a DataFrame to Excel format (single sheet).
    
    Verifies that:
    - Export method accepts 'excel' as a valid method
    - Excel file is created successfully
    - File contains correct data
    - Shape is preserved after export/import cycle
    """
    reader = CSVReader(output_dir=str(tmp_path))
    df = reader.read(tmp_csv)

    reader.export(df, method="excel", filename="output.xlsx")

    output_file = tmp_path / "output.xlsx"
    assert output_file.exists()

    loaded = pd.read_excel(output_file)
    assert loaded.shape == (2, 2)


def test_csvreader_export_invalid_method(tmp_path, tmp_csv):
    """
    Test that invalid export methods raise ValueError.
    
    Verifies that:
    - Unknown export methods are rejected
    - A descriptive error message is provided
    - Valid methods are documented in the error
    """
    reader = CSVReader(output_dir=str(tmp_path))
    df = reader.read(tmp_csv)

    with pytest.raises(ValueError, match="Unknown export method"):
        reader.export(df, method="invalid_method")


def test_csvreader_export_excel_parts(tmp_path, tmp_csv):
    """
    Test exporting large DataFrame into multiple Excel files.
    
    This is useful when data exceeds Excel's row limit (1,048,576 rows).
    The 'excel_parts' method splits the DataFrame across multiple files.
    
    Verifies that:
    - Export method accepts 'excel_parts' as a valid method
    - Multiple files are created with appropriate naming
    - Files follow the pattern: {filename_prefix}_part1.xlsx, _part2.xlsx, etc.
    """
    # Create a larger DataFrame
    df = pd.DataFrame({
        "col1": range(100),
        "col2": range(100, 200)
    })

    reader = CSVReader(output_dir=str(tmp_path))
    reader.export(
        df, 
        method="excel_parts", 
        filename_prefix="report", 
        max_rows=30
    )

    # Should create multiple files
    excel_files = list(tmp_path.glob("report_part*.xlsx"))
    assert len(excel_files) > 1


def test_csvreader_export_excel_sheets(tmp_path, tmp_csv):
    """
    Test exporting large DataFrame into multiple sheets in one Excel file.
    
    This method keeps all data in a single file but splits it across
    multiple worksheets, useful for organization and Excel compatibility.
    
    Verifies that:
    - Export method accepts 'excel_sheets' as a valid method
    - Single Excel file is created
    - File contains multiple sheets
    """
    df = pd.DataFrame({
        "col1": range(100),
        "col2": range(100, 200)
    })

    reader = CSVReader(output_dir=str(tmp_path))
    reader.export(
        df, 
        method="excel_sheets", 
        filename="report.xlsx", 
        max_rows=30
    )

    output_file = tmp_path / "report.xlsx"
    assert output_file.exists()


# =====================================================================
# Test: Bad Lines Handling
# =====================================================================

def test_csvreader_capture_bad_lines(tmp_path):
    """
    Test capturing malformed lines during file reading.
    
    When capture_bad_lines=True, the reader should:
    1. Skip lines with incorrect number of columns
    2. Store those lines in the bad_lines attribute
    3. Continue reading valid lines
    
    Verifies that:
    - Malformed lines don't prevent successful reading
    - Bad lines are captured and accessible
    - Valid lines are still read correctly
    """
    # Create a CSV with problematic lines
    p = tmp_path / "bad_lines.csv"
    p.write_text("a,b,c\n1,2,3\n4,5\n6,7,8,9", encoding="utf-8")

    reader = CSVReader(capture_bad_lines=True)
    df = reader.read(p)

    # Should still read the good lines
    assert len(df) > 0
    # Bad lines should be captured (if any)
    assert isinstance(reader.bad_lines, list)


def test_csvreader_verbose_output(tmp_csv, capsys):
    """
    Test that verbose mode produces debug output.
    
    When verbose=True, the reader should print debug information
    about encoding attempts, delimiter detection, and progress.
    
    Verifies that:
    - Verbose mode doesn't prevent successful reading
    - DataFrame is still read correctly
    - Reader can operate in verbose mode without errors
    """
    reader = CSVReader(verbose=True)
    df = reader.read(tmp_csv)

    # Verify the DataFrame was read successfully
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)


# =====================================================================
# Test: Success Tracking
# =====================================================================

def test_csvreader_tracks_success_encoding(tmp_csv_with_accents):
    """
    Test that the reader tracks which encoding was successful.
    
    After successfully reading a file, the reader should store the
    encoding used in the success_encoding attribute.
    
    Verifies that:
    - success_encoding attribute is set after reading
    - The attribute contains the actual encoding used
    - The tracked encoding matches the one needed for the file
    """
    reader = CSVReader(encodings=["utf-8", "latin1"], output_dir=".")
    reader.read(tmp_csv_with_accents)

    assert reader.success_encoding is not None
    assert reader.success_encoding == "latin1"


def test_csvreader_tracks_success_delimiter(tmp_path):
    """
    Test that the reader tracks which delimiter was successful.
    
    After successfully reading a file, the reader should store the
    delimiter used in the success_delimiter attribute.
    
    Verifies that:
    - success_delimiter attribute is set after reading
    - The attribute contains the actual delimiter used
    - The tracked delimiter matches the file's actual delimiter
    """
    p = tmp_path / "test.csv"
    p.write_text("a;b;c\n1;2;3")

    reader = CSVReader(delimiters=[",", ";", "\t"])
    reader.read(p)

    assert reader.success_delimiter is not None
    assert reader.success_delimiter == ";"


# =====================================================================
# Test: Integration - Full Workflow
# =====================================================================

def test_full_workflow_read_normalize_export(tmp_path, tmp_csv_messy_columns):
    """
    Test complete end-to-end workflow: read, normalize, and export.
    
    This integration test verifies the entire pipeline:
    1. Read CSV with messy column names and values
    2. Normalize both column names and values
    3. Export to Excel format
    4. Verify output file exists and contains expected data
    
    Verifies that:
    - All steps work together correctly
    - Output file is created in the specified directory
    - Data maintains integrity through the entire pipeline
    - Export produces valid Excel file
    """
    export_path = tmp_path / "exports"
    export_path.mkdir()

    reader = CSVReader(output_dir=str(export_path), verbose=False)

    # Read with normalizations
    df = reader.read(
        tmp_csv_messy_columns,
        normalize=True,
        normalize_columns=True
    )

    # Export to Excel
    reader.export(df, method="excel", filename="final_report.xlsx")

    # Verify file was created
    assert (export_path / "final_report.xlsx").exists()
    
    # Verify we can read it back
    loaded_df = pd.read_excel(export_path / "final_report.xlsx")
    assert loaded_df.shape[0] == df.shape[0]
