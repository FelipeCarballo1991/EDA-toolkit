# EDA-toolkit - CSVReader

A robust Python library for reading, processing, and exporting CSV files with automatic encoding detection, delimiter discovery, and data normalization capabilities.

## Features

### 🔍 Automatic Encoding Detection
- Tries multiple encodings automatically (UTF-8, Latin-1, CP1252, etc.)
- Gracefully handles files with mixed or uncommon encodings
- Supports 20+ encoding formats out of the box

### 🎯 Delimiter Auto-Detection
- Automatically detects the correct delimiter used in your CSV file
- Supports common delimiters: comma, semicolon, tab, pipe, and more
- Customizable delimiter lists for specific use cases

### 🛡️ Bad Line Detection
- Detects and captures malformed lines during file reading
- Optional logging of problematic lines for debugging
- Configurable behavior for handling corrupt data

### 📊 Data Normalization
- Normalize column names (remove accents, standardize casing, handle duplicates)
- Normalize cell values (trim whitespace, convert empty strings to None)
- Drop empty rows and columns automatically
- Create normalized versions without overwriting original data

### 📁 Batch Operations
- Read multiple CSV files from a directory at once
- Export to multiple formats: CSV, Excel (single sheet, multiple parts, or multiple sheets)
- Handle large datasets by splitting across multiple Excel files

### 🔄 Export Flexibility
- Export to CSV format
- Export to Excel with single or multiple sheets
- Split large DataFrames across multiple Excel files (useful for Excel's row limits)
- Customizable output directory and verbose logging

## Installation

```bash
pip install -r requirements.txt
```

### Requirements
- pandas >= 2.3.1
- numpy >= 2.3.1
- openpyxl >= 3.1.5

## Quick Start

### Basic Reading

```python
from pandas_toolkit.io import CSVReader

# Create a reader instance
reader = CSVReader()

# Read a CSV file (encoding and delimiter are auto-detected)
df = reader.read("path/to/file.csv")
```

### Reading with Encoding Detection

```python
# Specify custom encodings to try
reader = CSVReader(encodings=["utf-8", "latin1", "cp1252"])
df = reader.read("path/to/file.csv")
```

### Reading with Custom Delimiters

```python
# Specify custom delimiters to try
reader = CSVReader(delimiters=[";", "\t", "|"])
df = reader.read("path/to/file.csv")
```

### Bad Line Detection

```python
# Enable bad line capture for debugging
reader = CSVReader(verbose=True, capture_bad_lines=True)
df = reader.read("path/to/problematic_file.csv")

# Access captured bad lines
print(reader.bad_lines)
```

## Usage Examples

### Normalize and Read in One Step

```python
reader = CSVReader(verbose=True)

# Read file and normalize cell values in one call
df = reader.read_and_normalize("data.csv")

# The returned DataFrame contains original columns plus normalized versions
# (columns with "_norm" suffix)
print(df.columns)
# Output: ['col1', 'col2', 'col1_norm', 'col2_norm']
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
# (useful if DataFrame exceeds Excel's row limit)
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
    encodings=["utf-8", "utf-8-sig", "latin1", "cp1252"],
    delimiters=[",", ";", "\t", "|"],
    verbose=True,                          # Print debug information
    capture_bad_lines=True,               # Capture malformed lines
    output_dir="outputs"                  # Directory for exports
)

# Read file with encoding/delimiter auto-detection
df = reader.read("raw_data.csv")

# Normalize column names
df = reader.normalize_columns(df, convert_case="lower")

# Normalize cell values
df = reader.normalize(df, drop_empty_cols=True, drop_empty_rows=True)

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

## API Reference

### CSVReader Class

#### Constructor

```python
CSVReader(
    encodings=None,           # List of encodings to try
    delimiters=None,          # List of delimiters to try
    verbose=False,            # Enable debug output
    capture_bad_lines=False,  # Capture malformed lines
    output_dir=".",           # Output directory for exports
    exporter=None            # Custom FileExporter instance
)
```

#### Methods

| Method | Description |
|--------|-------------|
| `read(filepath, **kwargs)` | Read a CSV file with auto-detection |
| `read_and_normalize(filepath, **kwargs)` | Read and normalize in one step |
| `read_multiple_files(folderpath, **kwargs)` | Read all CSV files in a directory |
| `normalize(df, **kwargs)` | Normalize cell values in a DataFrame |
| `normalize_columns(df, **kwargs)` | Normalize column names |
| `export(df, method, **kwargs)` | Export DataFrame to various formats |

## Common Use Cases

### Use Case 1: Clean and Standardize a CSV File

```python
reader = CSVReader(verbose=True, output_dir="cleaned_data")

# Read with auto-detection
df = reader.read("messy_data.csv")

# Normalize everything
df = reader.normalize_columns(df, convert_case="lower")
df = reader.normalize(df)

# Export cleaned version
reader.export(df, method="excel", filename="clean_data.xlsx")
```

### Use Case 2: Merge Multiple CSV Files

```python
reader = CSVReader(output_dir="merged_data")

# Read all files from a folder
files = reader.read_multiple_files("raw_data_folder/")

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

## Troubleshooting

### FileEncodingError: "We can't encode {filepath}"

The file uses an encoding not in your encoding list. Try:

```python
reader = CSVReader(
    encodings=[
        "utf-8", "utf-8-sig", "latin1", "cp1252", 
        "iso-8859-1", "shift_jis", "euc-jp"
    ]
)
df = reader.read("file.csv")
```

### Delimiter Not Detected Correctly

Add the correct delimiter explicitly:

```python
reader = CSVReader(delimiters=["|", ";", "\t", ","])
df = reader.read("file.csv")
```

### Bad Lines Warnings

Enable bad line capture to identify problematic rows:

```python
reader = CSVReader(verbose=True, capture_bad_lines=True)
df = reader.read("file.csv")
print(f"Found {len(reader.bad_lines)} bad lines")
for line in reader.bad_lines[:5]:  # Show first 5
    print(line)
```

## License

See LICENSE file for details.