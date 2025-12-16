# EDA-toolkit - CSVReader

A robust Python library for reading, processing, and exporting CSV files with automatic encoding detection, delimiter discovery, and data normalization capabilities.

## Features

### 🔍 Automatic Encoding Detection
- Tries multiple encodings automatically (UTF-8, Latin-1, CP1252, ISO-8859-1, and 20+ more)
- Gracefully handles files with mixed or uncommon encodings
- Intelligently tracks which encoding was successful
- Supports encoding fallback mechanism

### 🎯 Automatic Delimiter Detection
- Automatically detects the correct delimiter used in your CSV file
- Supports common delimiters: comma, semicolon, tab, pipe, colon, and more
- Prefers delimiters that produce more columns (intelligent heuristic)
- Customizable delimiter lists for specific use cases
- Tracks which delimiter was successfully used

### 🛡️ Bad Line Detection
- Detects and captures malformed lines during file reading
- Optional logging of problematic lines for debugging
- Configurable behavior for handling corrupt data
- Does not interrupt file reading on bad lines

### 📊 Data Normalization
- **Column Name Normalization**: Remove accents, standardize casing, handle duplicates
- **Cell Value Normalization**: Trim whitespace, convert empty strings to None, normalize case
- Drop empty rows and columns automatically
- Create normalized versions without overwriting original data
- Accents and diacritical marks are properly removed

### 📁 Batch Operations
- Read multiple CSV files from a directory at once
- Export to multiple formats: CSV, Excel (single sheet, multiple parts, or multiple sheets)
- Handle large datasets by splitting across multiple Excel files
- Maintain consistency across batch operations

### 🔄 Export Flexibility
- Export to CSV format
- Export to Excel with single or multiple sheets
- Split large DataFrames across multiple Excel files (useful for Excel's row limits: 1,048,576)
- Customizable output directory and verbose logging
- Inherited by all subclasses for extensibility

### 🏗️ Extensible Architecture
- Template Method pattern for easy extension
- Create custom readers by extending FileReader
- Unified export interface across all reader types
- Support for future formats (JSON, Excel, Parquet, etc.)

## Installation

```bash
pip install -r requirements.txt
```

### Requirements
- pandas >= 2.3.1
- numpy >= 2.3.1
- openpyxl >= 3.1.5

## Architecture

### Class Hierarchy

```
FileReader (Abstract Base)
    ├── read()                    # Template Method
    ├── read_multiple_files()     # Batch operations
    └── export()                  # Common export interface
    
    └── FileReaderEncoding (Abstract)
        ├── _read()               # Try multiple encodings
        └── _read_with_encoding() # Must implement
        
        └── DelimitedTextReader
            ├── _read_with_encoding()  # Try multiple delimiters
            
            └── CSVReader             # CSV-specific reader
```

## Quick Start

### Basic Reading

```python
from pandas_toolkit.io import CSVReader

# Create a reader instance
reader = CSVReader()

# Read a CSV file (encoding and delimiter are auto-detected)
df = reader.read("path/to/file.csv")
```

### Reading with Custom Encodings

```python
# Specify custom encodings to try (in order of preference)
reader = CSVReader(encodings=["utf-8", "latin1", "cp1252", "iso-8859-1"])
df = reader.read("path/to/file.csv")

# Check which encoding was used
print(f"Used encoding: {reader.success_encoding}")
```

### Reading with Custom Delimiters

```python
# Specify custom delimiters to try
reader = CSVReader(delimiters=[";", "\t", "|", ","])
df = reader.read("path/to/file.csv")

# Check which delimiter was used
print(f"Used delimiter: {repr(reader.success_delimiter)}")
```

### Bad Line Detection

```python
# Enable bad line capture for debugging
reader = CSVReader(verbose=True, capture_bad_lines=True)
df = reader.read("path/to/problematic_file.csv")

# Access captured bad lines
print(f"Found {len(reader.bad_lines)} bad lines")
for line in reader.bad_lines[:5]:
    print(line)
```

## Usage Examples

### Normalize During Reading

```python
reader = CSVReader(verbose=True)

# Read file and normalize column names in one call
df = reader.read("data.csv", normalize_columns=True)

# The returned DataFrame contains normalized column names
print(df.columns)
# Output: ['col1', 'col2', 'col3']
```

### Normalize Column Names

```python
import pandas as pd

# Create a DataFrame with messy column names
df = pd.DataFrame({
    "First Name": [1, 2, 3],
    "Last  Name": [4, 5, 6],
    "Émployee-ID": [7, 8, 9]
})

reader = CSVReader()

# Normalize column names to lowercase with underscores
normalized_df = reader.normalize_columns(df, convert_case="lower")
print(normalized_df.columns.tolist())
# Output: ['first_name', 'last_name', 'employee_id']
```

### Handle Duplicate and Empty Columns

```python
df = pd.DataFrame({
    "Name": [1, 2],
    "Name": [3, 4],  # Duplicate
    "": [5, 6]       # Empty name
})

reader = CSVReader()
normalized_df = reader.normalize_columns(df)
print(normalized_df.columns.tolist())
# Output: ['name', 'name_1', 'unnamed']
```

### Normalize Cell Values

```python
df = pd.DataFrame({
    "Name": ["  JUAN  ", "  MARIA  "],
    "Status": ["  ACTIVE  ", "  INACTIVE  "]
})

reader = CSVReader()

# Normalize values (creates _norm columns)
normalized_df = reader.normalize(
    df, 
    trim_strings=True, 
    convert_case="lower"
)

print(normalized_df.columns)
# Output: ['Name', 'Status', 'Name_norm', 'Status_norm']

print(normalized_df['Name_norm'].tolist())
# Output: ['juan', 'maria']
```

### Read and Normalize in One Step

```python
reader = CSVReader(verbose=True)

# Read file with both column and value normalization
df = reader.read("data.csv", normalize=True, normalize_columns=True)

# DataFrame has:
# - Normalized column names (lowercase, underscores, no accents)
# - Original columns preserved
# - New "_norm" columns with normalized values
```

### Read Multiple Files

```python
reader = CSVReader()

# Read all CSV files from a directory
files_dict = reader.read_multiple_files("path/to/folder/")

# Each file is loaded as a separate DataFrame
for filename, df in files_dict.items():
    print(f"{filename}: {df.shape}")

# Concatenate all files if needed
import pandas as pd
combined_df = pd.concat(files_dict.values(), ignore_index=True)
```

### Read Multiple Files with Normalization

```python
reader = CSVReader()

# Read all files and normalize them
files_dict = reader.read_multiple_files(
    "data_folder/",
    normalize=True,
    normalize_columns=True
)

# All files are normalized automatically
for filename, df in files_dict.items():
    print(f"{filename}: {df.columns.tolist()}")
```

### Export to CSV

```python
reader = CSVReader(output_dir="exports", verbose=True)

# Read and process your data
df = reader.read("input.csv")

# Export to CSV
reader.export(df, method="csv", filename="output.csv")
```

### Export to Excel

```python
reader = CSVReader(output_dir="exports", verbose=True)

# Single-sheet Excel file
reader.export(df, method="excel", filename="report.xlsx")
```

### Export Large DataFrames - Multiple Parts

```python
reader = CSVReader(output_dir="exports", verbose=True)

# Split a large DataFrame into multiple Excel files
# (useful if DataFrame exceeds Excel's row limit of 1,048,576)
reader.export(
    df,
    method="excel_parts",
    filename_prefix="report",
    max_rows=1000000
)
# Output: report_part1.xlsx, report_part2.xlsx, report_part3.xlsx
```

### Export Large DataFrames - Multiple Sheets

```python
reader = CSVReader(output_dir="exports", verbose=True)

# Split a large DataFrame into multiple sheets within one Excel file
reader.export(
    df,
    method="excel_sheets",
    filename="report.xlsx",
    max_rows=50000
)
# Output: Single file with Sheet1, Sheet2, Sheet3, etc.
```

## Advanced Configuration

### Full Example with All Options

```python
reader = CSVReader(
    encodings=["utf-8", "utf-8-sig", "latin1", "cp1252", "iso-8859-1"],
    delimiters=[",", ";", "\t", "|"],
    verbose=True,                          # Print debug information
    capture_bad_lines=True,               # Capture malformed lines
    output_dir="outputs"                  # Directory for exports
)

# Read file with encoding/delimiter auto-detection
df = reader.read("raw_data.csv")
print(f"Encoding: {reader.success_encoding}")
print(f"Delimiter: {repr(reader.success_delimiter)}")

# Normalize column names
df = reader.read("raw_data.csv", normalize_columns=True)

# Normalize cell values
df = reader.normalize(
    df, 
    drop_empty_cols=True, 
    drop_empty_rows=True,
    trim_strings=True,
    convert_case="lower"
)

# Export results
reader.export(df, method="excel", filename="cleaned_data.xlsx")
```

### Normalize Method Options

```python
df_normalized = reader.normalize(
    df,
    drop_empty_cols=True,      # Remove columns with all NaN values
    drop_empty_rows=True,      # Remove rows with all NaN values
    trim_strings=True,         # Strip whitespace from strings
    convert_case="lower"       # 'lower', 'upper', or None
)
```

### Normalize Columns Method Options

```python
df_normalized = reader.normalize_columns(
    df,
    convert_case="lower",           # 'lower', 'upper', or None
    empty_col_name="unnamed"        # Name for empty columns
)
```

### Read Method Options

```python
df = reader.read(
    "path/to/file.csv",
    normalize=False,                # Normalize cell values
    normalize_columns=False,        # Normalize column names
    # Additional pandas read_csv arguments:
    skiprows=0,                     # Skip first N rows
    nrows=1000,                     # Read only first N rows
    dtype={'col1': str}             # Specify column types
)
```

## API Reference

### CSVReader Class

#### Constructor

```python
CSVReader(
    encodings=None,           # List of encodings to try (default: COMMON_ENCODINGS)
    delimiters=None,          # List of delimiters to try (default: COMMON_DELIMITERS)
    verbose=False,            # Enable debug output
    capture_bad_lines=False,  # Capture malformed lines
    output_dir=".",           # Output directory for exports
    exporter=None            # Custom FileExporter instance
)
```

#### Methods

| Method | Description |
|--------|-------------|
| `read(filepath, normalize=False, normalize_columns=False, **kwargs)` | Read a CSV file with optional normalization |
| `read_multiple_files(folderpath, **kwargs)` | Read all CSV files from a directory |
| `normalize(df, drop_empty_cols=False, drop_empty_rows=False, trim_strings=True, convert_case="lower")` | Normalize cell values in a DataFrame |
| `normalize_columns(df, convert_case="lower", empty_col_name="unnamed")` | Normalize column names |
| `export(df, method="excel", **kwargs)` | Export DataFrame to various formats |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `success_encoding` | str | The encoding that was successfully used to read the file |
| `success_delimiter` | str | The delimiter that was successfully used to parse the file |
| `bad_lines` | list | Captured malformed lines (if `capture_bad_lines=True`) |

### Export Methods

#### CSV Export

```python
reader.export(df, method="csv", filename="output.csv")
```

#### Excel Export (Single Sheet)

```python
reader.export(df, method="excel", filename="report.xlsx")
```

#### Excel Export (Multiple Files)

```python
reader.export(
    df, 
    method="excel_parts", 
    filename_prefix="report",
    max_rows=1000000
)
```

#### Excel Export (Multiple Sheets in One File)

```python
reader.export(
    df, 
    method="excel_sheets", 
    filename="report.xlsx",
    max_rows=50000
)
```

## Common Use Cases

### Use Case 1: Clean and Standardize a CSV File

```python
reader = CSVReader(verbose=True, output_dir="cleaned_data")

# Read with auto-detection
df = reader.read("messy_data.csv")

# Normalize everything
df = reader.read("messy_data.csv", normalize_columns=True, normalize=True)

# Export cleaned version
reader.export(df, method="excel", filename="clean_data.xlsx")
```

### Use Case 2: Merge Multiple CSV Files

```python
reader = CSVReader(output_dir="merged_data")

# Read all files from a folder with normalization
files = reader.read_multiple_files(
    "raw_data_folder/",
    normalize_columns=True
)

# Combine them
merged_df = pd.concat(files.values(), ignore_index=True)

# Export result
reader.export(merged_df, method="excel", filename="merged.xlsx")
```

### Use Case 3: Handle Large Files

```python
reader = CSVReader(output_dir="exports")

# Read large file
large_df = reader.read("very_large_file.csv")

# Process it...

# Export in multiple parts to avoid Excel row limits
reader.export(
    large_df,
    method="excel_parts",
    filename_prefix="large_report",
    max_rows=1000000
)
```

### Use Case 4: Handle Non-Standard Encodings

```python
# Japanese encoded CSV
reader = CSVReader(
    encodings=["utf-8", "shift_jis", "euc-jp"],
    verbose=True
)
df = reader.read("japanese_data.csv")
print(f"Successfully read with encoding: {reader.success_encoding}")
```

### Use Case 5: Process CSV with Custom Delimiters

```python
# Pipe-delimited file
reader = CSVReader(delimiters=["|", ",", ";"])
df = reader.read("pipe_delimited.txt")
print(f"Successfully read with delimiter: {repr(reader.success_delimiter)}")

# Export to standard CSV
reader.export(df, method="csv", filename="converted.csv")
```

### Use Case 6: Batch Process Directory with Normalization

```python
reader = CSVReader(output_dir="processed", verbose=True)

# Read and normalize all CSV files
files = reader.read_multiple_files(
    "raw_data/",
    normalize=True,
    normalize_columns=True
)

# Export each normalized file
for filename, df in files.items():
    reader.export(
        df, 
        method="excel", 
        filename=f"{filename}_processed.xlsx"
    )
```

## Troubleshooting

### FileEncodingError: "Could not read {filepath} with any of the following encodings"

The file uses an encoding not in your encoding list. Try adding more encodings:

```python
reader = CSVReader(
    encodings=[
        "utf-8", "utf-8-sig", "latin1", "cp1252", 
        "iso-8859-1", "shift_jis", "euc-jp", "big5"
    ]
)
df = reader.read("file.csv")
```

### Delimiter Not Detected Correctly

If the auto-detection chooses the wrong delimiter, explicitly specify it:

```python
reader = CSVReader(delimiters=["|", ";", "\t", ","])
df = reader.read("file.csv")
print(f"Used delimiter: {repr(reader.success_delimiter)}")
```

### Bad Lines Warnings

Enable bad line capture to identify and debug problematic rows:

```python
reader = CSVReader(verbose=True, capture_bad_lines=True)
df = reader.read("file.csv")
print(f"Found {len(reader.bad_lines)} bad lines")
for i, line in enumerate(reader.bad_lines[:10]):  # Show first 10
    print(f"Line {i}: {line}")
```

### Column Names Not Normalized Correctly

If accent removal doesn't work as expected:

```python
# Check original column names
df = reader.read("file.csv")
print(df.columns.tolist())

# Try explicit normalization with convert_case
normalized = reader.normalize_columns(df, convert_case="lower")
print(normalized.columns.tolist())
```

### Memory Issues with Large Files

If you encounter memory issues with very large CSVs:

```python
# Read in chunks using pandas parameters
df = reader.read("large_file.csv", nrows=100000)

# Or export in multiple parts
reader.export(
    df,
    method="excel_parts",
    filename_prefix="large",
    max_rows=500000
)
```

## Performance Tips

1. **Use `verbose=False` in production** - Debug output has overhead
2. **Specify encodings explicitly** if known - Reduces encoding attempts
3. **Specify delimiters explicitly** if known - Reduces delimiter attempts
4. **Use `capture_bad_lines=False` by default** - Exception handling has overhead
5. **For very large files**, consider splitting before processing
6. **Cache the reader instance** to reuse encoding/delimiter detection results

## Advanced: Creating Custom Readers

The architecture supports creating custom readers for other formats:

```python
from pandas_toolkit.io.interfaces import FileReader
import pandas as pd

class JSONReader(FileReader):
    """Custom reader for JSON files."""
    
    def _read(self, filepath: str, **kwargs) -> pd.DataFrame:
        """Implement JSON-specific reading logic."""
        return pd.read_json(filepath, **kwargs)

# Use it like any other reader
reader = JSONReader(output_dir="exports")
df = reader.read("data.json", normalize_columns=True)
reader.export(df, method="excel", filename="output.xlsx")
```

## Supported Encodings

UTF-8, UTF-8-SIG, CP1252, Latin-1, ISO-8859-1, UTF-16, UTF-16-LE, UTF-16-BE, UTF-32, UTF-32-LE, UTF-32-BE, CP1250, CP1251, CP1253, CP1254, CP932, Shift-JIS, EUC-JP, EUC-KR, Big5, GB2312, Mac-Roman, ASCII

## Supported Delimiters

Comma (,), Semicolon (;), Tab (\t), Pipe (|), Colon (:), Tilde (~), Caret (^), Hash (#), Space, Underscore (_), Hyphen (-), Forward Slash (/), Backslash (\), Asterisk (*), Equals (=), Single Quote ('), Double Quote (")

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure:
- All tests pass: `pytest tests/`
- Code is properly documented with docstrings
- Follow the existing code style and architecture