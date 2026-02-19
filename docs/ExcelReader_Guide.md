# ExcelReader - Complete Guide

## Description

`ExcelReader` is a robust component for reading Excel files (.xlsx and .xls). It includes **automatic engine detection** with fallback, handling of multiple sheets, and all the toolkit's normalization capabilities.

## Main Features

- ✅ **Supports .xlsx and .xls** (new and old formats)
- ✅ **Automatic engine detection** (openpyxl, xlrd) with fallback
- ✅ **Reading individual sheets** or multiple
- ✅ **Automatic sheet detection** available
- ✅ **Data norm alization** and column names
- ✅ **Export** to multiple formats
- ✅ **Robust error handling**

## Installing Dependencies

```bash
pip install pandas openpyxl xlrd
# Or install all project dependencies:
pip install -r requirements.txt
```

## Basic Usage

### Import the Reader

```python
from pandas_toolkit.io.readers import ExcelReader
# Or using the factory
from pandas_toolkit.io.factory import ReaderFactory
```

### Simple Reading (First Sheet)

```python
reader = ExcelReader()

# Reads the first sheet by default
df = reader.read("report.xlsx")

print(f"Shape: {df.shape}")
print(f"Engine used: {reader.success_engine}")
```

### Read Specific Sheet

```python
reader = ExcelReader(verbose=True)

# By sheet name
df = reader.read("report.xlsx", sheet_name="Sales")

# By index (0 = first sheet)
df = reader.read("report.xlsx", sheet_name=1)  # Second sheet

print(f"Shape: {df.shape}")
```

### Read with Normalization

```python
reader = ExcelReader(verbose=True)

df = reader.read(
    "report.xlsx",
    sheet_name="Data",
    normalize=True,              # Normalize values
    normalize_columns=True,      # Normalize column names
    skip_leading_empty_rows=True,  # Skip empty rows at start
    skip_trailing_empty_rows=True  # Skip empty rows at end
)

print(df.columns.tolist())
```

## ExcelReader Methods

### 1. `read()` - Read a sheet

```python
reader = ExcelReader()

df = reader.read(
    filepath="report.xlsx",
    sheet_name=0,                     # Sheet name or index (default: 0)
    normalize=False,                  # Normalize values
    normalize_columns=False,          # Normalize column names
    skip_leading_empty_rows=True,
    skip_trailing_empty_rows=True,
    # All pandas.read_excel parameters are supported:
    header=0,                         # Header row
    skiprows=None,                    # Rows to skip
    usecols=None,                     # Columns to read
    dtype=None,                       # Data types
    # ... etc
)
```

### 2. `read_sheet_names()` - List available sheets

```python
reader = ExcelReader()

# Get names of all sheets
sheets = reader.read_sheet_names("report.xlsx")

print(f"Available sheets: {sheets}")
# ['Sales', 'Inventory', 'Customers']
```

### 3. `read_multiple_sheets()` - Read multiple sheets

```python
reader = ExcelReader(verbose=True)

# Read all sheets
sheets = reader.read_multiple_sheets("report.xlsx")

# Returns a dictionary {sheet_name: DataFrame}
for sheet_name, df in sheets.items():
    print(f"{sheet_name}: {df.shape}")

# Read only specific sheets
sheets = reader.read_multiple_sheets(
    "report.xlsx",
    sheet_names=["Sales", "Inventory"]
)
```

### 4. `export()` - Export DataFrame

```python
reader = ExcelReader(output_dir="exports")

df = reader.read("report.xlsx", sheet_name="Sales")

# Export to CSV
reader.export(df, method="csv", filename="sales.csv")

# Export to Excel
reader.export(df, method="excel", filename="sales_processed.xlsx")

# Export to multiple Excel files (for large DataFrames)
reader.export(
    df,
    method="excel_parts",
    filename_prefix="sales",
    max_rows=10000
)
# Creates: sales_part1.xlsx, sales_part2.xlsx, etc.

# Export to multiple sheets (for large DataFrames)
reader.export(
    df,
    method="excel_sheets",
    filename="sales_complete.xlsx",
    max_rows=5000
)
# Creates: one file with multiple sheets
```

## Automatic Engine Detection

### Supported Engines

```python
EXCEL_ENGINES = {
    '.xlsx': ['openpyxl', 'xlrd'],  # Try openpyxl first, then xlrd
    '.xls': ['xlrd', 'openpyxl'],    # Try xlrd first for .xls
    'default': ['openpyxl']
}
```

### How It Works

The reader automatically tries different engines until it finds one that works:

```python
reader = ExcelReader(verbose=True)

# You will see in the log:
# [DEBUG] Trying to read Excel with engine='openpyxl'
# [INFO] Successfully read with engine='openpyxl': 100 rows, 5 columns

df = reader.read("report.xlsx")

print(f"Engine used: {reader.success_engine}")  # 'openpyxl'
```

### Customize Engines

```python
# Only use openpyxl
reader = ExcelReader(
    engines={
        '.xlsx': ['openpyxl'],
        '.xls': ['openpyxl']
    }
)

# Change the order of testing
reader = ExcelReader(
    engines={
        '.xlsx': ['xlrd', 'openpyxl'],  # Try xlrd first
    }
)
```

## Complete Example: Multiple Sheets

```python
from pandas_toolkit.io.readers import ExcelReader

print("=" * 70)
print("PROCESSING EXCEL FILE WITH MULTIPLE SHEETS")
print("=" * 70)

reader = ExcelReader(verbose=True, output_dir="exports")

file = "business_report.xlsx"

# Step 1: List available sheets
print("\nAvailable sheets:")
sheets = reader.read_sheet_names(file)
for i, sheet in enumerate(sheets):
    print(f"  {i}: {sheet}")

# Step 2: Read all sheets
print("\n" + "=" * 70)
print("Reading all sheets...")
print("=" * 70)

all_sheets = reader.read_multiple_sheets(
    file,
    normalize=True,
    normalize_columns=True
)

print(f"\n✓ Total sheets read: {len(all_sheets)}\n")

# Step 3: Inspect each sheet
for sheet_name, df in all_sheets.items():
    print(f"Sheet: {sheet_name}")
    print(f"  • Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  • Columns: {df.columns.tolist()}")
    print()

# Step 4: Work with specific sheets
sales_df = all_sheets.get('Sales')
inventory_df = all_sheets.get('Inventory')

if sales_df is not None:
    print("\n📊 Sales Analysis:")
    print(sales_df.head(3))
    
    # Export
    reader.export(sales_df, method="csv", filename="sales.csv")

if inventory_df is not None:
    print("\n📦 Inventory Analysis:")
    print(inventory_df.head(3))
    
    # Export
    reader.export(inventory_df, method="csv", filename="inventory.csv")

print("\n✅ Process completed!")
```

## Common Use Cases

### Case 1: Excel with Old Format (.xls)

```python
reader = ExcelReader(verbose=True)

# The reader automatically detects the format and uses the correct engine
df = reader.read("old_report.xls")

print(f"Engine used: {reader.success_engine}")  # Probably 'xlrd'
```

### Case 2: Excel with Hidden Sheets

```python
reader = ExcelReader()

# List all sheets (including hidden)
sheets = reader.read_sheet_names("report.xlsx")
print(f"Sheets: {sheets}")

# Hidden sheets can also be read
df = reader.read("report.xlsx", sheet_name="HiddenSheet")
```

### Case 3: Excel with Headers in Different Row

```python
reader = ExcelReader()

# If headers are in row 3
df = reader.read(
    "report.xlsx",
    header=2,  # Row 3 (0-indexed)
    skiprows=[0, 1]  # Skip the first 2 rows
)
```

### Case 4: Large Excel - Split into Multiple Files

```python
reader = ExcelReader(output_dir="exports")

# Read large Excel
df = reader.read("large_report.xlsx")

print(f"Total rows: {len(df)}")

# Export in files of 10,000 rows each
reader.export(
    df,
    method="excel_parts",
    filename_prefix="report",
    max_rows=10000
)
# Creates: report_part1.xlsx, report_part2.xlsx, etc.
```

### Case 5: Consolidate Multiple Sheets

```python
import pandas as pd
from pandas_toolkit.io.readers import ExcelReader

reader = ExcelReader()

# Read all sheets
sheets = reader.read_multiple_sheets("report.xlsx")

# Consolidate into a single DataFrame
df_consolidated = pd.concat(sheets.values(), ignore_index=True)

print(f"Consolidated DataFrame: {df_consolidated.shape}")

# Export consolidated
reader.export(df_consolidated, method="csv", filename="consolidated.csv")
```

## Batch Processing

### Process Multiple Excel Files

```python
from pathlib import Path
from pandas_toolkit.io.readers import ExcelReader

reader = ExcelReader(verbose=True, output_dir="exports")

# Get all Excel files
excel_files = list(Path("data_folder").glob("*.xlsx"))

for excel_file in excel_files:
    print(f"\n{'='*70}")
    print(f"Processing: {excel_file.name}")
    print('='*70)
    
    # Read all sheets
    sheets = reader.read_multiple_sheets(
        str(excel_file),
        normalize=True,
        normalize_columns=True
    )
    
    # Process each sheet
    for sheet_name, df in sheets.items():
        print(f"\n  Sheet: {sheet_name}")
        print(f"    Shape: {df.shape}")
        
        # Export each sheet as CSV
        output_name = f"{excel_file.stem}_{sheet_name}.csv"
        reader.export(df, method="csv", filename=output_name)
        print(f"    ✓ Exported: {output_name}")

print("\n✅ Batch processing completed!")
```

## Using with Factory

```python
from pandas_toolkit.io.factory import ReaderFactory

# The factory automatically creates an ExcelReader
reader = ReaderFactory.create_reader("report.xlsx", verbose=True)

df = reader.read("report.xlsx", sheet_name="Sales")

print(f"Reader type: {type(reader).__name__}")  # ExcelReader
```

## Advanced Parameters

### Passing Parameters to pandas.read_excel

```python
reader = ExcelReader()

df = reader.read(
    "report.xlsx",
    sheet_name="Data",
    # Pandas-specific parameters
    header=0,                   # Header row
    skiprows=[1, 2, 3],        # Skip specific rows
    usecols='A:E',             # Only columns A to E
    dtype={'A': str, 'B': int}, # Data types
    parse_dates=['fecha'],      # Parse dates
    na_values=['NA', 'N/A'],   # Additional null values
    # ... all pd.read_excel parameters
)
```

## Useful Attributes

```python
reader = ExcelReader()
df = reader.read("report.xlsx")

# Successful engine
print(f"Engine: {reader.success_engine}")

# Output directory
print(f"Output dir: {reader.output_dir}")

# Configured engines
print(f"Engines: {reader.engines}")
```

## Error Handling

### File Not Found

```python
reader = ExcelReader()

try:
    df = reader.read("nonexistent_file.xlsx")
except FileNotFoundError as e:
    print(f"Error: {e}")
```

### Sheet Not Found

```python
reader = ExcelReader()

try:
    df = reader.read("report.xlsx", sheet_name="NonexistentSheet")
except Exception as e:
    print(f"Error: {e}")
    
    # List available sheets
    sheets = reader.read_sheet_names("report.xlsx")
    print(f"Available sheets: {sheets}")
```

### No Engine Available

```python
# If you don't have openpyxl or xlrd installed
reader = ExcelReader(verbose=True)

try:
    df = reader.read("report.xlsx")
except Exception as e:
    print(f"Error: {e}")
    # Error: Could not read Excel file with any of the following engines...
    
    # Solution: install engine
    # pip install openpyxl
```

## Verbose Mode

```python
reader = ExcelReader(verbose=True)

# Will show you:
# [DEBUG] Trying to read Excel with engine='openpyxl', sheet=Sales
# [INFO] Successfully read with engine='openpyxl': 1000 rows, 5 columns

df = reader.read("report.xlsx", sheet_name="Sales")
```

## Comparison with Native pandas

### With native pandas:

```python
import pandas as pd

# Read with native pandas
df = pd.read_excel("report.xlsx", sheet_name="Sales", engine='openpyxl')

# For multiple sheets you need extra logic
xls = pd.ExcelFile("report.xlsx")
sheets = {}
for sheet_name in xls.sheet_names:
    sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
```

### With ExcelReader:

```python
from pandas_toolkit.io.readers import ExcelReader

reader = ExcelReader(verbose=True)

# Automatic engine detection
df = reader.read("report.xlsx", sheet_name="Sales")

# Multiple sheets simplified
sheets = reader.read_multiple_sheets("report.xlsx")

# Advantages:
# - Automatic engine fallback
# - Integrated normalization
# - Direct export to multiple formats
# - Consistent API with other readers
# - Robust error handling
```

## Tips and Best Practices

### 1. Always list sheets first

```python
reader = ExcelReader()

# See what sheets are available
sheets = reader.read_sheet_names("report.xlsx")
print(f"Sheets: {sheets}")

# Then read the one you need
df = reader.read("report.xlsx", sheet_name=sheets[0])
```

### 2. Use verbose during development

```python
# During development
reader = ExcelReader(verbose=True)

# In production
reader = ExcelReader(verbose=False)
```

### 3. Normalize when working with multiple sources

```python
reader = ExcelReader()

# Normalize for consistency
df = reader.read(
    "report.xlsx",
    normalize=True,
    normalize_columns=True
)
```

### 4. Split large DataFrames on export

```python
reader = ExcelReader(output_dir="exports")

df = reader.read("large_report.xlsx")

# Excel has a limit of ~1 million rows
# Split automatically
reader.export(
    df,
    method="excel_parts",
    filename_prefix="report",
    max_rows=100000
)
```

## Troubleshooting

### Problem: "No module named 'openpyxl'"

**Solution**: Install openpyxl

```bash
pip install openpyxl
```

### Problem: "Excel file format cannot be determined"

**Solution**: Verify that the extension is correct

```python
# Make sure the file has the correct extension
reader = ExcelReader()
df = reader.read("file.xlsx")  # Not "file.xls" if it's xlsx
```

### Problem: "Worksheet named 'X' not found"

**Solution**: List available sheets first

```python
reader = ExcelReader()

sheets = reader.read_sheet_names("report.xlsx")
print(f"Available sheets: {sheets}")

# Use the exact name
df = reader.read("report.xlsx", sheet_name=sheets[0])
```

## Compatibility

- ✅ Python 3.7+
- ✅ pandas 2.0+
- ✅ openpyxl 3.0+ (recommended for .xlsx)
- ✅ xlrd 2.0+ (optional, for old .xls)
- ✅ Windows, Linux, macOS

## Additional Examples

See also:
- [`test_excel_reader.py`](../tests/test_excel_reader.py) - Unit tests
- [`Tests_ExcelReader.ipynb`](../Testeos%20Jupyter/Tests_ExcelReader.ipynb) - Interactive examples

## Support

To report bugs or request features, open an issue in the repository.
