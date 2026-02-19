# CSVReader - Complete Guide

## Description

`CSVReader` is the most robust toolkit component for reading CSV files. It includes **automatic encoding detection** and **automatic delimiter detection**, making it ideal for processing problematic CSV files or files of unknown origin.

## Main Features

- ✅ **Automatic encoding detection** (UTF-8, Latin-1, Windows-1252, etc.)
- ✅ **Automatic delimiter detection** (`,`, `;`, `\t`, `|`)
- ✅ **Capture malformed lines** for later analysis
- ✅ **Data normalization** and column names
- ✅ **Batch processing** of multiple files
- ✅ **Export** to multiple formats
- ✅ **Robust error handling**

## Installing Dependencies

```bash
pip install pandas numpy
# Or install all project dependencies:
pip install -r requirements.txt
```

## Basic Usage

### Import the Reader

```python
from pandas_toolkit.io.readers import CSVReader
# Or using the factory
from pandas_toolkit.io.factory import ReaderFactory
```

### Simple Reading

```python
reader = CSVReader()

# Basic reading - automatic detection
df = reader.read("data.csv")

print(f"Shape: {df.shape}")
print(f"Detected encoding: {reader.success_encoding}")
print(f"Detected delimiter: {repr(reader.success_delimiter)}")
```

### Reading with Normalization

```python
reader = CSVReader(verbose=True)

# Read with full normalization
df = reader.read(
    "data.csv",
    normalize=True,              # Normalizes values (creates _norm columns)
    normalize_columns=True,      # Normalizes column names
    skip_leading_empty_rows=True,  # Skips empty rows at the beginning
    skip_trailing_empty_rows=True  # Skips empty rows at the end
)

print(df.columns.tolist())
```

## Automatic Detection

### Supported Encodings (default)

CSVReader automatically tries the following encodings:

```python
COMMON_ENCODINGS = [
    'utf-8',
    'latin1',
    'iso-8859-1',
    'cp1252',
    'windows-1252',
    'utf-16',
    'ascii'
]
```

### Supported Delimiters (default)

```python
COMMON_DELIMITERS = [
    ',',    # Comma (standard CSV)
    ';',    # Semicolon (European CSV)
    '\t',   # Tab (TSV)
    '|'     # Pipe
]
```

### Customize Detection

```python
# Custom encodings
reader = CSVReader(
    encodings=['utf-8', 'latin1'],  # Only these encodings
    verbose=True
)

# Custom delimiters
reader = CSVReader(
    delimiters=[',', ';', '|'],  # Only these delimiters
    verbose=True
)

# Both
reader = CSVReader(
    encodings=['utf-8', 'cp1252'],
    delimiters=[',', ';'],
    verbose=True
)
```

## CSVReader Methods

### 1. `read()` - Read CSV file

```python
reader = CSVReader()

df = reader.read(
    filepath="data.csv",
    normalize=False,                  # Normalize values
    normalize_columns=False,          # Normalize column names
    skip_leading_empty_rows=True,     # Skip empty rows at the beginning
    skip_trailing_empty_rows=True,    # Skip empty rows at the end
    # All pandas.read_csv parameters are supported:
    header=0,                         # Header row
    skiprows=None,                    # Rows to skip
    usecols=None,                     # Columns to read
    dtype=None,                       # Data types
    # ... etc
)
```

### 2. `read_multiple_files()` - Batch reading

```python
reader = CSVReader(verbose=True)

# Read all CSVs from a folder
files = reader.read_multiple_files(
    "data_folder/",
    normalize=True,
    normalize_columns=True
)

# Returns a dictionary {filename: DataFrame}
for filename, df in files.items():
    print(f"{filename}: {df.shape}")
```

### 3. `export()` - Export DataFrame

```python
reader = CSVReader(output_dir="exports")

df = reader.read("data.csv")

# Export to CSV
reader.export(df, method="csv", filename="output.csv")

# Export to Excel
reader.export(df, method="excel", filename="report.xlsx")

# Export to Parquet
reader.export(df, method="parquet", filename="data.parquet")

# Export to JSON
reader.export(df, method="json", filename="data.json")
```

## Handling Problematic Files

### Files with Unknown Encoding

```python
reader = CSVReader(verbose=True)

# The reader will automatically try all encodings
df = reader.read("problematic_file.csv")

print(f"✓ File read with encoding: {reader.success_encoding}")
```

### Files with Unknown Delimiter

```python
reader = CSVReader(verbose=True)

# The reader will automatically detect the delimiter
df = reader.read("unknown_file.txt")

print(f"✓ Delimiter detected: {repr(reader.success_delimiter)}")
```

### Files with Malformed Lines

```python
reader = CSVReader(
    capture_bad_lines=True,  # Captures problematic lines
    verbose=True
)

df = reader.read("file_with_errors.csv")

# Inspect problematic lines
if reader.bad_lines:
    print(f"Captured problematic lines: {len(reader.bad_lines)}")
    for line_num, line_content in reader.bad_lines:
        print(f"  Line {line_num}: {line_content}")
```

### Files with Empty Rows

```python
reader = CSVReader()

# Skip empty rows automatically
df = reader.read(
    "file_with_empty_rows.csv",
    skip_leading_empty_rows=True,   # Skip empty rows at the beginning
    skip_trailing_empty_rows=True   # Skip empty rows at the end
)
```

## Complete Example: Problematic File

```python
from pandas_toolkit.io.readers import CSVReader

# File with multiple problems:
# - Encoding desconocido
# - Delimitador desconocido
# - Líneas mal formateadas
# - Filas vacías
# - Nombres de columnas con acentos y espacios

print("=" * 70)
print("PROCESANDO ARCHIVO CSV PROBLEMÁTICO")
print("=" * 70)

reader = CSVReader(
    verbose=True,               # See the entire process
    capture_bad_lines=True,     # Capturar líneas problemáticas
    output_dir="exports"        # Carpeta de salida
)

# Read with all corrections
df = reader.read(
    "archivo_problematico.csv",
    normalize=True,                    # Normalizar valores
    normalize_columns=True,            # Normalizar nombres de columnas
    skip_leading_empty_rows=True,
    skip_trailing_empty_rows=True
)

# Información del proceso
print(f"\n✓ Archivo leído exitosamente!")
print(f"  • Encoding detectado: {reader.success_encoding}")
print(f"  • Delimiter detectado: {repr(reader.success_delimiter)}")
print(f"  • Shape: {df.shape[0]} filas × {df.shape[1]} columnas")
print(f"  • Columnas: {df.columns.tolist()}")

# Si hubo líneas problemáticas
if reader.bad_lines:
    print(f"\n⚠ Líneas problemáticas: {len(reader.bad_lines)}")
    for line_num, line_content in reader.bad_lines:
        print(f"  Línea {line_num}: {line_content[:100]}...")

# Vista previa
print("\n📋 Vista previa de los datos:")
print(df.head(3))

# Export clean data
reader.export(df, method="csv", filename="datos_limpios.csv")
reader.export(df, method="excel", filename="datos_limpios.xlsx")

print("\n✅ Datos exportados en: exports/")
```

## Batch Processing

### Process Multiple Files

```python
from pathlib import Path
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader(verbose=True, output_dir="exports")

# Método 1: Usar read_multiple_files
print("Método 1: read_multiple_files")
files = reader.read_multiple_files(
    "data_folder/",
    normalize=True,
    normalize_columns=True
)

for filename, df in files.items():
    print(f"\n{filename}:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {df.columns.tolist()}")
    
    # Export each processed file
    clean_filename = Path(filename).stem + "_clean.csv"
    reader.export(df, method="csv", filename=clean_filename)

# Método 2: Procesar manualmente
print("\nMétodo 2: Procesamiento manual")
data_folder = Path("data_folder")
csv_files = list(data_folder.glob("*.csv"))

for csv_file in csv_files:
    print(f"\nProcesando: {csv_file.name}")
    
    df = reader.read(
        str(csv_file),
        normalize=True,
        normalize_columns=True
    )
    
    print(f"  • Encoding: {reader.success_encoding}")
    print(f"  • Delimiter: {repr(reader.success_delimiter)}")
    print(f"  • Shape: {df.shape}")
    
    # Exportar
    output_name = f"{csv_file.stem}_processed.xlsx"
    reader.export(df, method="excel", filename=output_name)

print("\n✅ Procesamiento batch completado!")
```

## Common Use Cases

### Case 1: European CSV (semicolon)

```python
reader = CSVReader(verbose=True)

# Automatically detects ; as delimiter
df = reader.read("european_data.csv")

print(f"Detected delimiter: {repr(reader.success_delimiter)}")  # ';'
```

### Case 2: CSV with Latin-1 Encoding

```python
reader = CSVReader(verbose=True)

# Automatically detects latin-1
df = reader.read("spanish_data.csv")

print(f"Detected encoding: {reader.success_encoding}")  # 'latin1'
```

### Case 3: Column Normalization

```python
reader = CSVReader()

# File with columns: ["  Name  ", "Last Name", "Phone Number"]
df = reader.read(
    "data.csv",
    normalize_columns=True
)

print(df.columns.tolist())
# ['name', 'last_name', 'phone_number']
```

### Case 4: Value Normalization

```python
reader = CSVReader()

df = reader.read(
    "data.csv",
    normalize=True  # Creates _norm columns
)

# Original columns + _norm columns
print(df.columns.tolist())
# ['Name', 'Status', 'Name_norm', 'Status_norm']

# Normalized values (trim, lowercase)
print(df[['Status', 'Status_norm']].head())
```

## Using with Factory

```python
from pandas_toolkit.io.factory import ReaderFactory

# The factory automatically creates a CSVReader
reader = ReaderFactory.create_reader("data.csv", verbose=True)

df = reader.read("data.csv")

print(f"Reader type: {type(reader).__name__}")  # CSVReader
```

## Advanced Parameters

### Passing Parameters to pandas.read_csv

```python
reader = CSVReader()

df = reader.read(
    "data.csv",
    # Specific pandas parameters
    header=0,                   # Header row
    skiprows=[1, 2, 3],        # Skip specific rows
    usecols=['A', 'B', 'C'],   # Only these columns
    dtype={'A': str, 'B': int}, # Data types
    parse_dates=['date'],      # Parse dates
    na_values=['NA', 'N/A'],   # Additional null values
    thousands=',',              # Thousands separator
    decimal='.',                # Decimal separator
    comment='#',                # Comment lines
    # ... all pd.read_csv parameters
)
```

## Useful Attributes

After reading a file, you can access:

```python
reader = CSVReader()
df = reader.read("data.csv")

# Successful encoding
print(f"Encoding: {reader.success_encoding}")

# Successful delimiter
print(f"Delimiter: {repr(reader.success_delimiter)}")

# Problematic lines (if capture_bad_lines=True)
if hasattr(reader, 'bad_lines') and reader.bad_lines:
    print(f"Bad lines: {len(reader.bad_lines)}")

# Output directory
print(f"Output dir: {reader.output_dir}")
```

## Error Handling

### File Not Found

```python
reader = CSVReader()

try:
    df = reader.read("nonexistent_file.csv")
except FileNotFoundError as e:
    print(f"Error: {e}")
```

### File Without Compatible Encoding

```python
reader = CSVReader(
    encodings=['utf-8'],  # Only tries UTF-8
    verbose=True
)

try:
    df = reader.read("latin1_file.csv")
except Exception as e:
    print(f"Could not read with any encoding: {e}")
```

## Verbose Mode

```python
reader = CSVReader(verbose=True)

# Will show:
# [INFO] Trying encoding='utf-8', delimiter=','
# [INFO] Successfully read with encoding='utf-8', delimiter=','
# [INFO] Loaded 1000 rows, 5 columns

df = reader.read("data.csv")
```

## Comparison with Native pandas

### With native pandas:

```python
import pandas as pd

# You have to specify everything manually
df = pd.read_csv(
    "data.csv",
    encoding='utf-8',  # You have to guess
    delimiter=',',      # You have to guess
    on_bad_lines='skip' # Loses problematic lines
)
```

### With CSVReader:

```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader(
    capture_bad_lines=True,  # Captures problematic lines
    verbose=True             # See the entire process
)

# Automatic detection of encoding and delimiter
df = reader.read("data.csv")

# Advantages:
# - No need to guess encoding or delimiter
# - Capture problematic lines for analysis
# - Integrated normalization
# - Direct export to multiple formats
# - Built-in batch processing
```

## Tips and Best Practices

### 1. Always use verbose during development

```python
# During development
reader = CSVReader(verbose=True)

# In production
reader = CSVReader(verbose=False)
```

### 2. Capture bad lines on critical files

```python
reader = CSVReader(capture_bad_lines=True)

df = reader.read("important_data.csv")

# Check for problems
if reader.bad_lines:
    print(f"⚠ {len(reader.bad_lines)} problematic lines")
    # Analyze or report
```

### 3. Always normalize when working with multiple sources

```python
reader = CSVReader()

# Normalize for consistency
df = reader.read(
    "data_from_multiple_sources.csv",
    normalize=True,
    normalize_columns=True
)
```

### 4. Use batch processing for efficiency

```python
reader = CSVReader()

# Process all files at once
files = reader.read_multiple_files("data_folder/", normalize=True)
```

## Troubleshooting

### Problem: "UnicodeDecodeError"

**Solution**: Add more encodings to try

```python
reader = CSVReader(
    encodings=['utf-8', 'latin1', 'cp1252', 'iso-8859-1'],
    verbose=True
)
```

### Problem: "Columns don't match"

**Solution**: The delimiter is misdetected

```python
reader = CSVReader(
    delimiters=[';', ',', '\t', '|'],  # Try more options
    verbose=True
)
```

### Problem: "Too many columns"

**Solution**: There are delimiters in the data

```python
reader = CSVReader()

df = reader.read(
    "data.csv",
    quotechar='"',     # Use quotes to escape
    quoting=1          # QUOTE_ALL
)
```

## Compatibility

- ✅ Python 3.7+
- ✅ pandas 2.0+
- ✅ Windows, Linux, macOS

## Additional Examples

See also:
- [`test_csv_reader.py`](../tests/test_csv_reader.py) - Unit tests
- [`Tests_CSVReader.ipynb`](../Testeos%20Jupyter/Tests_CSVReader.ipynb) - Interactive examples

## Support

To report bugs or request features, open an issue in the repository.
