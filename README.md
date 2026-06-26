# EDA-toolkit

A comprehensive Python toolkit for exploratory data analysis (EDA) with advanced file reading capabilities, automatic encoding detection, and data normalization features.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Development & Building](#development--building)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [Usage Examples](#usage-examples)
- [Advanced Features](#advanced-features)
- [API Reference](#api-reference)

## Features

✨ **Smart File Reading**
- Automatic encoding detection (UTF-8, Latin-1, Windows-1252, and more)
- Automatic delimiter detection for delimited text files
- Support for multiple formats: CSV, TSV, Excel, JSON, Pipe-delimited, HTML

🔧 **Data Normalization**
- Column name normalization (remove accents, standardize casing, remove special characters)
- Cell value normalization (trim whitespace, case conversion)
- Handle empty rows and columns
- Duplicate column name detection

💾 **Flexible Export**
- Export to CSV, Excel (single or multiple sheets)
- Split large DataFrames across multiple files
- Preserve data integrity through complete pipeline

🏭 **Factory Pattern**
- Automatic reader selection based on file extension
- Easy registration of custom readers
- Extensible architecture

## Installation

### From GitHub (Recommended)

Install directly from the GitHub repository:

```bash
# Install the latest version
pip install git+https://github.com/FelipeCarballo1991/EDA-toolkit.git

# Install a specific version (using tags)
pip install git+https://github.com/FelipeCarballo1991/EDA-toolkit.git@v0.1.0

# Update to the latest version (if already installed)
pip install --upgrade git+https://github.com/FelipeCarballo1991/EDA-toolkit.git

# Force reinstall (useful when repository changed but version number didn't)
pip install --force-reinstall git+https://github.com/FelipeCarballo1991/EDA-toolkit.git
```

### From Source

```bash
# Clone the repository
git clone https://github.com/FelipeCarballo1991/EDA-toolkit.git
cd EDA-toolkit

# Install the package
pip install .
```

### For Development

```bash
# Clone the repository
git clone https://github.com/FelipeCarballo1991/EDA-toolkit.git
cd EDA-toolkit

# Create a virtual environment
python -m venv .venv

# Activate the environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Upgrade pip and build tools
python -m pip install --upgrade pip setuptools wheel

# Install in editable mode for development
pip install -e .
```

## Development & Building

### Package Structure

The project uses `pyproject.toml` for modern Python packaging:

```
EDA-toolkit/
├── pandas_toolkit/          # Main package directory
│   ├── __init__.py
│   ├── io/                  # I/O modules
│   │   ├── __init__.py
│   │   ├── readers/
│   │   ├── base/
│   │   └── ...
├── docs/                    # Documentation
├── tests/                   # Test files
├── pyproject.toml          # Package configuration
└── README.md
```

### Building the Package

To create distributable builds:

```bash
# 1. Install the build tool
pip install build

# 2. Generate distribution packages
python -m build

# This creates:
# dist/
#   pandas_toolkit-0.1.0.tar.gz         # Source distribution
#   pandas_toolkit-0.1.0-py3-none-any.whl  # Wheel distribution
```

### Testing the Build

To test the package in a clean environment:

```bash
# Create a test environment
python -m venv test_env

# Activate it
# Windows:
test_env\Scripts\activate
# Linux/Mac:
source test_env/bin/activate

# Install from the wheel
pip install dist/pandas_toolkit-0.1.0-py3-none-any.whl

# Test the import
python -c "import pandas_toolkit; print('Installation successful!')"
```

### pyproject.toml Configuration

The package uses modern Python packaging standards with the following key dependencies:

- **pandas** >= 2.2, < 3.0
- **numpy** >= 2.0, < 3.0
- **openpyxl** >= 3.1, < 4.0 (for Excel support)
- **pyarrow** >= 21.0.0 (for Parquet support)
- **lxml** >= 5.0.0 (for HTML/XML parsing)
- **html5lib** >= 1.1 (for HTML parsing)
- **python-dateutil** >= 2.9.0

Requires Python >= 3.9

## Quick Start

### Basic File Reading

```python
from pandas_toolkit.io import CSVReader

# Create a reader
reader = CSVReader()

# Read a CSV file
df = reader.read("data.csv")

# Read with normalization
df = reader.read(
    "data.csv",
    normalize=True,              # Normalize cell values
    normalize_columns=True       # Normalize column names
)

print(df.head())
```

### Using the Factory

```python
from pandas_toolkit.io import ReaderFactory

# Factory automatically selects the correct reader
factory = ReaderFactory()

# Works with any supported format
df_csv = factory.create_reader("data.csv").read("data.csv")
df_excel = factory.create_reader("report.xlsx").read("report.xlsx")
df_json = factory.create_reader("data.json").read("data.json")

# Check supported formats
print(factory.get_supported_extensions())
# ['.csv', '.html', '.htm', '.json', '.jsonl', '.pipe', '.tsv', '.xls', '.xlsx']
```

## Core Components

### File Readers

#### CSVReader
Reads CSV files with automatic encoding and delimiter detection.

```python
from pandas_toolkit.io import CSVReader

reader = CSVReader(
    encodings=["utf-8", "latin1", "cp1252"],  # Custom encodings to try
    verbose=True                               # Show debug information
)

df = reader.read("data.csv")
print(f"Detected encoding: {reader.success_encoding}")
print(f"Detected delimiter: {reader.success_delimiter}")
```

#### TSVReader & PipeReader
Specialized readers for tab-separated and pipe-separated values.

```python
from pandas_toolkit.io import TSVReader, PipeReader

# Read TSV files
tsv_reader = TSVReader()
df = tsv_reader.read("data.tsv")

# Read pipe-delimited files
pipe_reader = PipeReader()
df = pipe_reader.read("data.pipe")
```

#### ExcelReader
Read single or multiple sheets from Excel workbooks.

```python
from pandas_toolkit.io import ExcelReader

reader = ExcelReader()

# Read specific sheet
df = reader.read("report.xlsx", sheet_name="Sales")

# Get all sheet names
sheets = reader.read_sheet_names("report.xlsx")
print(sheets)  # ['Sales', 'Inventory', 'Customers']

# Read multiple sheets as dictionary
data = reader.read_multiple_sheets("report.xlsx")
for sheet_name, df in data.items():
    print(f"{sheet_name}: {df.shape}")

# Read all sheets as list (unified interface)
tables = reader.read_all("report.xlsx")
for i, df in enumerate(tables):
    print(f"Sheet {i}: {df.shape}")
```

#### JSONReader
Read JSON and JSONL (JSON Lines) formatted files.

```python
from pandas_toolkit.io import JSONReader

reader = JSONReader()

# Read JSON file
df = reader.read("data.json", orient="records")

# Read JSONL (streaming format)
df = reader.read_lines("streaming_data.jsonl")
```

#### HTMLReader
Read HTML files containing multiple tables (Oracle exports, web tables, etc.).

```python
from pandas_toolkit.io import HTMLReader

reader = HTMLReader(verbose=True)

# Read first table by default
df = reader.read("oracle_export.html")

# Read specific table by index
df0 = reader.read("oracle_export.html", table_index=0)
df1 = reader.read("oracle_export.html", table_index=1)
df2 = reader.read("oracle_export.html", table_index=2)

# Get count of tables
count = reader.get_tables_count("oracle_export.html")
print(f"Found {count} tables")

# Read all tables as list (unified interface - recommended)
tables = reader.read_all("oracle_export.html")
for i, df in enumerate(tables):
    print(f"Table {i}: {df.shape}")

# Backward compatible: read_all_tables() still works
tables = reader.read_all_tables("oracle_export.html")  # Same as read_all()

# Read specific tables as dictionary
tables = reader.read_multiple_tables(
    "oracle_export.html",
    table_indices=[0, 2, 5]
)
df0 = tables[0]
df2 = tables[2]
df5 = tables[5]
```

## Usage Examples

### Example 1: Unified Interface with read_all()

All readers now support a unified `read_all()` interface that always returns a list of DataFrames:

```python
from pandas_toolkit.io import ReaderFactory

factory = ReaderFactory()

# CSV, JSON, Parquet → Returns [df] (single DataFrame in list)
tables = factory.create_reader("data.csv").read_all("data.csv")
print(len(tables))  # 1
df = tables[0]

# Excel → Returns list of DataFrames (one per sheet)
tables = factory.create_reader("report.xlsx").read_all("report.xlsx")
print(len(tables))  # Number of sheets
for i, df in enumerate(tables):
    print(f"Sheet {i}: {df.shape}")

# HTML → Returns list of DataFrames (one per table)
tables = factory.create_reader("page.html").read_all("page.html")
print(len(tables))  # Number of HTML tables
for i, df in enumerate(tables):
    print(f"Table {i}: {df.shape}")

# Process all tables consistently regardless of format
for table in tables:
    # Do something with each DataFrame
    print(table.head())
```

### Example 2: Export Multiple Tables with export_tables()

The new `export_tables()` method intelligently handles single or multiple DataFrames:

```python
from pandas_toolkit.io import HTMLReader, FileExporter

# Read multiple tables from HTML
reader = HTMLReader()
tables = reader.read_all("oracle_export.html")
print(f"Found {len(tables)} tables")

# Export all tables to a single Excel file with multiple sheets
exporter = FileExporter(output_dir="exports")
exporter.export_tables(
    tables,
    filename="oracle_export.xlsx"
)
# Creates: oracle_export.xlsx with Table1, Table2, Table3, ... sheets

# Single DataFrame also works
df = reader.read("data.csv")
exporter.export_tables(df, filename="single_table.xlsx")

# Large DataFrame automatically splits into multiple sheets
import pandas as pd
large_df = pd.DataFrame({"col": range(2_000_000)})  # 2M rows
exporter.export_tables(
    large_df,
    filename="large_data.xlsx",
    max_rows_per_sheet=1000000
)
# Creates: large_data.xlsx with Sheet1 (1M rows), Sheet2 (1M rows)
```

### Example 3: Complete Workflow - HTML to Excel

```python
from pandas_toolkit.io import ReaderFactory, FileExporter

# Read all tables from HTML file
factory = ReaderFactory()
tables = factory.create_reader("oracle_export.html").read_all(
    "oracle_export.html",
    normalize=True,
    normalize_columns=True
)

print(f"Processing {len(tables)} tables...")

# Export all tables to single Excel file
exporter = FileExporter(output_dir="exports", verbose=True)
exporter.export_tables(
    tables,
    filename="processed_oracle_export.xlsx"
)

print("✓ Export completed!")
```

### Example 4: Reading Messy Data

```python
from pandas_toolkit.io import CSVReader

reader = CSVReader(verbose=True)

# File with problematic encoding and messy column names
df = reader.read(
    "messy_data.csv",
    normalize=True,
    normalize_columns=True
)

# Original columns: ["   First Name   ", "Last  Name", "Émployee-ID"]
# Normalized columns: ["first_name", "last_name", "employee_id"]

print(df.columns)
```

### Example 5: Batch Processing Files

```python
from pandas_toolkit.io import CSVReader

reader = CSVReader()

# Read all CSV files from a directory
files = reader.read_multiple_files(
    "data_folder/",
    normalize=True,
    normalize_columns=True
)

# Process each file
for filename, df in files.items():
    print(f"Processing {filename}...")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {df.columns.tolist()}")
```

### Example 6: Data Export (Legacy Methods)

```python
from pandas_toolkit.io import CSVReader

reader = CSVReader(output_dir="exports")

df = reader.read("data.csv")

# Export to CSV
reader.export(df, method="csv", filename="output.csv")

# Export to Excel
reader.export(df, method="excel", filename="report.xlsx")

# Export to multiple Excel sheets (for large files)
reader.export(
    df,
    method="excel_sheets",
    filename="large_report.xlsx",
    max_rows=5000
)

# Export to multiple Excel files
reader.export(
    df,
    method="excel_parts",
    filename_prefix="data",
    max_rows=10000
)
# Creates: data_part1.xlsx, data_part2.xlsx, etc.
```

### Example 7: Column Name Normalization

```python
from pandas_toolkit.io import CSVReader
import pandas as pd

reader = CSVReader()

# Create sample DataFrame with messy columns
df = pd.DataFrame({
    "   First Name   ": ["Juan", "Maria"],
    "Last  Name": ["García", "López"],
    "Émployee-ID": ["E001", "E002"]
})

# Normalize column names
df_normalized = reader.normalize_columns(df, convert_case="lower")

print(df_normalized.columns)
# ['first_name', 'last_name', 'employee_id']

# Preserve original case
df_normalized = reader.normalize_columns(df, convert_case=None)
print(df_normalized.columns)
# ['First_Name', 'Last_Name', 'Employee_ID']
```

### Example 8: Cell Value Normalization

```python
from pandas_toolkit.io import CSVReader
import pandas as pd

reader = CSVReader()

# Create sample DataFrame with messy values
df = pd.DataFrame({
    "Name": ["  JUAN  ", "  MARIA  "],
    "Status": ["  ACTIVE  ", "  INACTIVE  "]
})

# Create normalized columns (with "_norm" suffix)
df_normalized = reader.normalize(
    df,
    trim_strings=True,
    convert_case="lower",
    drop_empty_rows=False,
    drop_empty_cols=False
)

print(df_normalized.columns)
# ['Name', 'Status', 'Name_norm', 'Status_norm']

print(df_normalized['Name_norm'].tolist())
# ['juan', 'maria']
```

## Advanced Features

### Custom Encoding Detection

```python
from pandas_toolkit.io import CSVReader

# Define custom encoding priority
reader = CSVReader(
    encodings=["utf-8-sig", "utf-8", "iso-8859-1", "cp1252"]
)

df = reader.read("data.csv")
print(f"Successfully decoded with: {reader.success_encoding}")
```

### Capturing Bad Lines

```python
from pandas_toolkit.io import CSVReader

reader = CSVReader(capture_bad_lines=True, verbose=True)

df = reader.read("problematic_data.csv")

# Access captured bad lines
print(f"Found {len(reader.bad_lines)} bad lines")
for line in reader.bad_lines:
    print(line)
```

### Registering Custom Readers

```python
from pandas_toolkit.io import ReaderFactory, FileReader
import pandas as pd

class ParquetReader(FileReader):
    """Custom reader for Parquet files"""
    
    def _read(self, filepath: str, **kwargs) -> pd.DataFrame:
        return pd.read_parquet(filepath, **kwargs)
    
    def _get_file_extensions(self) -> list:
        return ['.parquet']

# Register the custom reader
factory = ReaderFactory()
factory.register_reader(".parquet", ParquetReader)

# Now use it
reader = factory.create_reader("data.parquet")
df = reader.read("data.parquet")
```

### Complete Pipeline

```python
from pandas_toolkit.io import ReaderFactory

# 1. Create factory
factory = ReaderFactory()

# 2. Read file with automatic format detection
reader = factory.create_reader("data.xlsx")
df = reader.read(
    "data.xlsx",
    normalize=True,
    normalize_columns=True
)

# 3. Process data
df['total'] = df['price'] * df['quantity']

# 4. Export results
reader.export(df, method="excel", filename="processed_report.xlsx")

print(f"✓ Successfully processed {df.shape[0]} rows")
```

## API Reference

### ReaderFactory

```python
class ReaderFactory:
    @classmethod
    def create_reader(filepath, output_dir=".", verbose=False, **kwargs) -> FileReader
    
    @classmethod
    def get_supported_extensions() -> list
    
    @classmethod
    def register_reader(extension, reader_class)
```

### FileReader (Base Class)

```python
class FileReader:
    def read(filepath, normalize=False, normalize_columns=False, **kwargs) -> pd.DataFrame
    
    def read_all(filepath, normalize=False, normalize_columns=False, **kwargs) -> list[pd.DataFrame]
    # Unified interface: always returns list of DataFrames
    # - Single-table formats (CSV, JSON): returns [df]
    # - Multi-table formats (Excel, HTML): returns [df1, df2, ...]
    
    def read_multiple_files(folderpath, **kwargs) -> dict
    
    def normalize_columns(df, convert_case="lower", empty_col_name="unnamed") -> pd.DataFrame
    
    def normalize(df, drop_empty_cols=False, drop_empty_rows=False, 
                  trim_strings=True, convert_case="lower") -> pd.DataFrame
    
    def export(df, method="excel", **kwargs)
```

### FileExporter

```python
class FileExporter:
    def export(df, method="excel", **kwargs)
    # Single DataFrame export
    # Methods: "csv", "excel", "excel_parts", "excel_sheets"
    
    def export_tables(tables, filename, method="excel", max_rows_per_sheet=1000000, **kwargs)
    # Intelligent multi-table export (NEW in v1.1.0)
    # - Accepts list[pd.DataFrame] or single pd.DataFrame
    # - Automatically handles: single tables, multiple tables, large tables
    # - Splits into multiple sheets/files when needed
    # - Respects Excel limits (1,048,576 rows per sheet)
    
    # Export Methods
    # - "csv": Export to single CSV file (single table only)
    # - "excel": Export to Excel with intelligent sheet management
```

## Supported File Formats

| Format | Reader | Extensions |
|--------|--------|-----------|
| CSV | CSVReader | `.csv` |
| TSV | TSVReader | `.tsv` |
| Pipe-delimited | PipeReader | `.pipe` |
| Excel | ExcelReader | `.xlsx`, `.xls` |
| JSON | JSONReader | `.json`, `.jsonl` |

## Error Handling

```python
from pandas_toolkit.io import CSVReader, FileEncodingError

reader = CSVReader(encodings=["ascii"])

try:
    df = reader.read("non_ascii_file.csv")
except FileEncodingError as e:
    print(f"Could not decode file: {e}")
    print("Try with different encodings")
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.1.0 (Current - February 2026)
- ✨ **NEW:** Unified `read_all()` interface across all readers
  - Returns `list[pd.DataFrame]` consistently for all file formats
  - Single-table formats (CSV, JSON, Parquet) return `[df]`
  - Multi-table formats (Excel, HTML) return `[df1, df2, ...]`
- ✨ **NEW:** Intelligent `export_tables()` method in FileExporter
  - Handles single or multiple DataFrames automatically
  - Auto-splits large tables into multiple sheets
  - Respects Excel row limits (1,048,576 rows/sheet)
  - Smart sheet naming strategies
- 🔧 **IMPROVED:** Excel row limit increased from 10,000 to 1,000,000 (default)
- 🔧 **IMPROVED:** HTMLReader.read_all_tables() now aliased to read_all() for consistency
- ✅ 94 tests passing - no breaking changes
- 📚 Enhanced documentation with new workflow examples

### Version 1.0.0
- ✨ Initial release with core file reading capabilities
- 🔧 Automatic encoding detection with fallback mechanism
- 🔧 Automatic delimiter detection for delimited files
- 💾 Data normalization for columns and values
- 💾 Multiple export formats (CSV, Excel with multiple sheets/files)
- 🏭 Factory pattern for reader selection
- 📚 Comprehensive documentation and examples

## Contact

For questions or issues, please open an issue on GitHub or send me an email to felipecarballo1991@gmail.com