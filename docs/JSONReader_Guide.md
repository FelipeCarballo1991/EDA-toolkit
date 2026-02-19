# JSONReader - Complete Guide

## Description

`JSONReader` is a component for reading JSON and JSONL (JSON Lines) files. It supports multiple formats and JSON orientations, making it versatile for different data structures.

## Main Features

- ✅ **Supports standard JSON** (complete)
- ✅ **Supports JSONL** (JSON Lines / streaming)
- ✅ **Multiple orientations** (records, columns, index, split, table)
- ✅ **Automatic detection** of JSONL format
- ✅ **Data normalization** and column names
- ✅ **Export** to multiple formats
- ✅ **Batch processing** of multiple files

## Installing Dependencies

```bash
pip install pandas
# Or install all project dependencies:
pip install -r requirements.txt
```

## Basic Usage

### Import the Reader

```python
from pandas_toolkit.io.readers import JSONReader
# Or using the factory
from pandas_toolkit.io.factory import ReaderFactory
```

### Simple Reading

```python
reader = JSONReader()

# Standard JSON
df = reader.read("datos.json")

# JSONL (JSON Lines)
df = reader.read("datos.jsonl")

print(f"Shape: {df.shape}")
```

### Read with Normalization

```python
reader = JSONReader(verbose=True)

df = reader.read(
    "datos.json",
    normalize=True,              # Normalize values
    normalize_columns=True,      # Normalize column names
    skip_leading_empty_rows=True,
    skip_trailing_empty_rows=True
)

print(df.columns.tolist())
```

## Supported JSON Formats

### 1. Records (List of Objects) - DEFAULT

The most common format: list of dictionaries.

```json
[
    {"nombre": "Juan", "edad": 30, "ciudad": "Madrid"},
    {"nombre": "María", "edad": 25, "ciudad": "Barcelona"},
    {"nombre": "Pedro", "edad": 35, "ciudad": "Valencia"}
]
```

```python
reader = JSONReader()
df = reader.read("datos.json", orient="records")  # Default
# o simplemente:
df = reader.read("datos.json")
```

### 2. Columns (Dictionary of Arrays)

```json
{
    "nombre": ["Juan", "María", "Pedro"],
    "edad": [30, 25, 35],
    "ciudad": ["Madrid", "Barcelona", "Valencia"]
}
```

```python
reader = JSONReader()
df = reader.read("datos.json", orient="columns")
```

### 3. Index (Dictionary of Dictionaries)

```json
{
    "0": {"nombre": "Juan", "edad": 30, "ciudad": "Madrid"},
    "1": {"nombre": "María", "edad": 25, "ciudad": "Barcelona"},
    "2": {"nombre": "Pedro", "edad": 35, "ciudad": "Valencia"}
}
```

```python
reader = JSONReader()
df = reader.read("datos.json", orient="index")
```

### 4. Split (Dictionary with columns and data)

```json
{
    "columns": ["nombre", "edad", "ciudad"],
    "data": [
        ["Juan", 30, "Madrid"],
        ["María", 25, "Barcelona"],
        ["Pedro", 35, "Valencia"]
    ]
}
```

```python
reader = JSONReader()
df = reader.read("datos.json", orient="split")
```

### 5. JSONL (JSON Lines) - Streaming Format

Cada línea es un objeto JSON individual:

```
{"nombre": "Juan", "edad": 30, "ciudad": "Madrid"}
{"nombre": "María", "edad": 25, "ciudad": "Barcelona"}
{"nombre": "Pedro", "edad": 35, "ciudad": "Valencia"}
```

```python
reader = JSONReader()

# Método 1: Detección automática por extensión
df = reader.read("datos.jsonl")

# Método 2: Método específico
df = reader.read_lines("datos.jsonl")

# Método 3: Parámetro explícito
df = reader.read("datos.txt", lines=True)
```

## JSONReader Methods

### 1. `read()` - Read JSON file

```python
reader = JSONReader()

df = reader.read(
    filepath="datos.json",
    orient="records",                 # JSON orientation
    normalize=False,                  # Normalize values
    normalize_columns=False,          # Normalize column names
    skip_leading_empty_rows=True,
    skip_trailing_empty_rows=True,
    # All pandas.read_json parameters are supported:
    dtype=None,                       # Data types
    convert_dates=True,               # Convert dates automatically
    # ... etc
)
```

### 2. `read_lines()` - Read JSONL specifically

```python
reader = JSONReader()

# Read JSON Lines (each line is a JSON object)
df = reader.read_lines("streaming_data.jsonl")

# It is equivalent to:
df = reader.read("streaming_data.jsonl", lines=True)
```

### 3. `read_multiple_files()` - Batch reading

```python
reader = JSONReader(verbose=True)

# Read all JSON files in a folder
files = reader.read_multiple_files(
    "data_folder/",
    normalize=True,
    normalize_columns=True
)

# Returns a dictionary {filename: DataFrame}
for filename, df in files.items():
    print(f"{filename}: {df.shape}")
```

### 4. `export()` - Export DataFrame

```python
reader = JSONReader(output_dir="exports")

df = reader.read("datos.json")

# Export to CSV
reader.export(df, method="csv", filename="datos.csv")

# Export to Excel
reader.export(df, method="excel", filename="datos.xlsx")

# Export to JSON
reader.export(df, method="json", filename="datos_procesados.json")
```

## Complete Example: API Response

```python
from pandas_toolkit.io.readers import JSONReader
import requests
import json

print("=" * 70)
print("PROCESANDO RESPUESTA JSON DE API")
print("=" * 70)

# Simular respuesta de API
api_response = {
    "status": "success",
    "data": [
        {"id": 1, "nombre": "Producto A", "precio": 100, "stock": 50},
        {"id": 2, "nombre": "Producto B", "precio": 200, "stock": 30},
        {"id": 3, "nombre": "Producto C", "precio": 150, "stock": 40}
    ]
}

# Guardar a archivo
with open("api_response.json", "w", encoding="utf-8") as f:
    json.dump(api_response["data"], f, indent=2, ensure_ascii=False)

# Read with JSONReader
reader = JSONReader(verbose=True, output_dir="exports")

df = reader.read(
    "api_response.json",
    orient="records",
    normalize=True,
    normalize_columns=True
)

print(f"\n✓ API data loaded: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nPreview:")
print(df)

# Analysis
print(f"\n📊 Analysis:")
print(f"  • Total products: {len(df)}")
print(f"  • Average price: ${df['precio'].mean():.2f}")
print(f"  • Total stock: {df['stock'].sum()}")

# Export
reader.export(df, method="csv", filename="productos_api.csv")
reader.export(df, method="excel", filename="productos_api.xlsx")

print("\n✅ Data exported to: exports/")
```

## Example: Streaming JSONL

```python
from pandas_toolkit.io.readers import JSONReader

print("=" * 70)
print("PROCESSING JSONL FILE (STREAMING)")
print("=" * 70)

# Create example JSONL file
import json

logs = [
    {"timestamp": "2024-01-01 10:00:00", "level": "INFO", "message": "Server started"},
    {"timestamp": "2024-01-01 10:05:00", "level": "WARNING", "message": "High memory usage"},
    {"timestamp": "2024-01-01 10:10:00", "level": "ERROR", "message": "Connection failed"},
    {"timestamp": "2024-01-01 10:15:00", "level": "INFO", "message": "Connection restored"}
]

with open("server_logs.jsonl", "w", encoding="utf-8") as f:
    for log in logs:
        f.write(json.dumps(log) + "\n")

# Read with JSONReader
reader = JSONReader(verbose=True)

df = reader.read_lines("server_logs.jsonl")

print(f"\n✓ Logs loaded: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nLogs:")
print(df)

# Filter errors
errors = df[df['level'] == 'ERROR']
print(f"\n⚠ Errors found: {len(errors)}")
print(errors)

# Export errors
reader.export(errors, method="csv", filename="errors_only.csv")

print("\n✅ Log analysis completed!")
```

## Common Use Cases

### Case 1: API REST Response

```python
reader = JSONReader()

# Typical API response format
df = reader.read("api_data.json", orient="records")

print(f"API data loaded: {df.shape}")
```

### Case 2: Nested JSON (Flatten)

```python
import pandas as pd
from pandas_toolkit.io.readers import JSONReader

# JSON with nested structure
nested_json = [
    {
        "id": 1,
        "user": {
            "name": "Juan",
            "email": "juan@example.com"
        },
        "metadata": {
            "created": "2024-01-01",
            "status": "active"
        }
    }
]

# Save and read
import json
with open("nested.json", "w") as f:
    json.dump(nested_json, f)

reader = JSONReader()

# Read and flatten
df = pd.json_normalize(pd.read_json("nested.json"))

print(df.columns.tolist())
# ['id', 'user.name', 'user.email', 'metadata.created', 'metadata.status']
```

### Case 3: Large JSONL File (Streaming)

```python
reader = JSONReader(verbose=True)

# For large files, JSONL is more efficient
# Reads line by line instead of loading everything into memory
df = reader.read_lines("large_dataset.jsonl")

print(f"Large dataset loaded: {df.shape}")
```

### Case 4: Export DataFrame to JSON

```python
import pandas as pd
from pandas_toolkit.io.readers import JSONReader

# Create DataFrame
df = pd.DataFrame({
    'nombre': ['Juan', 'María', 'Pedro'],
    'edad': [30, 25, 35],
    'ciudad': ['Madrid', 'Barcelona', 'Valencia']
})

# Export to JSON with different orientations
reader = JSONReader(output_dir="exports")

# As records
df.to_json("exports/datos_records.json", orient="records", indent=2, force_ascii=False)

# As columns
df.to_json("exports/datos_columns.json", orient="columns", indent=2, force_ascii=False)

# As JSONL
df.to_json("exports/datos.jsonl", orient="records", lines=True, force_ascii=False)

print("✅ DataFrames exported in multiple JSON formats")
```

## Batch Processing

```python
from pathlib import Path
from pandas_toolkit.io.readers import JSONReader

reader = JSONReader(verbose=True, output_dir="exports")

# Process all JSON files in a folder
json_files = list(Path("data_folder").glob("*.json"))

all_data = []

for json_file in json_files:
    print(f"\nProcessing: {json_file.name}")
    
    df = reader.read(
        str(json_file),
        normalize=True,
        normalize_columns=True
    )
    
    print(f"  Shape: {df.shape}")
    
    # Add origin column
    df['source_file'] = json_file.name
    
    all_data.append(df)
    
    # Export individually
    output_name = f"{json_file.stem}_processed.csv"
    reader.export(df, method="csv", filename=output_name)

# Consolidate all files
import pandas as pd
df_consolidado = pd.concat(all_data, ignore_index=True)

print(f"\n✓ Consolidated DataFrame: {df_consolidado.shape}")

# Export consolidated
reader.export(df_consolidado, method="excel", filename="consolidado.xlsx")

print("\n✅ Batch processing completed!")
```

## Using with Factory

```python
from pandas_toolkit.io.factory import ReaderFactory

# The factory automatically creates a JSONReader
reader = ReaderFactory.create_reader("datos.json", verbose=True)

df = reader.read("datos.json")

print(f"Reader type: {type(reader).__name__}")  # JSONReader
```

## Advanced Parameters

```python
reader = JSONReader()

df = reader.read(
    "datos.json",
    orient="records",
    # Pandas-specific parameters
    dtype={'edad': int, 'precio': float},  # Data types
    convert_dates=True,                     # Convert dates
    date_unit='ms',                         # Timestamp unit
    encoding='utf-8',                       # Encoding
    lines=False,                            # JSONL format
    # ... all pd.read_json parameters
)
```

## Error Handling

### File Not Found

```python
reader = JSONReader()

try:
    df = reader.read("archivo_inexistente.json")
except FileNotFoundError as e:
    print(f"Error: {e}")
```

### Malformed JSON

```python
reader = JSONReader(verbose=True)

try:
    df = reader.read("malformed.json")
except Exception as e:
    print(f"JSON parsing error: {e}")
```

## Modo Verbose

```python
reader = JSONReader(verbose=True)

# Te mostrará:
# [INFO] Reading JSON file: datos.json, orient: records
# [INFO] Successfully loaded 1000 rows, 5 columns

df = reader.read("datos.json")
```

## Comparación con pandas Nativo

### Con pandas nativo:

```python
import pandas as pd

# JSON estándar
df = pd.read_json("datos.json", orient="records")

# JSONL
df = pd.read_json("datos.jsonl", lines=True)
```

### Con JSONReader:

```python
from pandas_toolkit.io.readers import JSONReader

reader = JSONReader(verbose=True)

# Detección automática + normalización
df = reader.read(
    "datos.json",
    normalize=True,
    normalize_columns=True
)

# Ventajas:
# - Normalización integrada
# - Direct export to multiple formats
# - API consistente con otros readers
# - Procesamiento batch incorporado
# - Detección automática de JSONL
```

## Tips and Best Practices

### 1. Use JSONL for large files

```python
# JSONL is more efficient for streaming
reader = JSONReader()
df = reader.read_lines("large_data.jsonl")
```

### 2. Specify correct orientation

```python
reader = JSONReader()

# If you know the format, specify it
df = reader.read("api_response.json", orient="records")
```

### 3. Normalize nested JSON

```python
import pandas as pd
import json

# For nested JSON, use pd.json_normalize
with open("nested.json") as f:
    data = json.load(f)

df = pd.json_normalize(data)
```

### 4. Preserve UTF-8 encoding

```python
# When exporting, use force_ascii=False to preserve special characters
df.to_json(
    "output.json",
    orient="records",
    force_ascii=False,
    indent=2
)
```

## Troubleshooting

### Problem: "ValueError: Expected object or value"

**Solution**: Malformed JSON

```python
# Verify JSON format
import json

with open("datos.json") as f:
    data = json.load(f)  # This will show the exact error
```

### Problem: "Insufficient memory"

**Solution**: Use JSONL for streaming

```python
# Instead of loading the entire JSON
# Convert to JSONL and read line by line
reader = JSONReader()
df = reader.read_lines("datos.jsonl")
```

## Compatibility

- ✅ Python 3.7+
- ✅ pandas 2.0+
- ✅ Windows, Linux, macOS

## Additional Examples

See also:
- [`test.py`](../test.py) - Test examples
- pandas documentation: `pd.read_json()`

## Support

To report bugs or request features, open an issue in the repository.
