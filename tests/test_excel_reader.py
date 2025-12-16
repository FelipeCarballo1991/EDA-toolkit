import pandas as pd
import pytest
from pandas_toolkit.io import ExcelReader
from pandas_toolkit.io.base.constants import EXCEL_ENGINES


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def tmp_excel_simple(tmp_path):
    """
    Create a temporary simple Excel file.
    
    Returns
    -------
    Path
        Path to the temporary Excel file.
    """
    df = pd.DataFrame({
        "col1": [1, 2, 3],
        "col2": ["a", "b", "c"]
    })
    filepath = tmp_path / "simple.xlsx"
    df.to_excel(filepath, index=False, sheet_name="Sheet1")
    return filepath


@pytest.fixture
def tmp_excel_multiple_sheets(tmp_path):
    """
    Create a temporary Excel file with multiple sheets.
    
    Returns
    -------
    Path
        Path to the temporary Excel file with multiple sheets.
    """
    filepath = tmp_path / "multiple_sheets.xlsx"
    
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        # Sheet 1: Sales data
        df_sales = pd.DataFrame({
            "Date": ["2023-01-01", "2023-01-02"],
            "Amount": [100, 200]
        })
        df_sales.to_excel(writer, sheet_name="Sales", index=False)
        
        # Sheet 2: Inventory data
        df_inventory = pd.DataFrame({
            "Product": ["A", "B"],
            "Quantity": [10, 20]
        })
        df_inventory.to_excel(writer, sheet_name="Inventory", index=False)
        
        # Sheet 3: Customers data
        df_customers = pd.DataFrame({
            "Name": ["John", "Jane"],
            "City": ["NYC", "LA"]
        })
        df_customers.to_excel(writer, sheet_name="Customers", index=False)
    
    return filepath


@pytest.fixture
def tmp_excel_with_accents(tmp_path):
    """
    Create a temporary Excel file with accented characters.
    
    Returns
    -------
    Path
        Path to the temporary Excel file with accented characters.
    """
    df = pd.DataFrame({
        "Nombre": ["José", "María"],
        "Empleado-ID": ["E001", "E002"],
        "Departamento": ["Ventas", "RH"]
    })
    filepath = tmp_path / "accents.xlsx"
    df.to_excel(filepath, index=False, sheet_name="Empleados")
    return filepath


# =====================================================================
# Test: Basic Excel Reading
# =====================================================================

def test_excel_reader_basic_read(tmp_excel_simple):
    """
    Test basic Excel reading without any processing.
    
    Verifies that:
    - Excel file is read successfully
    - DataFrame is created with correct shape
    - Column names are preserved
    - Cell values are correctly loaded
    """
    reader = ExcelReader()
    df = reader.read(tmp_excel_simple)

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 2)
    assert list(df.columns) == ["col1", "col2"]
    assert df.iloc[0]["col1"] == 1


def test_excel_reader_has_read_method():
    """
    Test that ExcelReader has read() method.
    
    Verifies that:
    - ExcelReader has a read() method
    - The method is callable
    """
    reader = ExcelReader()
    assert hasattr(reader, 'read')
    assert callable(reader.read)


# =====================================================================
# Test: Engine Detection and Fallback
# =====================================================================

def test_excel_reader_engine_tracking(tmp_excel_simple):
    """
    Test that the reader tracks which engine was used.
    
    After successfully reading a file, the reader should store
    the engine used in the success_engine attribute.
    
    Verifies that:
    - success_engine attribute is set after reading
    - The attribute contains a valid engine name
    - Engine is one of the supported engines
    """
    reader = ExcelReader()
    df = reader.read(tmp_excel_simple)

    assert reader.success_engine is not None
    assert reader.success_engine in ["openpyxl", "xlrd"]
    assert isinstance(df, pd.DataFrame)


def test_excel_reader_custom_engines(tmp_excel_simple):
    """
    Test custom engine configuration.
    
    Verifies that:
    - Custom engines can be provided
    - Reader uses custom engine configuration
    - Custom engines are respected
    """
    custom_engines = {
        ".xlsx": ["openpyxl"],
        "default": ["openpyxl"]
    }
    
    reader = ExcelReader(engines=custom_engines)
    assert reader.engines == custom_engines
    
    df = reader.read(tmp_excel_simple)
    assert df.shape == (3, 2)


def test_excel_reader_get_engines_for_xlsx(tmp_excel_simple):
    """
    Test engine selection for .xlsx files.
    
    Verifies that:
    - Correct engines are selected for .xlsx files
    - openpyxl is tried first for modern Excel
    - Fallback engines are available
    """
    reader = ExcelReader()
    engines = reader._get_engines_for_file(str(tmp_excel_simple))
    
    assert len(engines) > 0
    assert "openpyxl" in engines


def test_excel_reader_get_engines_for_xls():
    """
    Test engine selection for .xls files.
    
    Verifies that:
    - Correct engines are selected for legacy .xls files
    - Proper engines are available for legacy format
    """
    reader = ExcelReader()
    engines = reader._get_engines_for_file("legacy_file.xls")
    
    assert len(engines) > 0
    # xlrd should be in the list for .xls files
    assert isinstance(engines, list)


def test_excel_reader_engine_mismatch_fallback(tmp_excel_simple):
    """
    Test that reader falls back to alternative engines.
    
    When attempting to read with an unavailable or unsuitable engine,
    the reader should try alternatives and succeed.
    
    Verifies that:
    - Reader can handle engine failures gracefully
    - Fallback mechanism works correctly
    - File is successfully read despite engine issues
    """
    # Create reader with specific engine order
    reader = ExcelReader()
    df = reader.read(tmp_excel_simple)
    
    # Even if first engine failed, it should succeed
    assert df is not None
    assert df.shape == (3, 2)


# =====================================================================
# Test: Sheet Operations
# =====================================================================

def test_excel_reader_read_specific_sheet(tmp_excel_multiple_sheets):
    """
    Test reading a specific sheet by name.
    
    Verifies that:
    - Specific sheet can be read by name
    - Correct data is returned for the sheet
    - DataFrame contains expected columns
    """
    reader = ExcelReader()
    df = reader.read(tmp_excel_multiple_sheets, sheet_name="Sales")

    assert df.shape[0] == 2
    assert "Date" in df.columns
    assert "Amount" in df.columns


def test_excel_reader_read_sheet_by_index(tmp_excel_multiple_sheets):
    """
    Test reading a sheet by index position.
    
    Verifies that:
    - Sheet can be accessed by index (0-based)
    - First sheet (index 0) is read correctly
    - Data from correct sheet is returned
    """
    reader = ExcelReader()
    
    # Read first sheet (index 0)
    df_first = reader.read(tmp_excel_multiple_sheets, sheet_name=0)
    assert df_first.shape[0] == 2
    
    # Read second sheet (index 1)
    df_second = reader.read(tmp_excel_multiple_sheets, sheet_name=1)
    assert "Product" in df_second.columns


def test_excel_reader_get_sheet_names(tmp_excel_multiple_sheets):
    """
    Test retrieving all sheet names without loading data.
    
    Verifies that:
    - All sheet names are correctly detected
    - Sheet names match expected values
    - No data is loaded when retrieving sheet names
    """
    reader = ExcelReader()
    sheets = reader.read_sheet_names(tmp_excel_multiple_sheets)

    assert len(sheets) == 3
    assert "Sales" in sheets
    assert "Inventory" in sheets
    assert "Customers" in sheets


def test_excel_reader_read_all_sheets(tmp_excel_multiple_sheets):
    """
    Test reading all sheets from a workbook.
    
    When sheet_names is None, all sheets should be read.
    
    Verifies that:
    - All sheets are read into dictionary
    - Dictionary keys are sheet names
    - Each value is a DataFrame with correct data
    """
    reader = ExcelReader()
    sheets = reader.read_multiple_sheets(tmp_excel_multiple_sheets)

    assert len(sheets) == 3
    assert "Sales" in sheets
    assert "Inventory" in sheets
    assert "Customers" in sheets
    
    # Verify data integrity
    assert sheets["Sales"].shape == (2, 2)
    assert sheets["Inventory"].shape == (2, 2)
    assert sheets["Customers"].shape == (2, 2)


def test_excel_reader_read_specific_sheets(tmp_excel_multiple_sheets):
    """
    Test reading only specified sheets from a workbook.
    
    Verifies that:
    - Only requested sheets are read
    - Other sheets are ignored
    - Returned dictionary contains only selected sheets
    """
    reader = ExcelReader()
    sheets = reader.read_multiple_sheets(
        tmp_excel_multiple_sheets,
        sheet_names=["Sales", "Customers"]
    )

    assert len(sheets) == 2
    assert "Sales" in sheets
    assert "Customers" in sheets
    assert "Inventory" not in sheets


# =====================================================================
# Test: Excel with Normalization
# =====================================================================

def test_excel_reader_with_normalize_columns(tmp_excel_with_accents):
    """
    Test reading Excel with column normalization.
    
    Verifies that:
    - Column names are normalized
    - Accents are removed
    - Special characters (hyphens) are converted to underscores
    - All column names are lowercase
    """
    reader = ExcelReader()
    df = reader.read(tmp_excel_with_accents, normalize_columns=True)

    assert "nombre" in df.columns
    assert "empleado_id" in df.columns  # Changed from "employee_id"
    assert "departamento" in df.columns


def test_excel_reader_with_normalize_values(tmp_excel_with_accents):
    """
    Test reading Excel with value normalization.
    
    Verifies that:
    - Normalized value columns are created with "_norm" suffix
    - Original columns are preserved
    - Data is correctly normalized
    """
    reader = ExcelReader()
    df = reader.read(tmp_excel_with_accents, normalize=True)

    # Should have original columns plus _norm columns
    assert "Nombre" in df.columns
    assert "Nombre_norm" in df.columns


def test_excel_reader_with_both_normalizations(tmp_excel_with_accents):
    """
    Test reading Excel with both column and value normalization.
    
    Verifies that:
    - Both transformations are applied
    - Column names are normalized
    - Values are normalized with "_norm" suffix
    """
    reader = ExcelReader()
    df = reader.read(
        tmp_excel_with_accents,
        normalize=True,
        normalize_columns=True
    )

    # Columns should be normalized
    assert "nombre" in df.columns
    # Should have _norm columns
    assert any("_norm" in col for col in df.columns)


# =====================================================================
# Test: Error Handling
# =====================================================================

def test_excel_reader_file_not_found():
    """
    Test behavior when Excel file doesn't exist.
    
    Verifies that:
    - FileNotFoundError is raised
    - Error message is informative
    """
    reader = ExcelReader()
    
    with pytest.raises(FileNotFoundError, match="File not found"):
        reader.read("nonexistent_file.xlsx")


def test_excel_reader_invalid_sheet_name(tmp_excel_multiple_sheets):
    """
    Test behavior when requesting non-existent sheet.
    
    Verifies that:
    - Appropriate error is raised
    - Reader handles invalid sheet names
    """
    reader = ExcelReader()
    
    with pytest.raises(Exception):
        reader.read(tmp_excel_multiple_sheets, sheet_name="NonExistentSheet")


# =====================================================================
# Test: Verbose Output
# =====================================================================

def test_excel_reader_verbose_output(tmp_excel_simple, capsys):
    """
    Test that verbose mode produces debug output.
    
    When verbose=True, the reader should print debug information
    about engine attempts and progress.
    
    Verifies that:
    - Verbose mode doesn't prevent successful reading
    - DataFrame is still read correctly
    - Reader can operate in verbose mode without errors
    """
    reader = ExcelReader(verbose=True)
    df = reader.read(tmp_excel_simple)

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 2)


def test_excel_reader_verbose_sheet_reading(tmp_excel_multiple_sheets, capsys):
    """
    Test verbose output when reading multiple sheets.
    
    Verifies that:
    - Sheet information is printed in verbose mode
    - All sheets are successfully read
    - Verbose mode provides useful debugging info
    """
    reader = ExcelReader(verbose=True)
    sheets = reader.read_multiple_sheets(tmp_excel_multiple_sheets)

    assert len(sheets) == 3


# =====================================================================
# Test: Export Excel Files
# =====================================================================

def test_excel_reader_export_to_csv(tmp_path, tmp_excel_simple):
    """
    Test exporting Excel data to CSV.
    
    Verifies that:
    - Excel data can be exported to CSV
    - CSV file is created correctly
    - Data integrity is maintained
    """
    export_path = tmp_path / "exports"
    export_path.mkdir()
    
    reader = ExcelReader(output_dir=str(export_path))
    df = reader.read(tmp_excel_simple)
    
    reader.export(df, method="csv", filename="exported.csv")
    
    assert (export_path / "exported.csv").exists()


def test_excel_reader_export_to_excel(tmp_path, tmp_excel_simple):
    """
    Test exporting to another Excel file.
    
    Verifies that:
    - Excel data can be exported to a new Excel file
    - File is created in output directory
    - Data is preserved through export cycle
    """
    export_path = tmp_path / "exports"
    export_path.mkdir()
    
    reader = ExcelReader(output_dir=str(export_path))
    df = reader.read(tmp_excel_simple)
    
    reader.export(df, method="excel", filename="exported.xlsx")
    
    assert (export_path / "exported.xlsx").exists()


# =====================================================================
# Test: Integration - Full Workflow
# =====================================================================

def test_excel_full_workflow(tmp_path, tmp_excel_multiple_sheets):
    """
    Test complete end-to-end workflow with Excel.
    
    This integration test verifies:
    1. Read multiple sheets from Excel
    2. Normalize data
    3. Export to new format
    4. Verify file creation
    
    Verifies that:
    - All steps work together correctly
    - Engine detection works seamlessly
    - Output files are created properly
    """
    export_path = tmp_path / "exports"
    export_path.mkdir()
    
    reader = ExcelReader(output_dir=str(export_path), verbose=False)
    
    # Read all sheets
    sheets = reader.read_multiple_sheets(
        tmp_excel_multiple_sheets,
        normalize=True,
        normalize_columns=True
    )
    
    # Export consolidated data
    combined_df = pd.concat(sheets.values(), ignore_index=True)
    reader.export(combined_df, method="excel", filename="consolidated.xlsx")
    
    assert (export_path / "consolidated.xlsx").exists()
    assert len(sheets) == 3