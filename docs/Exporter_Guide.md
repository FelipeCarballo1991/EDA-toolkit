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

# Todos los readers tienen un exporter integrado
reader = CSVReader(output_dir="exports")

df = reader.read("datos.csv")

# Use the reader's exporter
reader.export(df, method="excel", filename="datos.xlsx")
```

## Export a CSV

### Basic

```python
exporter = FileExporter(output_dir="exports")

exporter.export(
    df,
    method="csv",
    filename="datos.csv"
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
    df_grande,
    method="excel_parts",
    filename_prefix="datos",
    max_rows=100000  # 100K filas por archivo
)

# Crea:
# - datos_part1.xlsx (filas 0-99,999)
# - datos_part2.xlsx (filas 100,000-199,999)
# - datos_part3.xlsx (filas 200,000-299,999)
# etc.
```

### 3. Excel Sheets (Multiple Sheets)

Para datasets grandes que quieres en un solo archivo:

```python
# Split into multiple sheets within the same file
exporter.export(
    df_grande,
    method="excel_sheets",
    filename="datos_completos.xlsx",
    max_rows=50000  # 50K filas por hoja
)

# Crea un archivo con hojas:
# - Sheet_1 (filas 0-49,999)
# - Sheet_2 (filas 50,000-99,999)
# - Sheet_3 (filas 100,000-149,999)
# etc.
```

### Comparación Excel Methods

```python
import pandas as pd
from pandas_toolkit.io.exporter import FileExporter

# Large example DataFrame (300K rows)
df_grande = pd.DataFrame({
    'id': range(300000),
    'valor': range(300000)
})

exporter = FileExporter(output_dir="exports", verbose=True)

print("=" * 70)
print("COMPARACIÓN DE MÉTODOS EXCEL")
print("=" * 70)

# Método 1: Excel simple
# Para datasets < 1M filas
exporter.export(df_grande, method="excel", filename="simple.xlsx")
print("✓ simple.xlsx - Un archivo, una hoja, todas las filas")

# Método 2: Excel parts
# Para datasets > 1M filas o cuando necesitas archivos separados
exporter.export(
    df_grande,
    method="excel_parts",
    filename_prefix="partes",
    max_rows=100000
)
print("✓ partes_part1.xlsx, partes_part2.xlsx, partes_part3.xlsx")
print("  - Tres archivos separados")

# Método 3: Excel sheets
# Para datasets grandes que quieres en un solo archivo
exporter.export(
    df_grande,
    method="excel_sheets",
    filename="hojas.xlsx",
    max_rows=100000
)
print("✓ hojas.xlsx - Un archivo con 3 hojas")

print("\n✅ Comparación completada!")
```

## Export a Parquet

Parquet es ideal para big data y almacenamiento eficiente:

```python
exporter = FileExporter(output_dir="exports")

# Basic export
exporter.export(
    df,
    method="parquet",
    filename="datos.parquet"
)

# Con compresión
exporter.export(
    df,
    method="parquet",
    filename="datos.parquet",
    compression='snappy'  # Opciones: 'snappy', 'gzip', 'brotli'
)
```

### Ventajas de Parquet

- ✅ Compresión eficiente (archivos más pequeños)
- ✅ Lectura más rápida que CSV
- ✅ Preserva tipos de datos
- ✅ Permite lectura parcial (columnar)

```python
# Comparación de tamaños
exporter = FileExporter(output_dir="exports")

# CSV
exporter.export(df_grande, method="csv", filename="datos.csv")
# Tamaño: ~15 MB

# Parquet
exporter.export(df_grande, method="parquet", filename="datos.parquet")
# Tamaño: ~3 MB (5x más pequeño!)
```

## Export a JSON

```python
exporter = FileExporter(output_dir="exports")

# JSON records (lista de objetos)
df.to_json(
    "exports/datos_records.json",
    orient="records",
    indent=2,
    force_ascii=False
)

# JSONL (JSON Lines)
df.to_json(
    "exports/datos.jsonl",
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
print("PIPELINE COMPLETO DE EXPORT")
print("=" * 70)

# 1. Leer datos
print("\n1️⃣ Leyendo datos...")
reader = CSVReader(verbose=True, output_dir="exports")
df = reader.read("datos_originales.csv", normalize=True, normalize_columns=True)
print(f"   ✓ Cargados: {df.shape[0]} filas × {df.shape[1]} columnas")

# 2. Process (example)
print("\n2️⃣ Procesando datos...")
df_procesado = df[df['valor'] > 100].copy()
df_procesado['fecha_proceso'] = pd.Timestamp.now()
print(f"   ✓ Filtrados: {df_procesado.shape[0]} filas")

# 3. Export to multiple formats
print("\n3️⃣ Exporting to multiple formats...")

exporter = FileExporter(output_dir="exports", verbose=True)

# CSV (para compatibilidad)
exporter.export(df_procesado, method="csv", filename="datos_procesados.csv")
print("   ✓ CSV exportado")

# Excel (para reportes)
exporter.export(df_procesado, method="excel", filename="reporte.xlsx")
print("   ✓ Excel exportado")

# Parquet (para almacenamiento eficiente)
exporter.export(df_procesado, method="parquet", filename="datos.parquet")
print("   ✓ Parquet exportado")

# JSON (para APIs)
df_procesado.to_json(
    "exports/datos.json",
    orient="records",
    indent=2,
    force_ascii=False
)
print("   ✓ JSON exportado")

print("\n✅ Pipeline completado! Archivos en: exports/")
```

## Export with Readers

Todos los readers tienen el método `export()`:

```python
from pandas_toolkit.io.readers import (
    CSVReader, ExcelReader, JSONReader, HTMLReader
)

# CSV Reader
csv_reader = CSVReader(output_dir="exports")
df = csv_reader.read("datos.csv")
csv_reader.export(df, method="excel", filename="desde_csv.xlsx")

# Excel Reader
excel_reader = ExcelReader(output_dir="exports")
df = excel_reader.read("reporte.xlsx", sheet_name="Ventas")
excel_reader.export(df, method="csv", filename="ventas.csv")

# JSON Reader
json_reader = JSONReader(output_dir="exports")
df = json_reader.read("api_data.json")
json_reader.export(df, method="excel", filename="desde_json.xlsx")

# HTML Reader
html_reader = HTMLReader(output_dir="exports")
df = html_reader.read("oracle_export.html", table_index=0)
html_reader.export(df, method="csv", filename="tabla_oracle.csv")
```

## Handling Large Files

### Estrategia para Diferentes Tamaños

```python
from pandas_toolkit.io.exporter import FileExporter

exporter = FileExporter(output_dir="exports")

# Pequeño (< 10K filas) - Excel simple
if len(df) < 10000:
    exporter.export(df, method="excel", filename="datos.xlsx")

# Mediano (10K - 1M filas) - Excel simple o CSV
elif len(df) < 1000000:
    exporter.export(df, method="excel", filename="datos.xlsx")
    exporter.export(df, method="csv", filename="datos.csv")

# Grande (1M - 10M filas) - Excel parts o Parquet
elif len(df) < 10000000:
    exporter.export(
        df,
        method="excel_parts",
        filename_prefix="datos",
        max_rows=500000
    )
    exporter.export(df, method="parquet", filename="datos.parquet")

# Muy grande (> 10M filas) - Solo Parquet o CSV
else:
    exporter.export(df, method="parquet", filename="datos.parquet")
    exporter.export(df, method="csv", filename="datos.csv")

print(f"✓ Datos exportados ({len(df):,} filas)")
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
    df.to_excel(writer, sheet_name='Datos', index=False)
    
    # Get worksheet
    worksheet = writer.sheets['Datos']
    
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

## Tips y Mejores Prácticas

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
    exporter.export(df, method="excel", filename="datos.xlsx")
    print("✓ Export exitoso")
except PermissionError:
    print("✗ Archivo abierto en Excel, ciérralo primero")
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
