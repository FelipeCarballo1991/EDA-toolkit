# Quick Start Guide - Enhanced Normalization

## 🚀 Quick Start

### Basic Usage (Compatible with existing code)

```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader()

# Traditional way - still works
df = reader.read("data.csv", normalize=True, normalize_columns=True)
```

### Using Presets (New - Recommended)

```python
# Basic preset (recommended for most cases)
df = reader.normalize(df, preset='basic')

# Complete preset (exhaustive cleaning)
df = reader.normalize(df, preset='full')

# Preset for analysis (replaces original columns)
df = reader.normalize(df, preset='analysis_ready')
```

## 📚 Practical Examples

### Example 1: Customer Data Cleaning

```python
import pandas as pd
from pandas_toolkit.io.readers import CSVReader

# Sample data
data = {
    "  Nombre  ": ["  JUAN PÉREZ  ", "  Maria García  ", "  "],
    "Email": ["juan@email.com", "MARIA@EMAIL.COM", "N/A"],
    "Teléfono": ["123-456-7890", "", "null"],
    "Status": ["ACTIVO", "activo", "Activo"]
}
df = pd.DataFrame(data)

reader = CSVReader()

# Complete normalization
df_clean = reader.normalize_columns(df)  # Normalize column names
df_clean = reader.normalize(df_clean, preset='basic')  # Normalize values

print(df_clean)
#   nombre         email           telefono     status  \
# 0 juan pérez     juan@email.com  123-456-7890 activo  
# 1 maria garcía   maria@email.com -            activo  
# 2 -              -               -            activo
```

### Example 2: Preparation for Analysis

```python
from pandas_toolkit.io.readers import CSVReader
from pandas_toolkit.io.base import NormalizationConfig

reader = CSVReader()

# Read and normalize in one step
df = reader.read("sales.csv", normalize_columns=True)

# Use analysis_ready preset (replaces original columns)
df = reader.normalize(df, preset='analysis_ready')

# Now df has:
# - Normalized columns (no spaces, lowercase, no accents)
# - Normalized values (trim, lowercase, standardized nulls)
# - No duplicated columns (_norm)
# - Ready for analysis
```

### Example 3: Custom Normalization

```python
from pandas_toolkit.io.base import NormalizationConfig

# Custom configuration
config = NormalizationConfig(
    strings={
        'trim': True,
        'case': 'upper',  # UPPERCASE instead of lowercase
        'remove_special': False
    },
    nulls={
        'standardize': True,
        'values': ['MISSING', 'UNKNOWN', 'N/A', '']  # Specific null values
    },
    columns={
        'drop_original': True,  # Replace columns
        'suffix': '_clean'
    }
)

df = reader.normalize(df, config=config)
```

### Example 4: Null Values Standardization

```python
# Problem: Multiple representations of missing values
data = {
    "Cliente": ["Juan", "N/A", "Maria", "null", "Pedro", "-"],
    "Monto": ["1000", "", "2000", "N/A", "3000", "0"]
}
df = pd.DataFrame(data)

# Solution: Standardize nulls
df_clean = reader.normalize(
    df,
    standardize_nulls=True,
    null_values=['MISSING', 'N/A'],  # Additional values
    drop_original=True
)

# Now all nulls are np.nan
print(df_clean['Cliente'].isna().sum())  # → 3 null values
```

### Example 5: Keep Original Columns vs Replace Them

```python
# OPTION A: Keep originals (default)
df_with_both = reader.normalize(df, drop_original=False)
# Result: ['Nombre', 'Email', 'Nombre_norm', 'Email_norm']

# OPTION B: Replace originals
df_replaced = reader.normalize(df, drop_original=True)
# Result: ['Nombre', 'Email'] (but with normalized values)

# OPTION C: Use custom suffix
df_custom = reader.normalize(df, suffix='_clean', drop_original=False)
# Result: ['Nombre', 'Email', 'Nombre_clean', 'Email_clean']
```

### Example 6: Direct Use of Normalizers (Advanced)

```python
from pandas_toolkit.io.base.normalizers import (
    ColumnNormalizer,
    StringNormalizer,
    NullNormalizer
)

# Normalize only columns
df = ColumnNormalizer.normalize(df, convert_case="upper")

# Normalize only a specific column
df['nombre'] = StringNormalizer.normalize(
    df['nombre'],
    trim=True,
    convert_case="title"  # First letter uppercase
)

# Standardize nulls
df = NullNormalizer.normalize(df, null_values=['MISSING'])

# Get null summary
summary = NullNormalizer.get_null_summary(df)
print(summary)
#   column  null_count  null_percentage
# 0 nombre           2        20.0
# 1 email            1        10.0
```

### Example 7: Complete Cleaning Pipeline

```python
from pandas_toolkit.io.readers import CSVReader
from pandas_toolkit.io.base import NormalizationConfig

# 1. Read data
reader = CSVReader()
df = reader.read("raw_data.csv")

# 2. Normalize columns
df = reader.normalize_columns(df, convert_case="lower")

# 3. Configure custom normalization
config = NormalizationConfig.from_preset('full')
config.columns['drop_original'] = True  # Modify preset

# 4. Apply normalization
df = reader.normalize(df, config=config)

# 5. Drop empty rows/columns
df = reader.normalize(
    df,
    drop_empty_cols=True,
    drop_empty_rows=True,
    drop_original=True
)

# 6. Export clean data
reader.export([df], "clean_data.xlsx")
```

## 🎨 Approach Comparison

### Approach 1: Traditional (Backward Compatible)
```python
df = reader.read("data.csv", normalize=True, normalize_columns=True)
# ✅ Works as always
# ⚠️ Less control over options
```

### Approach 2: With Preset (Recommended)
```python
df = reader.read("data.csv", normalize_columns=True)
df = reader.normalize(df, preset='basic')
# ✅ Easy to use
# ✅ Consistent configuration
# ✅ Predefined use cases
```

### Approach 3: With Config (Maximum Control)
```python
config = NormalizationConfig(...)
df = reader.normalize(df, config=config)
# ✅ Total control
# ✅ Reusable
# ⚠️ More verbose
```

### Approach 4: Direct (Advanced)
```python
from pandas_toolkit.io.base.normalizers import ColumnNormalizer
df = ColumnNormalizer.normalize(df)
# ✅ Granular
# ✅ Fast for specific cases
# ⚠️ Requires more knowledge
```

## 🔍 Common Use Cases

### Case 1: Quick EDA
```python
# You want to explore data quickly
df = reader.normalize(df, preset='basic')
```

### Case 2: Prepare for Machine Learning
```python
# You need clean data for modeling
df = reader.normalize(df, preset='analysis_ready')
```

### Case 3: Maintain Traceability
```python
# You want to compare before/after
df = reader.normalize(df, drop_original=False, suffix='_clean')
# Now you have: original_value vs original_value_clean
```

### Case 4: Minimal Cleaning
```python
# You only want to remove spaces
df = reader.normalize(df, preset='minimal')
```

## 💡 Tips

1. **Use presets first**: Try `'basic'` or `'full'` before customizing
2. **drop_original=True for analysis**: Saves memory and simplifies
3. **Keep originals for auditing**: Use `drop_original=False` (default)
4. **Customize presets**: Load preset and modify what you need
5. **Check nulls first**: Use `NullNormalizer.get_null_summary(df)`

## 🐛 Troubleshooting

### Problem: "Values are not being normalized"
```python
# Make sure the column is string type
df['column'] = df['column'].astype(str)
df = reader.normalize(df)
```

### Problem: "I lost my original values"
```python
# Use drop_original=False (default)
df = reader.normalize(df, drop_original=False)
```

### Problem: "I need more control"
```python
# Use custom configuration
config = NormalizationConfig(...)
df = reader.normalize(df, config=config)
```

## 📖 Additional Resources

- [Complete Normalization Guide](Normalization_Guide.md)
- [Phase 1 Migration Guide](REFACTORING_PHASE1_GUIDE.md)
- [Normalizers Documentation](../pandas_toolkit/io/base/normalizers/README.md)
- [Phase 1 Summary](PHASE1_SUMMARY.md)

---

Enjoy the new normalization functionality! 🎉
