# Data Normalization - Complete Guide

## Description

The EDA toolkit includes **advanced normalization capabilities** for cleaning and standardizing data. All readers inherit from `NormalizeMixin`, providing consistent normalization functionality throughout the toolkit.

## Types of Normalization

### 1. Column Normalization
Cleans and standardizes column names

### 2. Value Normalization
Cleans and standardizes cell content

## Column Normalization

### Applied Transformations

1. ✅ **Trim whitespace** - Removes leading/trailing spaces
2. ✅ **Case conversion** - lower/upper/None
3. ✅ **Remove accents** - `Café` → `Cafe`
4. ✅ **Replace spaces** - Spaces → underscores
5. ✅ **Remove special characters** - Only `a-zA-Z0-9_`
6. ✅ **Handle duplicates** - Adds numeric suffixes
7. ✅ **Empty columns** - Default name

### Basic Usage

```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader()

# Read with column normalization
df = reader.read(
    "data.csv",
    normalize_columns=True  # Activates column normalization
)
```

### Example: Before and After

```python
import pandas as pd
from pandas_toolkit.io.readers import CSVReader

# DataFrame with problematic columns
data = {
    "   First Name   ": ["John", "Mary"],
    "Last  Name": ["Perez", "Garcia"],
    "Émployee-ID": ["001", "002"],
    "Salary ($)": [50000, 60000],
    "": ["Data1", "Data2"]  # Empty column
}

df_original = pd.DataFrame(data)

print("BEFORE normalization:")
print(df_original.columns.tolist())
# ['   First Name   ', 'Last  Name', 'Émployee-ID', 'Salary ($)', '']

# Normalize
reader = CSVReader()
df_normalized = reader.normalize_columns(df_original)

print("\nAFTER normalization:")
print(df_normalized.columns.tolist())
# ['first_name', 'last_name', 'employee_id', 'salary', 'unnamed']
```

### Detailed Transformations

```python
# Original column → Normalized

"   First Name   "      → "first_name"       # Trim + lowercase + underscore
"Last  Name"            → "last_name"        # Multiple spaces → one
"Émployee-ID"           → "employee_id"      # Accent removed, dash → _
"Salary ($)"            → "salary"           # Special characters removed
"Email@Address"         → "email_address"    # @ → _
"Début-Date"            → "debut_date"       # é → e
"año-2024"              → "ano_2024"         # ñ → n
"Número de Télefono"    → "numero_de_telefono"  # Multiple accents
""                      → "unnamed"          # Empty → default name
```

### Configuration Options

```python
reader = CSVReader()

# Lowercase (default)
df = reader.normalize_columns(df, convert_case="lower")
# "First Name" → "first_name"

# Uppercase
df = reader.normalize_columns(df, convert_case="upper")
# "First Name" → "FIRST_NAME"

# No case conversion
df = reader.normalize_columns(df, convert_case=None)
# "First Name" → "First_Name"

# Custom name for empty columns
df = reader.normalize_columns(df, empty_col_name="no_name")
# "" → "no_name"
```

### Handling Duplicates

```python
import pandas as pd
from pandas_toolkit.io.readers import CSVReader

# DataFrame with duplicate columns
df = pd.DataFrame(columns=["name", "age", "name", "name"])

reader = CSVReader()
df_norm = reader.normalize_columns(df)

print(df_norm.columns.tolist())
# ['name', 'age', 'name_1', 'name_2']
```

## Value Normalization

### Applied Transformations

1. ✅ **Trim whitespace** - Remove extra spaces
2. ✅ **Case conversion** - lower/upper/None
3. ✅ **Empty strings → None** - Clean empty values
4. ✅ **'nan' string → None** - Clean 'nan' strings
5. ✅ **_norm columns** - Create normalized columns

### Basic Usage

```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader()

# Read with value normalization
df = reader.read(
    "data.csv",
    normalize=True  # Activate value normalization
)

# The DataFrame will have original columns + _norm columns
print(df.columns.tolist())
# ['name', 'status', 'city', 'name_norm', 'status_norm', 'city_norm']
```

### Example: Before and After

```python
import pandas as pd
from pandas_toolkit.io.readers import CSVReader

# DataFrame with problematic values
df_original = pd.DataFrame({
    "name": ["  JOHN  ", "  MARY  ", "  PETER  "],
    "status": ["  ACTIVE  ", "  INACTIVE  ", "   "],
    "city": ["Madrid", "Barcelona", ""]
})

print("BEFORE normalization:")
print(df_original)
#       name        status     city
# 0   JOHN        ACTIVE     Madrid
# 1   MARY        INACTIVE   Barcelona
# 2   PETER                  

# Normalize
reader = CSVReader()
df_normalized = reader.normalize(
    df_original,
    trim_strings=True,
    convert_case="lower"
)

print("\nAFTER normalization (_norm columns):")
print(df_normalized[['name', 'name_norm', 'status', 'status_norm']])
#      name    name_norm     status   status_norm
# 0   JOHN    john          ACTIVE   active
# 1   MARY    mary          INACTIVE inactive
# 2   PETER   peter                  None
```

### Normalized DataFrame Structure

```python
# The DataFrame will have BOTH versions:
# - Original columns (unmodified)
# - _norm columns (normalized)

df = reader.read("data.csv", normalize=True)

print(df.columns.tolist())
# Original columns + Normalized columns
# ['name', 'lastname', 'email', 'name_norm', 'lastname_norm', 'email_norm']

# Use original column
print(df['name'].tolist())
# ['  JOHN  ', '  MARY  ']

# Use normalized column
print(df['name_norm'].tolist())
# ['john', 'mary']
```

### Configuration Options

```python
reader = CSVReader()

df_norm = reader.normalize(
    df,
    drop_empty_cols=False,      # Remove empty columns
    drop_empty_rows=False,      # Remove empty rows
    trim_strings=True,          # Trim whitespace
    convert_case="lower"        # Case conversion
)

# Examples of convert_case:
# - "lower": all lowercase
# - "upper": all uppercase
# - None: no case conversion
```

### Use Cases: Data Cleaning

```python
from pandas_toolkit.io.readers import CSVReader
import pandas as pd

print("=" * 70)
print("COMPLETE DATA CLEANING")
print("=" * 70)

# 1. Messy data
df_dirty = pd.DataFrame({
    "  Name  ": ["  JOHN DOE  ", "  mary smith  ", "  "],
    "Email@": ["  JOHN@EXAMPLE.COM  ", "  mary@example.com  ", ""],
    "Status": ["  ACTIVE  ", "  ", "  INACTIVE  "]
})

print("\n📋 ORIGINAL DATA:")
print(df_dirty)

# 2. Normalize EVERYTHING
reader = CSVReader()

# First normalize columns
df_clean = reader.normalize_columns(df_dirty)

# Then normalize values
df_clean = reader.normalize(
    df_clean,
    trim_strings=True,
    convert_case="lower",
    drop_empty_rows=False  # Preserve rows for analysis
)

print("\n✨ NORMALIZED DATA:")
print(df_clean)

print("\n📊 ANALYSIS:")
print(f"  • Original columns: {len(df_dirty.columns)}")
print(f"  • Columns after normalization: {len(df_clean.columns)}")
print(f"  • _norm columns created: {len([c for c in df_clean.columns if c.endswith('_norm')])}")

# 3. Use normalized data
print("\n🎯 CLEAN DATA (only _norm):")
norm_cols = [c for c in df_clean.columns if c.endswith('_norm')]
print(df_clean[norm_cols])
```

## Normalization of Both (Columns and Values)

### Best Practice: Normalize Everything

```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader()

# Normalize BOTH columns and values
df = reader.read(
    "dirty_data.csv",
    normalize_columns=True,  # Normalize names
    normalize=True           # Normalize values
)

# Now you have:
# 1. Clean column names
# 2. Original values
# 3. Normalized values (_norm)
```

### Complete Example

```python
from pandas_toolkit.io.readers import CSVReader

print("=" * 70)
print("COMPLETE NORMALIZATION")
print("=" * 70)

reader = CSVReader(verbose=True, output_dir="exports")

# Read with complete normalization
df = reader.read(
    "real_data.csv",
    normalize_columns=True,    # Clean column names
    normalize=True,            # Clean values
    skip_leading_empty_rows=True,   # Skip empty rows at start
    skip_trailing_empty_rows=True   # Skip empty rows at end
)

print(f"\n✓ Normalized data:")
print(f"  • Shape: {df.shape}")
print(f"  • Columns: {df.columns.tolist()}")

# Show comparison
print(f"\n📊 Original vs Normalized Comparison:")
for col in df.columns:
    if not col.endswith('_norm'):
        norm_col = col + '_norm'
        if norm_col in df.columns:
            print(f"\n  {col}:")
            print(f"    Original: {df[col].head(2).tolist()}")
            print(f"    Normalized: {df[norm_col].head(2).tolist()}")

# Export clean data
# Option 1: With all columns (original + _norm)
reader.export(df, method="excel", filename="normalized_data_complete.xlsx")

# Option 2: Only normalized columns
norm_cols = [c for c in df.columns if not c.endswith('_norm') or c.endswith('_norm')]
df_only_norm = df[[c for c in df.columns if c.endswith('_norm')]].copy()
# Rename removing _norm
df_only_norm.columns = [c.replace('_norm', '') for c in df_only_norm.columns]
reader.export(df_only_norm, method="excel", filename="normalized_data_clean.xlsx")

print("\n✅ Data exported!")
```

## Removal of Empty Rows/Columns

### During Reading

```python
reader = CSVReader()

df = reader.read(
    "data.csv",
    skip_leading_empty_rows=True,   # Skip empty rows at start
    skip_trailing_empty_rows=True   # Skip empty rows at end
)
```

### During Normalization

```python
reader = CSVReader()

df_norm = reader.normalize(
    df,
    drop_empty_cols=True,  # Remove completely empty columns
    drop_empty_rows=True   # Remove completely empty rows
)
```

### Manual Methods

```python
from pandas_toolkit.io.base import FileReader

# Skip empty rows at start
df = FileReader.skip_leading_empty_rows(df)

# Skip empty rows at end
df = FileReader.skip_trailing_empty_rows(df)
```

## Common Use Cases

### Case 1: Data from Multiple Sources

```python
# Normalize for consistency across sources
reader = CSVReader()

df1 = reader.read("source1.csv", normalize_columns=True, normalize=True)
df2 = reader.read("source2.csv", normalize_columns=True, normalize=True)
df3 = reader.read("source3.csv", normalize_columns=True, normalize=True)

# Now all have the same column format
import pandas as pd
df_consolidated = pd.concat([df1, df2, df3], ignore_index=True)
```

### Case 2: Database Preparation

```python
# Normalize before INSERT
reader = CSVReader()

df = reader.read(
    "data_for_db.csv",
    normalize_columns=True,  # SQL-friendly column names
    normalize=True           # Clean values
)

# Use only normalized columns
norm_cols = {c: c.replace('_norm', '') for c in df.columns if c.endswith('_norm')}
df_db = df[norm_cols.keys()].rename(columns=norm_cols)

# Now INSERT to DB
# df_db.to_sql('table', connection, if_exists='append')
```

### Case 3: Matching/Deduplication

```python
# Use normalized values for matching
reader = CSVReader()

df = reader.read("customers.csv", normalize=True)

# Find duplicates using normalized values
duplicates = df[df.duplicated(subset=['email_norm'], keep=False)]

print(f"Duplicates found: {len(duplicates)}")
```

## Tips and Best Practices

### 1. Always normalize in production

```python
# Always normalize in production environments
df = reader.read(
    file,
    normalize_columns=True,
    normalize=True
)
```

### 2. Preserve original data

```python
# Original columns are preserved
# You can compare or revert if needed
print("Original:", df['name'].iloc[0])
print("Normalized:", df['name_norm'].iloc[0])
```

### 3. Normalize before comparing

```python
# Use normalized values for comparisons
matching = df1.merge(
    df2,
    left_on='email_norm',
    right_on='email_norm'
)
```

### 4. Export clean data

```python
# Export only normalized columns for clean use
norm_cols = [c for c in df.columns if c.endswith('_norm')]
df_clean = df[norm_cols].copy()
df_clean.columns = [c.replace('_norm', '') for c in df_clean.columns]

reader.export(df_clean, method="csv", filename="clean_data.csv")
```

## Compatibility

- ✅ Python 3.7+
- ✅ pandas 2.0+
- ✅ All toolkit readers
- ✅ Windows, Linux, macOS

## See Also

- [CSVReader_Guide.md](CSVReader_Guide.md)
- [QuickStart_Guide.md](QuickStart_Guide.md)
- All Reader Guides

## Support

To report bugs or request features, open an issue in the repository.
