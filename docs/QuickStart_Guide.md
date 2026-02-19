# EDA-Toolkit - Quick Start Guide

## Introduction

**EDA-toolkit** is a comprehensive Python library for exploratory data analysis (EDA) with advanced file reading capabilities, automatic encoding detection, and data normalization.

## Quick Installation

```bash
# Clone repository
git clone <repo-url>
cd EDA-toolkit

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Get Started in 5 Minutes

### 1. Basic Reading

```python
from pandas_toolkit.io.readers import CSVReader

# Create reader
reader = CSVReader()

# Read file (automatic encoding and delimiter detection)
df = reader.read("data.csv")

print(f"Data loaded: {df.shape}")
```

### 2. Reading with Normalization

```python
# Read with automatic cleaning
df = reader.read(
    "data.csv",
    normalize=True,              # Clean values
    normalize_columns=True       # Clean column names
)

print(df.columns.tolist())  # Normalized columns
print(df.head())            # Preview
```

### 3. Export to Multiple Formats

```python
# Export results
reader.export(df, method="csv", filename="output.csv")
reader.export(df, method="excel", filename="report.xlsx")
```

## Available Readers

| Reader | Format | Primary Use |
|--------|---------|---------------|
| `CSVReader` | CSV | CSV files with automatic detection |
| `TSVReader` | TSV | Tab-separated files |
| `PipeReader` | Pipe | Pipe-delimited files |
| `ExcelReader` | Excel | .xlsx and .xls files |
| `JSONReader` | JSON/JSONL | APIs and JSON data |
| `HTMLReader` | HTML | HTML tables (Oracle, web) |

## Basic Usage by Format

### CSV (Automatic)

```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader(verbose=True)
df = reader.read("data.csv")

print(f"Encoding: {reader.success_encoding}")
print(f"Delimiter: {repr(reader.success_delimiter)}")
```

### Excel (Multiple Sheets)

```python
from pandas_toolkit.io.readers import ExcelReader

reader = ExcelReader()

# Single sheet
df = reader.read("report.xlsx", sheet_name="Sales")

# All sheets
sheets = reader.read_multiple_sheets("report.xlsx")
for name, df in sheets.items():
    print(f"{name}: {df.shape}")
```

### JSON (API/JSONL)

```python
from pandas_toolkit.io.readers import JSONReader

reader = JSONReader()

# Standard JSON
df = reader.read("api_data.json", orient="records")

# JSONL (streaming)
df = reader.read_lines("logs.jsonl")
```

### HTML (Multiple Tables)

```python
from pandas_toolkit.io.readers import HTMLReader

reader = HTMLReader()

# Single table
df = reader.read("oracle_export.html", table_index=0)

# All tables
tables = reader.read_all_tables("oracle_export.html")
df0, df1, df2 = tables[0], tables[1], tables[2]
```

## Using the Factory (Recommended)

The Factory automatically detects the file type:

```python
from pandas_toolkit.io.factory import ReaderFactory

# You don't need to know the file type
file = "data.csv"  # or .xlsx, .json, .html, etc.

reader = ReaderFactory.create_reader(file, verbose=True)
df = reader.read(file)

print(f"Reader used: {type(reader).__name__}")
```

### Example: Universal Processor

```python
from pandas_toolkit.io.factory import ReaderFactory
from pathlib import Path

def process_file(file):
    """Process any supported file."""
    try:
        reader = ReaderFactory.create_reader(file, verbose=True)
        df = reader.read(file, normalize=True, normalize_columns=True)
        
        print(f"✓ {file}")
        print(f"  Reader: {type(reader).__name__}")
        print(f"  Shape: {df.shape}")
        
        # Export
        base_name = Path(file).stem
        reader.export(df, method="csv", filename=f"{base_name}_processed.csv")
        
        return df
    except Exception as e:
        print(f"✗ Error processing {file}: {e}")
        return None

# Use
df = process_file("data.csv")
```

## Data Normalization

### Normalize Column Names

```python
reader = CSVReader()

# Before: ["  First Name  ", "Last-Name", "Émployee ID"]
df = reader.read("data.csv", normalize_columns=True)
# After: ["first_name", "last_name", "employee_id"]

print(df.columns.tolist())
```

### Normalize Values

```python
reader = CSVReader()

df = reader.read("data.csv", normalize=True)

# Creates _norm columns with clean values
print(df[['name', 'name_norm']].head())
#      name       name_norm
# 0    JOHN       john
# 1    MARY       mary
```

### Complete Normalization

```python
reader = CSVReader()

df = reader.read(
    "data.csv",
    normalize_columns=True,           # Clean names
    normalize=True,                   # Clean values
    skip_leading_empty_rows=True,     # Skip empty rows
    skip_trailing_empty_rows=True
)
```

## Data Export

### Basic Formats

```python
reader = CSVReader(output_dir="exports")
df = reader.read("data.csv")

# CSV
reader.export(df, method="csv", filename="output.csv")

# Excel
reader.export(df, method="excel", filename="report.xlsx")

# Parquet (efficient)
reader.export(df, method="parquet", filename="data.parquet")

# JSON
df.to_json("exports/data.json", orient="records", indent=2)
```

### Large Datasets

```python
# Split into multiple Excel files
reader.export(
    large_df,
    method="excel_parts",
    filename_prefix="data",
    max_rows=100000  # 100K per file
)
# Creates: data_part1.xlsx, data_part2.xlsx, etc.

# Or multiple sheets in one file
reader.export(
    large_df,
    method="excel_sheets",
    filename="data.xlsx",
    max_rows=50000  # 50K per sheet
)
```

## Batch Processing

### Multiple Files

```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader(verbose=True)

# Read all CSVs from a folder
files = reader.read_multiple_files(
    "data_folder/",
    normalize=True,
    normalize_columns=True
)

for filename, df in files.items():
    print(f"{filename}: {df.shape}")
    
    # Process each one
    reader.export(df, method="excel", filename=f"{filename}_processed.xlsx")
```

### With Factory (Any Format)

```python
from pandas_toolkit.io.factory import ReaderFactory
from pathlib import Path

folder = Path("data_folder")
factory = ReaderFactory()
supported = factory.get_supported_extensions()

for file in folder.iterdir():
    if file.suffix.lower() in supported:
        reader = factory.create_reader(str(file))
        df = reader.read(str(file), normalize=True)
        
        print(f"✓ {file.name}: {df.shape}")
```

## Practical Examples

### Example 1: Problematic CSV

```python
from pandas_toolkit.io.readers import CSVReader

# File with unknown encoding, unknown delimiter, and dirty columns
reader = CSVReader(
    verbose=True,
    capture_bad_lines=True
)

df = reader.read(
    "problematic_file.csv",
    normalize=True,
    normalize_columns=True
)

print(f"✓ File read:")
print(f"  Encoding: {reader.success_encoding}")
print(f"  Delimiter: {repr(reader.success_delimiter)}")
print(f"  Shape: {df.shape}")

if reader.bad_lines:
    print(f"  ⚠ Problematic lines: {len(reader.bad_lines)}")
```

### Example 2: Excel Multi-Sheet

```python
from pandas_toolkit.io.readers import ExcelReader

reader = ExcelReader(verbose=True, output_dir="exports")

# View available sheets
sheets = reader.read_sheet_names("report.xlsx")
print(f"Sheets: {sheets}")

# Read all
all_sheets = reader.read_multiple_sheets("report.xlsx", normalize=True)

# Export each sheet as CSV
for sheet_name, df in all_sheets.items():
    reader.export(df, method="csv", filename=f"{sheet_name}.csv")
    print(f"✓ {sheet_name}: {df.shape}")
```

### Example 3: Oracle HTML Export

```python
from pandas_toolkit.io.readers import HTMLReader

reader = HTMLReader(verbose=True, output_dir="exports")

# Read all tables
tables = reader.read_all_tables(
    "oracle_export.html",
    normalize=True,
    normalize_columns=True
)

print(f"Total tables: {len(tables)}")

# Process each table
for i, df in enumerate(tables):
    print(f"\nTable {i}:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {df.columns.tolist()}")
    
    # Export
    reader.export(df, method="csv", filename=f"table_{i}.csv")
    reader.export(df, method="excel", filename=f"table_{i}.xlsx")
```

### Example 4: API JSON Response

```python
from pandas_toolkit.io.readers import JSONReader

reader = JSONReader(verbose=True)

# Read API response
df = reader.read("api_response.json", orient="records")

print(f"API data: {df.shape}")
print(df.head())

# Export for analysis
reader.export(df, method="excel", filename="api_data.xlsx")
```

### Example 5: Complete Pipeline

```python
from pandas_toolkit.io.factory import ReaderFactory

print("=" * 70)
print("COMPLETE PROCESSING PIPELINE")
print("=" * 70)

# 1. Read (automatic detection)
reader = ReaderFactory.create_reader("data.csv", verbose=True, output_dir="exports")
print(f"\n1️⃣ Reader: {type(reader).__name__}")

# 2. Load and clean
df = reader.read(
    "data.csv",
    normalize=True,
    normalize_columns=True
)
print(f"2️⃣ Loaded: {df.shape}")

# 3. Process (your logic here)
df_processed = df[df['value'] > 100].copy()
print(f"3️⃣ Filtered: {df_processed.shape}")

# 4. Export
reader.export(df_processed, method="csv", filename="result.csv")
reader.export(df_processed, method="excel", filename="result.xlsx")
print(f"4️⃣ Exported: exports/")

print("\n✅ Pipeline completed!")
```

## Recommended Configuration

### For Development

```python
# Verbose enabled to see what's happening
reader = CSVReader(
    verbose=True,
    capture_bad_lines=True,
    output_dir="exports"
)
```

### For Production

```python
# Verbose disabled, automatic normalization
reader = CSVReader(
    verbose=False,
    capture_bad_lines=False,
    output_dir="output"
)

df = reader.read(
    file,
    normalize=True,
    normalize_columns=True
)
```

## Common Troubleshooting

### "UnicodeDecodeError"

```python
# Add more encodings to try
reader = CSVReader(
    encodings=['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
)
```

### "No module named 'openpyxl'"

```bash
pip install openpyxl
```

### "File not found"

```python
from pathlib import Path

# Verify the file exists
file = Path("data.csv")
if file.exists():
    df = reader.read(str(file))
else:
    print(f"File not found: {file}")
```

### "Columns don't match"

```python
# Try more delimiters
reader = CSVReader(
    delimiters=[',', ';', '\t', '|', ' ']
)
```

## Additional Resources

### Complete Guides

- [CSVReader_Guide.md](CSVReader_Guide.md) - CSV with automatic detection
- [ExcelReader_Guide.md](ExcelReader_Guide.md) - Excel multi-sheet
- [JSONReader_Guide.md](JSONReader_Guide.md) - JSON and JSONL
- [HTMLReader_Guide.md](HTMLReader_Guide.md) - HTML tables
- [DelimitedReaders_Guide.md](DelimitedReaders_Guide.md) - TSV and Pipe
- [Factory_Guide.md](Factory_Guide.md) - Factory pattern
- [Exporter_Guide.md](Exporter_Guide.md) - Advanced export
- [Normalization_Guide.md](Normalization_Guide.md) - Detailed normalization

### Tests and Examples

- `tests/` - Unit tests with examples
- `Testeos Jupyter/` - Interactive notebooks
- `test_html_reader.py` - HTMLReader examples

## Support and Contribution

- **Issues**: Report bugs or request features on GitHub
- **Docs**: All guides in the `docs/` folder
- **Tests**: Run `pytest tests/` to see all tests

## Command Summary

```python
# Basic import
from pandas_toolkit.io.readers import CSVReader, ExcelReader, JSONReader, HTMLReader
from pandas_toolkit.io.factory import ReaderFactory

# Quick read
reader = CSVReader()
df = reader.read("data.csv", normalize=True, normalize_columns=True)

# With Factory (recommended)
reader = ReaderFactory.create_reader("file.ext", verbose=True)
df = reader.read("file.ext", normalize=True, normalize_columns=True)

# Export
reader.export(df, method="csv", filename="output.csv")
reader.export(df, method="excel", filename="report.xlsx")
```

Ready to start! 🚀
