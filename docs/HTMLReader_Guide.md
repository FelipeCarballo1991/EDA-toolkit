# HTMLReader - Complete Guide

## Description

`HTMLReader` is a toolkit component that allows reading HTML files containing one or more tables. It's especially useful for processing Oracle database exports, HTML reports, and web pages with tabular data.

## Main Features

- ✅ Reading HTML files with multiple tables
- ✅ Access specific tables by index
- ✅ Read all tables at once
- ✅ Data normalization support
- ✅ Compatible with Oracle exports
- ✅ Automatic error handling
- ✅ Export to multiple formats (CSV, Excel, Parquet, etc.)

## Installing Dependencies

To use `HTMLReader`, you need to install additional dependencies for HTML parsing:

```bash
pip install lxml html5lib
```

Or install all project dependencies:

```bash
pip install -r requirements.txt
```

## Basic Usage

### Import the Reader

```python
from pandas_toolkit.io.readers import HTMLReader
# Or using the factory
from pandas_toolkit.io.factory import ReaderFactory
```

### Read First Table (Default)

```python
reader = HTMLReader()

# Reads the first table by default (index 0)
df = reader.read("file.html")

print(df.head())
print(f"Shape: {df.shape}")
```

### Read Specific Tables by Index

```python
reader = HTMLReader(verbose=True)

# Read different tables by their index
df0 = reader.read("file.html", table_index=0)  # First table
df1 = reader.read("file.html", table_index=1)  # Second table
df2 = reader.read("file.html", table_index=2)  # Third table

print(f"Table 0: {df0.shape}")
print(f"Table 1: {df1.shape}")
print(f"Table 2: {df2.shape}")
```

## HTMLReader Methods

### 1. `read()` - Read a specific table

```python
reader = HTMLReader()

df = reader.read(
    filepath="file.html",
    table_index=0,                    # Table index (default: 0)
    normalize=False,                  # Normalize values
    normalize_columns=False,          # Normalize column names
    skip_leading_empty_rows=True,     # Skip empty rows at the beginning
    skip_trailing_empty_rows=True     # Skip empty rows at the end
)
```

### 2. `get_tables_count()` - Count tables without loading data

```python
reader = HTMLReader()

count = reader.get_tables_count("file.html")
print(f"The file contains {count} tables")
```

### 3. `read_all_tables()` - Read all tables as a list

```python
reader = HTMLReader(verbose=True)

# Returns a list of DataFrames
tables = reader.read_all_tables("file.html")

print(f"Total tables: {len(tables)}")

# Access each table by index
df0 = tables[0]
df1 = tables[1]
df2 = tables[2]

# Iterate over all tables
for i, df in enumerate(tables):
    print(f"Table {i}:")
    print(f"  - Rows: {df.shape[0]}")
    print(f"  - Columns: {df.shape[1]}")
    print(f"  - Columns: {df.columns.tolist()}")
    print()
```

### 4. `read_multiple_tables()` - Read specific tables as a dictionary

```python
reader = HTMLReader()

# Read only some specific tables
tables = reader.read_multiple_tables(
    "file.html",
    table_indices=[0, 2, 5]  # Only reads tables 0, 2, and 5
)

# Access as dictionary
df0 = tables[0]
df2 = tables[2]
df5 = tables[5]

# Or read all tables as dictionary (omit table_indices)
all_tables = reader.read_multiple_tables("file.html")

for idx, df in all_tables.items():
    print(f"Table {idx}: {df.shape}")
```

## Complete Example: Oracle File

This is a practical example to process an Oracle export with multiple tables:

```python
from pandas_toolkit.io.readers import HTMLReader

# Path to Oracle file
filepath = r"C:\Users\...\Oracle_SUARMZWORAP01_PMMP_20251119164507.html"

# Create reader with verbose to see the process
reader = HTMLReader(verbose=True, output_dir="exports")

# Method 1: Read all tables at once
print("=" * 60)
print("Reading all tables...")
print("=" * 60)

tables = reader.read_all_tables(filepath)

print(f"\nTotal tables found: {len(tables)}\n")

# Inspect each table
for i, df in enumerate(tables):
    print(f"Table {i}:")
    print(f"  Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"  Columns: {df.columns.tolist()}")
    print(f"  First row: {df.iloc[0].tolist() if len(df) > 0 else 'Empty'}")
    print()

# Method 2: Access specific tables
print("=" * 60)
print("Accessing specific tables...")
print("=" * 60)

df0 = reader.read(filepath, table_index=0)
df1 = reader.read(filepath, table_index=1)
df2 = reader.read(filepath, table_index=2)

print(f"First table: {df0.shape}")
print(df0.head(2))
print()

print(f"Second table: {df1.shape}")
print(df1.head(2))
print()

print(f"Third table: {df2.shape}")
print(df2.head(2))

# Method 3: Export each table
print("\n" + "=" * 60)
print("Exporting tables...")
print("=" * 60)

for i, df in enumerate(tables):
    # Export to CSV
    csv_filename = f"oracle_table_{i}.csv"
    reader.export(df, method="csv", filename=csv_filename)
    print(f"✓ Exported: {csv_filename}")
    
    # Export to Excel
    excel_filename = f"oracle_table_{i}.xlsx"
    reader.export(df, method="excel", filename=excel_filename)
    print(f"✓ Exported: {excel_filename}")

print("\nProcess completed!")
```

## Using with Normalization

HTMLReader supports the same normalization features as other readers:

```python
reader = HTMLReader(verbose=True)

# Read with column name and value normalization
df = reader.read(
    "oracle_export.html",
    table_index=0,
    normalize=True,              # Creates "_norm" columns with normalized values
    normalize_columns=True       # Normalizes column names
)

# Before: ["  Employee Name  ", "Salary ($)", "Début Date"]
# After: ["employee_name", "salary", "debut_date"]

print("Original vs normalized columns:")
for col in df.columns:
    if not col.endswith('_norm'):
        norm_col = col + '_norm' if col + '_norm' in df.columns else None
        print(f"  {col} -> {norm_col}")
```

## Using with Factory

The Factory automatically detects HTML files by their extension:

```python
from pandas_toolkit.io.factory import ReaderFactory

# The factory automatically creates an HTMLReader
reader = ReaderFactory.create_reader("oracle_export.html", verbose=True)

# The reader is already configured and ready to use
df = reader.read("oracle_export.html", table_index=0)

print(f"Reader type: {type(reader).__name__}")  # HTMLReader
```

## Error Handling

HTMLReader automatically handles several error cases:

### File not found

```python
reader = HTMLReader()

try:
    df = reader.read("nonexistent_file.html")
except FileNotFoundError as e:
    print(f"Error: {e}")
```

### Table index out of range

```python
reader = HTMLReader()

try:
    df = reader.read("file.html", table_index=999)
except ValueError as e:
    print(f"Error: {e}")
    # Error: Table index 999 is out of range. Found 3 table(s)...
```

### File without tables

```python
reader = HTMLReader()

try:
    df = reader.read("file_without_tables.html")
except ValueError as e:
    print(f"Error: {e}")
    # Error: No tables found in HTML file...
```

## Verbose Mode

Activate verbose mode for debugging:

```python
reader = HTMLReader(verbose=True)

# Will show detailed information:
# [DEBUG] Reading HTML file: file.html
# [INFO] Found 5 table(s) in HTML file
# [INFO] Successfully read table 0: 100 rows, 5 columns

df = reader.read("file.html")
```

## Export Tables

Once tables are read, you can export them to different formats:

```python
reader = HTMLReader(output_dir="exports")

# Read table
df = reader.read("oracle_export.html", table_index=0)

# Export to CSV
reader.export(df, method="csv", filename="table.csv")

# Export to Excel
reader.export(df, method="excel", filename="table.xlsx")

# Export to Parquet
reader.export(df, method="parquet", filename="table.parquet")

# Export to JSON
reader.export(df, method="json", filename="table.json")

# For large tables: split into multiple Excel files
reader.export(
    df,
    method="excel_parts",
    filename_prefix="table",
    max_rows=10000
)
# Creates: table_part1.xlsx, table_part2.xlsx, etc.
```

## Comparison with native pandas

### With native pandas:

```python
import pandas as pd

# pd.read_html returns a list of DataFrames
dfs = pd.read_html("file.html")

df0 = dfs[0]  # First table
df1 = dfs[1]  # Second table
df2 = dfs[2]  # Third table
```

### With HTMLReader (object-oriented):

```python
from pandas_toolkit.io.readers import HTMLReader

reader = HTMLReader(verbose=True, output_dir="exports")

# More control and additional features
df0 = reader.read("file.html", table_index=0, normalize=True)
df1 = reader.read("file.html", table_index=1, normalize=True)
df2 = reader.read("file.html", table_index=2, normalize=True)

# Or read all
tables = reader.read_all_tables("file.html", normalize=True)

# Advantages:
# - Integrated normalization
# - Verbose mode for debugging
# - Direct export to multiple formats
# - Consistent error handling
# - Automatic skip empty rows
```

## Tips and Best Practices

### 1. Explore the file first

```python
reader = HTMLReader(verbose=True)

# First count how many tables there are
count = reader.get_tables_count("file.html")
print(f"The file has {count} tables")

# Then read all to inspect them
tables = reader.read_all_tables("file.html")

for i, df in enumerate(tables):
    print(f"\nTable {i}:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {df.columns.tolist()}")
    print(f"  Sample:\n{df.head(2)}")
```

### 2. Use verbose during development

```python
# During development
reader = HTMLReader(verbose=True)

# In production
reader = HTMLReader(verbose=False)
```

### 3. Process selectively

```python
reader = HTMLReader()

# If you know you only need certain tables
tables = reader.read_multiple_tables(
    "file.html",
    table_indices=[0, 3]  # Only the ones you need
)
```

### 4. Combine normalization with export

```python
reader = HTMLReader(output_dir="exports")

# Read with normalization
df = reader.read(
    "oracle_export.html",
    table_index=0,
    normalize=True,
    normalize_columns=True
)

# Export clean data
reader.export(df, method="csv", filename="clean_data.csv")
```

## Compatibility

- ✅ Python 3.7+
- ✅ pandas 2.0+
- ✅ Requires: lxml >= 5.0.0 or html5lib >= 1.1
- ✅ Windows, Linux, macOS

## Troubleshooting

### Error: "No tables found"

Verify that the HTML contains `<table>` elements. Some exports may use `<div>` instead of `<table>`.

### Error: lxml not installed

```bash
pip install lxml
# or
pip install html5lib
```

### Encoding issues

If you have problems with special characters, specify the encoding:

```python
# pandas.read_html supports the encoding parameter
df = reader.read("file.html", encoding='utf-8')
```

## Additional Examples

See also:
- [`test_html_reader.py`](../test_html_reader.py) - Complete usage examples
- [`tests/test_html_reader.py`](../tests/test_html_reader.py) - Unit tests

## Support

To report bugs or request features, open an issue in the repository.
