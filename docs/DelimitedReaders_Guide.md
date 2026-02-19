# Delimiter Readers - Complete Guide
## TSVReader and PipeReader

## Description

`TSVReader` and `PipeReader` are specialized readers for tab-delimited and pipe-delimited files respectively. Both inherit from `DelimitedTextReader`, providing the same **automatic encoding detection** capabilities as `CSVReader`.

## Main Features

- ✅ **TSVReader**: Tab-delimited files (`\t`)
- ✅ **PipeReader**: Pipe-delimited files (`|`)
- ✅ **Automatic encoding detection**
- ✅ **Capture malformed lines**
- ✅ **Data normalization** and column names
- ✅ **Batch processing**
- ✅ **Export** to multiple formats

## Installing Dependencies

```bash
pip install pandas numpy
# Or install all project dependencies:
pip install -r requirements.txt
```

---

## TSVReader

### Description

`TSVReader` is optimized for reading **TSV (Tab-Separated Values)** files, a common format for database exports and analysis tools.

### Basic Usage

```python
from pandas_toolkit.io.readers import TSVReader

reader = TSVReader()

# Basic reading
df = reader.read("data.tsv")

print(f"Shape: {df.shape}")
print(f"Detected encoding: {reader.success_encoding}")
print(f"Delimiter: {repr(reader.success_delimiter)}")  # '\t'
```

### Read with Normalization

```python
reader = TSVReader(verbose=True)

df = reader.read(
    "datos.tsv",
    normalize=True,              # Normalize values
    normalize_columns=True,      # Normalize column names
    skip_leading_empty_rows=True,
    skip_trailing_empty_rows=True
)

print(df.columns.tolist())
```

### Complete Example: TSV File

```python
from pandas_toolkit.io.readers import TSVReader

print("=" * 70)
print("PROCESSING TSV FILE")
print("=" * 70)

reader = TSVReader(
    verbose=True,
    capture_bad_lines=True,
    output_dir="exports"
)

# Read TSV file
df = reader.read(
    "database_export.tsv",
    normalize=True,
    normalize_columns=True
)

print(f"\n✓ TSV file read successfully!")
print(f"  • Encoding: {reader.success_encoding}")
print(f"  • Delimiter: {repr(reader.success_delimiter)}")
print(f"  • Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"  • Columns: {df.columns.tolist()}")

# Preview
print(f"\n📋 Preview:")
print(df.head(3))

# Export
reader.export(df, method="csv", filename="datos_desde_tsv.csv")
reader.export(df, method="excel", filename="datos_desde_tsv.xlsx")

print("\n✅ Data exported!")
```

### Customize TSVReader

```python
# With custom encodings
reader = TSVReader(
    encodings=['utf-8', 'latin1', 'cp1252'],
    verbose=True
)

# With additional delimiters (if you need to test more)
reader = TSVReader(
    delimiters=['\t', '|'],  # Try tab first, then pipe
    verbose=True
)
```

### TSV Use Cases

#### 1. MySQL/PostgreSQL Export

```python
reader = TSVReader(verbose=True)

# Typical DB export
df = reader.read("mysql_export.tsv")

print(f"DB records loaded: {df.shape[0]}")
```

#### 2. Excel Export as TSV

```python
reader = TSVReader()

# When you save Excel as "Text (Tab delimited)"
df = reader.read("excel_saved_as_tsv.txt")

print(f"Excel data: {df.shape}")
```

#### 3. System Logs

```python
reader = TSVReader()

# Many logs use tabs
df = reader.read("system_logs.tsv")

print(f"Log entries: {len(df)}")
```

---

## PipeReader

### Description

`PipeReader` is optimized for reading **pipe-delimited** files (`|`), a common format in data warehouses and legacy systems.

### Basic Usage

```python
from pandas_toolkit.io.readers import PipeReader

reader = PipeReader()

# Basic reading
df = reader.read("datos.pipe")

print(f"Shape: {df.shape}")
print(f"Detected encoding: {reader.success_encoding}")
print(f"Delimiter: {repr(reader.success_delimiter)}")  # '|'
```

### Read with Normalization

```python
reader = PipeReader(verbose=True)

df = reader.read(
    "datos.pipe",
    normalize=True,
    normalize_columns=True,
    skip_leading_empty_rows=True,
    skip_trailing_empty_rows=True
)

print(df.columns.tolist())
```

### Complete Example: Pipe File

```python
from pandas_toolkit.io.readers import PipeReader

print("=" * 70)
print("PROCESSING PIPE-DELIMITED FILE")
print("=" * 70)

reader = PipeReader(
    verbose=True,
    capture_bad_lines=True,
    output_dir="exports"
)

# Read pipe-delimited file
df = reader.read(
    "warehouse_data.pipe",
    normalize=True,
    normalize_columns=True
)

print(f"\n✓ File read successfully!")
print(f"  • Encoding: {reader.success_encoding}")
print(f"  • Delimiter: {repr(reader.success_delimiter)}")
print(f"  • Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"  • Columns: {df.columns.tolist()}")

# Preview
print(f"\n📋 Preview:")
print(df.head(3))

# Export to more common format
reader.export(df, method="csv", filename="datos_desde_pipe.csv")
reader.export(df, method="excel", filename="datos_desde_pipe.xlsx")

print("\n✅ Data converted and exported!")
```

### Customize PipeReader

```python
# With custom encodings
reader = PipeReader(
    encodings=['utf-8', 'latin1'],
    verbose=True
)

# With additional delimiters
reader = PipeReader(
    delimiters=['|', '¦'],  # Normal pipe and broken bar
    verbose=True
)
```

### Pipe Use Cases

#### 1. Data Warehouse Exports

```python
reader = PipeReader(verbose=True)

# Typical data warehouse format
df = reader.read("dw_extract.pipe")

print(f"DW records: {df.shape[0]}")
```

#### 2. Legacy Systems

```python
reader = PipeReader()

# Many old systems use pipe
df = reader.read("legacy_system_export.dat")

print(f"Legacy data: {df.shape}")
```

#### 3. ETL Intermediate Files

```python
reader = PipeReader()

# Archivos intermedios de ETL
df = reader.read("etl_staging.pipe")

print(f"Staging records: {len(df)}")
```

---

## Common Methods

Both readers share the same methods:

### 1. `read()` - Read file

```python
reader = TSVReader()  # or PipeReader()

df = reader.read(
    filepath="datos.tsv",
    normalize=False,
    normalize_columns=False,
    skip_leading_empty_rows=True,
    skip_trailing_empty_rows=True,
    # All pandas.read_csv parameters
    header=0,
    skiprows=None,
    usecols=None,
    dtype=None,
)
```

### 2. `read_multiple_files()` - Batch

```python
reader = TSVReader(verbose=True)  # or PipeReader()

files = reader.read_multiple_files(
    "data_folder/",
    normalize=True,
    normalize_columns=True
)

for filename, df in files.items():
    print(f"{filename}: {df.shape}")
```

### 3. `export()` - Export

```python
reader = TSVReader(output_dir="exports")  # or PipeReader()

df = reader.read("datos.tsv")

reader.export(df, method="csv", filename="output.csv")
reader.export(df, method="excel", filename="output.xlsx")
reader.export(df, method="parquet", filename="output.parquet")
```

---

## Format Conversion Example

```python
from pandas_toolkit.io.readers import TSVReader, PipeReader, CSVReader

print("=" * 70)
print("CONVERSION BETWEEN DELIMITED FORMATS")
print("=" * 70)

output_dir = "exports"

# 1. TSV to CSV
print("\n1. TSV → CSV")
tsv_reader = TSVReader(verbose=True, output_dir=output_dir)
df_tsv = tsv_reader.read("datos.tsv")
tsv_reader.export(df_tsv, method="csv", filename="tsv_to_csv.csv")
print(f"   ✓ {df_tsv.shape[0]} records converted")

# 2. Pipe to CSV
print("\n2. Pipe → CSV")
pipe_reader = PipeReader(verbose=True, output_dir=output_dir)
df_pipe = pipe_reader.read("datos.pipe")
pipe_reader.export(df_pipe, method="csv", filename="pipe_to_csv.csv")
print(f"   ✓ {df_pipe.shape[0]} records converted")

# 3. CSV to TSV (save manually)
print("\n3. CSV → TSV")
csv_reader = CSVReader(verbose=True, output_dir=output_dir)
df_csv = csv_reader.read("datos.csv")
df_csv.to_csv(f"{output_dir}/csv_to_tsv.tsv", sep='\t', index=False)
print(f"   ✓ {df_csv.shape[0]} records converted")

# 4. CSV to Pipe (save manually)
print("\n4. CSV → Pipe")
df_csv.to_csv(f"{output_dir}/csv_to_pipe.pipe", sep='|', index=False)
print(f"   ✓ {df_csv.shape[0]} records converted")

print("\n✅ All conversions completed!")
```

---

## Batch Processing

```python
from pathlib import Path
from pandas_toolkit.io.readers import TSVReader, PipeReader

print("=" * 70)
print("BATCH PROCESSING OF DELIMITED FILES")
print("=" * 70)

output_dir = "exports"

# Process all TSV files
print("\n📁 Processing TSV files...")
tsv_reader = TSVReader(verbose=True, output_dir=output_dir)
tsv_files = list(Path("data_folder").glob("*.tsv"))

for tsv_file in tsv_files:
    print(f"\n  {tsv_file.name}")
    df = tsv_reader.read(str(tsv_file), normalize=True)
    print(f"    Shape: {df.shape}")
    
    # Convert to CSV
    output_name = f"{tsv_file.stem}.csv"
    tsv_reader.export(df, method="csv", filename=output_name)
    print(f"    ✓ Converted to CSV")

# Process all Pipe files
print("\n📁 Processing Pipe files...")
pipe_reader = PipeReader(verbose=True, output_dir=output_dir)
pipe_files = list(Path("data_folder").glob("*.pipe"))

for pipe_file in pipe_files:
    print(f"\n  {pipe_file.name}")
    df = pipe_reader.read(str(pipe_file), normalize=True)
    print(f"    Shape: {df.shape}")
    
    # Convert to Excel
    output_name = f"{pipe_file.stem}.xlsx"
    pipe_reader.export(df, method="excel", filename=output_name)
    print(f"    ✓ Converted to Excel")

print("\n✅ Batch processing completed!")
```

---

## Using with Factory

```python
from pandas_toolkit.io.factory import ReaderFactory

# TSV
tsv_reader = ReaderFactory.create_reader("datos.tsv", verbose=True)
df_tsv = tsv_reader.read("datos.tsv")
print(f"Type: {type(tsv_reader).__name__}")  # TSVReader

# Pipe
pipe_reader = ReaderFactory.create_reader("datos.pipe", verbose=True)
df_pipe = pipe_reader.read("datos.pipe")
print(f"Type: {type(pipe_reader).__name__}")  # PipeReader
```

---

## Useful Attributes

```python
reader = TSVReader()  # or PipeReader()
df = reader.read("datos.tsv")

# Detected encoding
print(f"Encoding: {reader.success_encoding}")

# Delimiter used
print(f"Delimiter: {repr(reader.success_delimiter)}")

# Problematic lines (if capture_bad_lines=True)
if hasattr(reader, 'bad_lines') and reader.bad_lines:
    print(f"Bad lines: {len(reader.bad_lines)}")
```

---

## Comparación: TSV vs Pipe vs CSV

| Characteristic | TSV | Pipe | CSV |
|----------------|-----|------|-----|
| Delimiter | `\t` (tab) | `\|` (pipe) | `,` (comma) |
| Common use | DB exports, logs | DW, legacy | General purpose |
| Advantage | Rare in data | Rare in data | Standard |
| Disadvantage | Invisible | Can appear in data | Common in text |

---

## Tips and Best Practices

### 1. Verify delimiter visually

```python
# For TSV, verify they are really tabs
with open("datos.tsv", 'r') as f:
    first_line = f.readline()
    print(repr(first_line))  # You'll see '\t' if they are real tabs
```

### 2. Use verbose during development

```python
# During development
reader = TSVReader(verbose=True)

# In production
reader = TSVReader(verbose=False)
```

### 3. Convert to standard format

```python
# Convert TSV/Pipe to CSV for compatibility
reader = TSVReader(output_dir="exports")
df = reader.read("datos.tsv")
reader.export(df, method="csv", filename="datos.csv")
```

---

## Troubleshooting

### Problem: "Columns don't match"

**Solution**: Verify real delimiter

```python
# The file may not use the expected delimiter
reader = TSVReader(
    delimiters=['\t', ',', '|', ';'],  # Try multiple
    verbose=True
)
```

### Problem: "UnicodeDecodeError"

**Solution**: Add more encodings

```python
reader = TSVReader(
    encodings=['utf-8', 'latin1', 'cp1252', 'iso-8859-1'],
    verbose=True
)
```

---

## Compatibility

- ✅ Python 3.7+
- ✅ pandas 2.0+
- ✅ Windows, Linux, macOS

---

## Additional Examples

See also:
- [`CSVReader_Guide.md`](CSVReader_Guide.md) - For more details about delimiters
- Unit tests in `tests/`

---

## Support

To report bugs or request features, open an issue in the repository.
