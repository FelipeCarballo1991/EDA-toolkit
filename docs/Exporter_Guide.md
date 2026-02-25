# FileExporter - Complete Guide

## Description

`FileExporter` is the component responsible for exporting DataFrames to different formats. All readers include a `FileExporter` instance, providing consistent export capabilities throughout the toolkit.

## Main Features

- ✅ **Export to CSV** - Delimited text files
- ✅ **Export to Excel** - One or multiple files/sheets
- ✅ **Export to Parquet** - Efficient columnar format
- ✅ **Export to JSON** - Multiple orientations
- ✅ **Automatic splitting** for large files
- ✅ **Automatic directory handling**

## Export Methods

| Method | Description | Usage |
|--------|-------------|-----|
| `csv` | One CSV file | Small/medium files |
| `excel` | One Excel file (one sheet) | Standard reports |
| `excel_parts` | Multiple Excel files | Very large datasets |
| `excel_sheets` | One file, multiple sheets | Large datasets |
| `parquet` | Parquet file | Big Data, efficient storage |
| `json` | JSON file | APIs, data exchange |

## Basic Usage

### Import and Create Exporter

```python
from pandas_toolkit.io.exporter import FileExporter
import pandas as pd

# Create example DataFrame
df = pd.DataFrame({
    'name': ['John', 'Mary', 'Peter'],
    'age': [30, 25, 35],
    'city': ['Madrid', 'Barcelona', 'Valencia']
})

# Create exporter
exporter = FileExporter(output_dir="exports", verbose=True)
```

### Using from a Reader

```python
from pandas_toolkit.io.readers import CSVReader

# All readers have an integrated exporter
reader = CSVReader(output_dir="exports")

df = reader.read("data.csv")

# Use the reader's exporter
reader.export(df, method="excel", filename="data.xlsx")
```

## Export a CSV

### Basic

```python
exporter = FileExporter(output_dir="exports")

exporter.export(
    df,
    method="csv",
    filename="data.csv"
)
```

### With Custom Parameters

```python
exporter.export(
    df,
    method="csv",
    filename="datos.csv",
    # Parámetros de pandas.to_csv
    index=False,              # No incluir índice
    encoding='utf-8',         # Encoding
    sep=',',                  # Separator
    quoting=1,                # Quote all fields
    quotechar='"'             # Quote character
)
```

## Export a Excel

### 1. Simple Excel (Single Sheet)

```python
exporter = FileExporter(output_dir="exports")

exporter.export(
    df,
    method="excel",
    filename="reporte.xlsx"
)
```

### 2. Excel Parts (Multiple Files)

Para datasets muy grandes que exceden el límite de filas de Excel (~1M filas):

```python
# Automatically split into multiple files
exporter.export(
    df_large,
    method="excel_parts",
    filename_prefix="data",
    max_rows=100000  # 100K rows per file
)

# Creates:
# - data_part1.xlsx (rows 0-99,999)
# - data_part2.xlsx (rows 100,000-199,999)
# - data_part3.xlsx (rows 200,000-299,999)
# etc.
```

### 3. Excel Sheets (Multiple Sheets)

For large datasets that you want in a single file:

```python
# Split into multiple sheets within the same file
exporter.export(
    df_large,
    method="excel_sheets",
    filename="complete_data.xlsx",
    max_rows=50000  # 50K rows per sheet
)

# Creates a file with sheets:
# - Sheet_1 (rows 0-49,999)
# - Sheet_2 (rows 50,000-99,999)
# - Sheet_3 (rows 100,000-149,999)
# etc.
```

### Excel Methods Comparison

```python
import pandas as pd
from pandas_toolkit.io.exporter import FileExporter

# Large example DataFrame (300K rows)
df_large = pd.DataFrame({
    'id': range(300000),
    'value': range(300000)
})

exporter = FileExporter(output_dir="exports", verbose=True)

print("=" * 70)
print("EXCEL METHODS COMPARISON")
print("=" * 70)

# Method 1: Simple Excel
# For datasets < 1M rows
exporter.export(df_large, method="excel", filename="simple.xlsx")
print("✓ simple.xlsx - One file, one sheet, all rows")

# Method 2: Excel parts
# For datasets > 1M rows or when you need separate files
exporter.export(
    df_large,
    method="excel_parts",
    filename_prefix="parts",
    max_rows=100000
)
print("✓ parts_part1.xlsx, parts_part2.xlsx, parts_part3.xlsx")
print("  - Three separate files")

# Method 3: Excel sheets
# For large datasets that you want in a single file
exporter.export(
    df_large,
    method="excel_sheets",
    filename="sheets.xlsx",
    max_rows=100000
)
print("✓ sheets.xlsx - One file with 3 sheets")

print("\n✅ Comparison completed!")
```

## Export a Parquet

Parquet es ideal para big data y almacenamiento eficiente:

```python
exporter = FileExporter(output_dir="exports")

# Basic export
exporter.export(
    df,
    method="parquet",
    filename="data.parquet"
)

# With compression
exporter.export(
    df,
    method="parquet",
    filename="data.parquet",
    compression='snappy'  # Opciones: 'snappy', 'gzip', 'brotli'
)
```

### Ventajas de Parquet

- ✅ Efficient compression (smaller files)
- ✅ Lectura más rápida que CSV
- ✅ Preserva tipos de datos
- ✅ Permite lectura parcial (columnar)

```python
# Size comparison
exporter = FileExporter(output_dir="exports")

# CSV
exporter.export(df_large, method="csv", filename="data.csv")
# Size: ~15 MB

# Parquet
exporter.export(df_large, method="parquet", filename="data.parquet")
# Size: ~3 MB (5x smaller!)
```

## Export a JSON

```python
exporter = FileExporter(output_dir="exports")

# JSON records (lista de objetos)
df.to_json(
    "exports/data_records.json",
    orient="records",
    indent=2,
    force_ascii=False
)

# JSONL (JSON Lines)
df.to_json(
    "exports/data.jsonl",
    orient="records",
    lines=True,
    force_ascii=False
)
```

## Complete Example: Export Pipeline

```python
from pandas_toolkit.io.readers import CSVReader
from pandas_toolkit.io.exporter import FileExporter
import pandas as pd

print("=" * 70)
print("COMPLETE EXPORT PIPELINE")
print("=" * 70)

# 1. Read data
print("\n1️⃣ Reading data...")
reader = CSVReader(verbose=True, output_dir="exports")
df = reader.read("original_data.csv", normalize=True, normalize_columns=True)
print(f"   ✓ Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# 2. Process (example)
print("\n2️⃣ Processing data...")
df_processed = df[df['value'] > 100].copy()
df_processed['process_date'] = pd.Timestamp.now()
print(f"   ✓ Filtered: {df_processed.shape[0]} rows")

# 3. Export to multiple formats
print("\n3️⃣ Exporting to multiple formats...")

exporter = FileExporter(output_dir="exports", verbose=True)

# CSV (for compatibility)
exporter.export(df_processed, method="csv", filename="processed_data.csv")
print("   ✓ CSV exported")

# Excel (for reports)
exporter.export(df_processed, method="excel", filename="report.xlsx")
print("   ✓ Excel exported")

# Parquet (for efficient storage)
exporter.export(df_processed, method="parquet", filename="data.parquet")
print("   ✓ Parquet exported")

# JSON (for APIs)
df_processed.to_json(
    "exports/data.json",
    orient="records",
    indent=2,
    force_ascii=False
)
print("   ✓ JSON exported")

print("\n✅ Pipeline completed! Files in: exports/")
```

## Export with Readers

All readers have the `export()` method:

```python
from pandas_toolkit.io.readers import (
    CSVReader, ExcelReader, JSONReader, HTMLReader
)

# CSV Reader
csv_reader = CSVReader(output_dir="exports")
df = csv_reader.read("data.csv")
csv_reader.export(df, method="excel", filename="from_csv.xlsx")

# Excel Reader
excel_reader = ExcelReader(output_dir="exports")
df = excel_reader.read("report.xlsx", sheet_name="Sales")
excel_reader.export(df, method="csv", filename="sales.csv")

# JSON Reader
json_reader = JSONReader(output_dir="exports")
df = json_reader.read("api_data.json")
json_reader.export(df, method="excel", filename="from_json.xlsx")

# HTML Reader
html_reader = HTMLReader(output_dir="exports")
df = html_reader.read("oracle_export.html", table_index=0)
html_reader.export(df, method="csv", filename="tabla_oracle.csv")
```

## Handling Large Files

### Strategy for Different Sizes

```python
from pandas_toolkit.io.exporter import FileExporter

exporter = FileExporter(output_dir="exports")

# Small (< 10K rows) - Simple Excel
if len(df) < 10000:
    exporter.export(df, method="excel", filename="data.xlsx")

# Medium (10K - 1M rows) - Simple Excel or CSV
elif len(df) < 1000000:
    exporter.export(df, method="excel", filename="data.xlsx")
    exporter.export(df, method="csv", filename="data.csv")

# Large (1M - 10M rows) - Excel parts or Parquet
elif len(df) < 10000000:
    exporter.export(
        df,
        method="excel_parts",
        filename_prefix="data",
        max_rows=500000
    )
    exporter.export(df, method="parquet", filename="data.parquet")

# Very large (> 10M rows) - Only Parquet or CSV
else:
    exporter.export(df, method="parquet", filename="data.parquet")
    exporter.export(df, method="csv", filename="data.csv")

print(f"✓ Data exported ({len(df):,} rows)")
```

## Advanced Parameters

### CSV with Custom Configuration

```python
exporter.export(
    df,
    method="csv",
    filename="datos.csv",
    # Parámetros personalizados
    sep=';',                    # Separador europeo
    decimal=',',                # Decimal europeo
    encoding='latin1',          # Encoding específico
    index=False,                # Sin índice
    header=True,                # Con headers
    quoting=1,                  # Quote all
    date_format='%Y-%m-%d'      # Formato de fecha
)
```

### Excel with Formatting

```python
# Para formateo avanzado, usa pandas directamente
with pd.ExcelWriter(
    'exports/reporte_formateado.xlsx',
    engine='openpyxl'
) as writer:
    df.to_excel(writer, sheet_name='Data', index=False)
    
    # Get worksheet
    worksheet = writer.sheets['Data']
    
    # Ajustar ancho de columnas
    for column in worksheet.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
```

## Tips and Best Practices

### 1. Organizar exports por fecha

```python
from datetime import datetime

fecha = datetime.now().strftime("%Y%m%d")
exporter = FileExporter(output_dir=f"exports/{fecha}")

exporter.export(df, method="excel", filename=f"reporte_{fecha}.xlsx")
```

### 2. Incluir timestamp en nombres

```python
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"datos_{timestamp}.xlsx"

exporter.export(df, method="excel", filename=filename)
```

### 3. Conditional export by size

```python
def export_smart(df, base_filename, output_dir="exports"):
    """Export inteligente basado en tamaño."""
    exporter = FileExporter(output_dir=output_dir)
    
    if len(df) < 100000:
        # Pequeño: Excel
        exporter.export(df, method="excel", filename=f"{base_filename}.xlsx")
        return "excel"
    else:
        # Grande: CSV + Parquet
        exporter.export(df, method="csv", filename=f"{base_filename}.csv")
        exporter.export(df, method="parquet", filename=f"{base_filename}.parquet")
        return "csv+parquet"
```

### 4. Validar antes de exportar

```python
def export_validated(df, filename, output_dir="exports"):
    """Export con validaciones."""
    # Validar DataFrame
    if df is None or df.empty:
        print("⚠ DataFrame vacío, no se exporta")
        return False
    
    # Validar columnas
    if len(df.columns) == 0:
        print("⚠ DataFrame sin columnas, no se exporta")
        return False
    
    # Export
    exporter = FileExporter(output_dir=output_dir, verbose=True)
    exporter.export(df, method="excel", filename=filename)
    return True
```

## Manejo de Errores

```python
from pandas_toolkit.io.exporter import FileExporter

exporter = FileExporter(output_dir="exports")

try:
    exporter.export(df, method="excel", filename="data.xlsx")
    print("✓ Export exitoso")
except PermissionError:
    print("✗ File open in Excel, close it first")
except ValueError as e:
    print(f"✗ Error de formato: {e}")
except Exception as e:
    print(f"✗ Error inesperado: {e}")
```

## Compatibilidad

- ✅ Python 3.7+
- ✅ pandas 2.0+
- ✅ openpyxl (para Excel)
- ✅ pyarrow (para Parquet)
- ✅ Windows, Linux, macOS

## See Also

- Todos los Readers Guides - Para usar export desde readers
- [QuickStart_Guide.md](QuickStart_Guide.md) - General guide

## Soporte

Para reportar bugs o solicitar features, abre un issue en el repositorio.
