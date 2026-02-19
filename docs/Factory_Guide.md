# ReaderFactory - Complete Guide

## Description

`ReaderFactory` is a component that implements the **Factory pattern** to automatically create the correct reader based on file extension. It simplifies toolkit usage by not having to manually select the appropriate reader.

## Main Features

- ✅ **Automatic detection** of reader by file extension
- ✅ **Support for all formats** in the toolkit
- ✅ **Simple and consistent API**
- ✅ **Extensible** for new readers
- ✅ **Error handling** for unsupported extensions

## Supported Formats

| Extension | Created Reader | Description |
|-----------|---------------|-------------|
| `.csv` | CSVReader | CSV files |
| `.tsv` | TSVReader | TSV files (Tab-separated) |
| `.txt` | CSVReader | Text files (uses CSV by default) |
| `.dat` | CSVReader | Data files (uses CSV by default) |
| `.xlsx` | ExcelReader | Modern Excel |
| `.xls` | ExcelReader | Old Excel |
| `.json` | JSONReader | Standard JSON |
| `.jsonl` | JSONReader | JSON Lines |
| `.pipe` | PipeReader | Pipe-delimited |
| `.html` | HTMLReader | HTML with tables |
| `.htm` | HTMLReader | HTML with tables |

## Basic Usage

### Import the Factory

```python
from pandas_toolkit.io.factory import ReaderFactory
```

### Create Reader Automatically

```python
# The factory automatically detects the file type
factory = ReaderFactory()

# CSV
reader = factory.create_reader("datos.csv")
df = reader.read("datos.csv")

# Excel
reader = factory.create_reader("reporte.xlsx")
df = reader.read("reporte.xlsx")

# JSON
reader = factory.create_reader("api_data.json")
df = reader.read("api_data.json")

# HTML
reader = factory.create_reader("oracle_export.html")
df = reader.read("oracle_export.html")
```

### No Need to Know the Reader

```python
from pandas_toolkit.io.factory import ReaderFactory

# User doesn't need to know which reader to use
archivo = "datos_desconocidos.csv"  # Could be .xlsx, .json, etc.

# Factory handles it automatically
reader = ReaderFactory.create_reader(archivo, verbose=True)
df = reader.read(archivo)

print(f"Reader used: {type(reader).__name__}")
print(f"Data loaded: {df.shape}")
```

## Factory Methods

### 1. `create_reader()` - Create Reader

```python
factory = ReaderFactory()

reader = factory.create_reader(
    filepath="datos.csv",        # File path
    output_dir="exports",        # Output directory
    verbose=False,               # Verbose mode
    **kwargs                     # Additional arguments for the reader
)

# Type-specific kwargs:
# - CSVReader: encodings, delimiters, capture_bad_lines
# - ExcelReader: engines
# - etc.
```

### 2. `get_supported_extensions()` - View Supported Extensions

```python
factory = ReaderFactory()

extensions = factory.get_supported_extensions()
print("Supported extensions:")
for ext in extensions:
    print(f"  {ext}")

# Output:
# Supported extensions:
#   .csv
#   .dat
#   .html
#   .htm
#   .json
#   .jsonl
#   .pipe
#   .tsv
#   .txt
#   .xls
#   .xlsx
```

## Complete Example: Universal Processing

```python
from pandas_toolkit.io.factory import ReaderFactory
from pathlib import Path

print("=" * 70)
print("UNIVERSAL FILE PROCESSING")
print("=" * 70)

factory = ReaderFactory()

# Files of different formats
archivos = [
    "datos.csv",
    "reporte.xlsx",
    "api_response.json",
    "database.tsv",
    "warehouse.pipe",
    "oracle_export.html"
]

for archivo in archivos:
    print(f"\n{'='*70}")
    print(f"Processing: {archivo}")
    print('='*70)
    
    try:
        # Factory creates the correct reader automatically
        reader = factory.create_reader(archivo, verbose=True, output_dir="exports")
        
        print(f"  • Reader: {type(reader).__name__}")
        
        # Read with normalization
        df = reader.read(
            archivo,
            normalize=True,
            normalize_columns=True
        )
        
        print(f"  • Shape: {df.shape}")
        print(f"  • Columns: {df.columns.tolist()[:5]}...")  # First 5
        
        # Export to unified format
        base_name = Path(archivo).stem
        reader.export(df, method="csv", filename=f"{base_name}_processed.csv")
        reader.export(df, method="excel", filename=f"{base_name}_processed.xlsx")
        
        print(f"  ✓ Processed and exported successfully")
        
    except ValueError as e:
        print(f"  ✗ Error: {e}")
    except FileNotFoundError:
        print(f"  ✗ File not found")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")

print("\n" + "=" * 70)
print("✅ PROCESSING COMPLETED")
print("=" * 70)
```

## Example: Universal Folder Processor

```python
from pandas_toolkit.io.factory import ReaderFactory
from pathlib import Path

def process_folder(folder_path, output_dir="exports"):
    """
    Processes all supported files in a folder.
    """
    print("=" * 70)
    print(f"PROCESSING FOLDER: {folder_path}")
    print("=" * 70)
    
    factory = ReaderFactory()
    supported = factory.get_supported_extensions()
    
    # Search for all files with supported extensions
    folder = Path(folder_path)
    archivos_procesados = 0
    archivos_fallidos = 0
    
    for archivo in folder.iterdir():
        if archivo.is_file() and archivo.suffix.lower() in supported:
            print(f"\n📄 {archivo.name}")
            
            try:
                # Create appropriate reader
                reader = factory.create_reader(
                    str(archivo),
                    verbose=False,
                    output_dir=output_dir
                )
                
                # Read and normalize
                df = reader.read(
                    str(archivo),
                    normalize=True,
                    normalize_columns=True
                )
                
                print(f"  ✓ Read: {df.shape[0]} rows × {df.shape[1]} columns")
                print(f"  ✓ Reader: {type(reader).__name__}")
                
                # Export to CSV (unified format)
                output_name = f"{archivo.stem}_normalized.csv"
                reader.export(df, method="csv", filename=output_name)
                
                archivos_procesados += 1
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                archivos_fallidos += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Processed: {archivos_procesados}")
    print(f"❌ Failed: {archivos_fallidos}")
    print("=" * 70)
    
    return archivos_procesados, archivos_fallidos


# Use the function
if __name__ == "__main__":
    procesados, fallidos = process_folder("data_folder", output_dir="exports")
```

## Advanced Usage

### Pass Specific Parameters to Reader

```python
factory = ReaderFactory()

# For CSVReader - specify encodings
reader = factory.create_reader(
    "datos.csv",
    verbose=True,
    encodings=['utf-8', 'latin1'],  # CSVReader-specific parameter
    capture_bad_lines=True
)

# For ExcelReader - specify engines
reader = factory.create_reader(
    "reporte.xlsx",
    verbose=True,
    engines={'.xlsx': ['openpyxl']}  # ExcelReader-specific parameter
)

# For HTMLReader - no additional parameters needed
reader = factory.create_reader(
    "oracle.html",
    verbose=True
)
```

### Validate Extension Before Processing

```python
from pathlib import Path
from pandas_toolkit.io.factory import ReaderFactory

def is_supported_file(filepath):
    """Verifies if a file is supported by the factory."""
    factory = ReaderFactory()
    supported = factory.get_supported_extensions()
    extension = Path(filepath).suffix.lower()
    return extension in supported


# Use the function
archivo = "datos.csv"

if is_supported_file(archivo):
    reader = ReaderFactory.create_reader(archivo)
    df = reader.read(archivo)
    print(f"✓ File processed: {df.shape}")
else:
    print(f"✗ Format not supported: {Path(archivo).suffix}")
```

## Example: Universal CLI Tool

```python
"""
CLI script to process any supported file.

Usage:
    python process_file.py datos.csv
    python process_file.py reporte.xlsx
    python process_file.py api_data.json
"""

import sys
from pathlib import Path
from pandas_toolkit.io.factory import ReaderFactory


def main():
    if len(sys.argv) < 2:
        print("Usage: python process_file.py <file>")
        print("\nSupported formats:")
        factory = ReaderFactory()
        for ext in factory.get_supported_extensions():
            print(f"  {ext}")
        sys.exit(1)
    
    archivo = sys.argv[1]
    
    if not Path(archivo).exists():
        print(f"❌ Error: File not found: {archivo}")
        sys.exit(1)
    
    print("=" * 70)
    print("UNIVERSAL FILE PROCESSOR")
    print("=" * 70)
    print(f"\nFile: {archivo}")
    
    try:
        # Create appropriate reader automatically
        factory = ReaderFactory()
        reader = factory.create_reader(archivo, verbose=True, output_dir="output")
        
        print(f"Reader: {type(reader).__name__}")
        
        # Read with normalization
        df = reader.read(
            archivo,
            normalize=True,
            normalize_columns=True
        )
        
        print(f"\n📊 Data loaded:")
        print(f"  • Rows: {df.shape[0]}")
        print(f"  • Columns: {df.shape[1]}")
        print(f"  • Columns: {df.columns.tolist()}")
        
        # Preview
        print(f"\n📋 Preview (first 5 rows):")
        print(df.head().to_string())
        
        # Ask for output format
        print(f"\n💾 Export to:")
        print("  1. CSV")
        print("  2. Excel")
        print("  3. Both")
        print("  4. Don't export")
        
        opcion = input("\nOption (1-4): ").strip()
        
        base_name = Path(archivo).stem
        
        if opcion in ['1', '3']:
            reader.export(df, method="csv", filename=f"{base_name}_processed.csv")
            print(f"  ✓ Exported: output/{base_name}_processed.csv")
        
        if opcion in ['2', '3']:
            reader.export(df, method="excel", filename=f"{base_name}_processed.xlsx")
            print(f"  ✓ Exported: output/{base_name}_processed.xlsx")
        
        print("\n✅ Process completed!")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("The file format is not supported.")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Error Handling

### Unsupported Extension

```python
factory = ReaderFactory()

try:
    reader = factory.create_reader("archivo.doc")
except ValueError as e:
    print(f"Error: {e}")
    # Error: Unsupported file extension: .doc
    # Supported extensions: .csv, .tsv, .xlsx, ...
    
    # View supported extensions
    supported = factory.get_supported_extensions()
    print(f"Supported extensions: {supported}")
```

### File Not Found

```python
factory = ReaderFactory()

try:
    reader = factory.create_reader("inexistente.csv")
    df = reader.read("inexistente.csv")
except FileNotFoundError as e:
    print(f"Error: {e}")
```

## Comparison: With vs Without Factory

### Without Factory (Manual)

```python
from pandas_toolkit.io.readers import CSVReader, ExcelReader, JSONReader

# You have to know which reader to use
archivo = "datos.csv"

if archivo.endswith('.csv'):
    reader = CSVReader()
elif archivo.endswith('.xlsx'):
    reader = ExcelReader()
elif archivo.endswith('.json'):
    reader = JSONReader()
else:
    raise ValueError("Format not supported")

df = reader.read(archivo)
```

### With Factory (Automatic)

```python
from pandas_toolkit.io.factory import ReaderFactory

# Factory handles it automatically
archivo = "datos.csv"  # Or .xlsx, .json, etc.

reader = ReaderFactory.create_reader(archivo)
df = reader.read(archivo)
```

## Advantages of Factory Pattern

1. **Simplicity**: You don't need to know which reader to use
2. **Flexibility**: Works with any supported format
3. **Maintainability**: Adding new readers is centralized
4. **Consistency**: Uniform API for all formats
5. **Scalability**: Easy to extend with new formats

## Extending the Factory (Advanced)

If you create a new reader, you can register it in the factory:

```python
# In factory.py
from pandas_toolkit.io.readers import MyCustomReader

class ReaderFactory:
    READER_MAP = {
        # ... existing ...
        ".custom": MyCustomReader,  # Add new reader
    }
```

## Tips and Best Practices

### 1. Validate extensions first

```python
factory = ReaderFactory()
supported = factory.get_supported_extensions()

if archivo.suffix.lower() in supported:
    reader = factory.create_reader(archivo)
else:
    print(f"Format not supported: {archivo.suffix}")
```

### 2. Use factory for generic tools

```python
# For scripts that accept any format
def process_any_file(filepath):
    factory = ReaderFactory()
    reader = factory.create_reader(filepath, verbose=True)
    return reader.read(filepath, normalize=True)
```

### 3. Combine with try-except for robustness

```python
factory = ReaderFactory()

try:
    reader = factory.create_reader(archivo)
    df = reader.read(archivo)
except ValueError:
    print("Format not supported")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Error: {e}")
```

## Compatibility

- ✅ Python 3.7+
- ✅ pandas 2.0+
- ✅ All toolkit readers
- ✅ Windows, Linux, macOS

## See Also

- [CSVReader_Guide.md](CSVReader_Guide.md)
- [ExcelReader_Guide.md](ExcelReader_Guide.md)
- [JSONReader_Guide.md](JSONReader_Guide.md)
- [HTMLReader_Guide.md](HTMLReader_Guide.md)
- [DelimitedReaders_Guide.md](DelimitedReaders_Guide.md)

## Support

To report bugs or request features, open an issue in the repository.
