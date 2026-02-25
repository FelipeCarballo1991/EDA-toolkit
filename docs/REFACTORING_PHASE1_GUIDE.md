# Phase 1 Refactoring - Migration Guide

## 🎉 What Changed?

**Phase 1** of the normalization refactoring has been completed successfully. The code has been reorganized to make it more modular, maintainable, and extensible, without breaking compatibility with existing code.

## 📦 New Structure

### Before (v1.x)
```
pandas_toolkit/io/base/
  ├── mixins.py  (241 lines - everything in one file)
  └── ...
```

### Now (v2.0)
```
pandas_toolkit/io/base/
  ├── mixins.py  (refactored - delegates to normalizers)
  ├── normalizers/
  │   ├── __init__.py
  │   ├── config.py              # NormalizationConfig (presets and configuration)
  │   ├── column_normalizer.py   # Column name normalization
  │   ├── string_normalizer.py   # String value normalization
  │   └── null_normalizer.py     # Null value standardization
  └── ...
```

## ✅ Implemented Changes

### 1. **Separation of Concerns**
Normalization code is now organized into specialized modules:

- **`ColumnNormalizer`**: Column name normalization
- **`StringNormalizer`**: String value normalization (trim, case, special chars)
- **`NullNormalizer`**: Null value standardization

### 2. **Preset Configuration System**
New `NormalizationConfig` class with predefined presets:

- **`minimal`**: Basic trim only
- **`basic`**: Trim + case + standard nulls
- **`full`**: Complete normalization (includes future normalizers)
- **`analysis_ready`**: Optimized for analysis (drop_original=True)

### 3. **New Features**

#### a) `drop_original` Parameter
```python
# Before: Always created columns with _norm suffix
df = reader.normalize(df)
# Columns: ['Name', 'Name_norm']

# Now: Option to replace original columns
df = reader.normalize(df, drop_original=True)
# Columns: ['Name']  (normalized values)
```

#### b) Enhanced Null Standardization
```python
# Converts multiple null representations to np.nan
df = reader.normalize(df, standardize_nulls=True)
# '', 'N/A', 'null', 'None', '-', '--' → np.nan

# Custom null values
df = reader.normalize(df, null_values=['MISSING', 'UNKNOWN'])
```

#### c) Customizable Suffix
```python
# Before: Always used '_norm'
df = reader.normalize(df)
# Columns: ['Name', 'Name_norm']

# Now: Customizable suffix
df = reader.normalize(df, suffix='_clean')
# Columns: ['Name', 'Name_clean']
```

#### d) Presets for Quick Use
```python
# Basic preset
df = reader.normalize(df, preset='basic')

# Complete preset
df = reader.normalize(df, preset='full')

# Preset for analysis (replaces columns)
df = reader.normalize(df, preset='analysis_ready')
```

#### e) Configuration with Objects or Dictionaries
```python
# Using config object
config = NormalizationConfig(
    strings={'trim': True, 'case': 'upper'},
    nulls={'standardize': True},
    columns={'drop_original': True, 'suffix': '_norm'}
)
df = reader.normalize(df, config=config)

# Using config dict
config_dict = {
    'strings': {'trim': True, 'case': 'lower'},
    'columns': {'drop_original': False}
}
df = reader.normalize(df, config=config_dict)
```

#### f) Remove special characters in values
```python
# New parameter in config
config = NormalizationConfig(
    strings={'remove_special': True}
)
df = reader.normalize(df, config=config)
# "user@email.com" → "useremailcom"
```

## 🔄 Backward Compatibility

### ✅ ALL existing code continues working

```python
# This still works exactly the same
df = reader.normalize_columns(df)
df = reader.normalize(df, trim_strings=True, convert_case="lower")

# Legacy methods also work
reader._remove_accents("Café")  # → "Cafe"
reader._handle_duplicate_columns(["name", "name"])  # → ['name', 'name_1']
```

### 📝 No changes required in existing code

Your current code will continue working without modifications. The new features are **opt-in**.

## 🚀 Adoption Guide

### Recommended Gradual Migration

#### Step 1: Get familiar with presets
```python
# Try different presets in your code
df = reader.normalize(df, preset='basic')
df = reader.normalize(df, preset='full')
```

#### Step 2: Explore drop_original
```python
# If you don't need the original columns
df = reader.normalize(df, drop_original=True)
```

#### Step 3: Use custom configuration
```python
# For specific cases
config = NormalizationConfig.from_preset('basic')
config.strings['case'] = 'upper'
df = reader.normalize(df, config=config)
```

## 📊 Usage Examples

### Case 1: Basic Cleaning (Backward Compatible)
```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader()
df = reader.read("data.csv", normalize=True, normalize_columns=True)
# Works exactly like before
```

### Case 2: Normalization for Analysis
```python
# Replace original columns with normalized versions
df = reader.read(
    "data.csv",
    normalize=True,
    normalize_columns=True
)
df = reader.normalize(df, preset='analysis_ready')
```

### Case 3: Custom Normalization
```python
config = NormalizationConfig(
    strings={'trim': True, 'case': 'lower', 'remove_special': False},
    nulls={'standardize': True, 'values': ['MISSING', 'N/A', '']},
    columns={'drop_original': False, 'suffix': '_clean'}
)

df = reader.normalize(df, config=config)
```

### Case 4: Standardize Null Values
```python
# Custom null values for your domain
df = reader.normalize(
    df,
    standardize_nulls=True,
    null_values=['UNKNOWN', 'NOT AVAILABLE', '-'],
    drop_original=True
)
```

## 🧪 Tests

**53 new tests** were added specific to the refactoring:

- `test_normalization_config.py`: 10 tests for configuration
- `test_normalizers.py`: 23 tests for specialized normalizers
- `test_normalize_mixin_refactored.py`: 20 tests for backward compatibility

**Total: 104 tests passing ✅**

## 📚 Documentation

### New exported modules
```python
from pandas_toolkit.io.base import (
    NormalizationConfig,     # ← NEW
    ColumnNormalizer,        # ← NEW
    StringNormalizer,        # ← NEW
    NullNormalizer,          # ← NEW
)
```

### Direct use of normalizers (advanced)
```python
from pandas_toolkit.io.base.normalizers import ColumnNormalizer, NullNormalizer

# Normalize columns only
df = ColumnNormalizer.normalize(df, convert_case="upper")

# Normalize nulls only
df = NullNormalizer.normalize(df, null_values=['MISSING'])

# Get null summary
summary = NullNormalizer.get_null_summary(df)
print(summary)
#   column  null_count  null_percentage
# 0      A           2        33.333333
```

## 🔮 Next Steps (Future Phases)

### Phase 2: Core Normalizations (In development)
- Date normalization
- Numeric normalization
- Improvements in null handling

### Phase 3: Advanced Normalizations
- Boolean normalization
- Automatic type detection
- Category standardization

### Phase 4: Report System
- Detailed change reports
- Transformation logging
- Normalization statistics

## ❓ FAQ

**Q: Do I need to change my existing code?**  
A: No, all existing code continues working. Changes are backward compatible.

**Q: When should I use `drop_original=True`?**  
A: Use it when you're sure you don't need the original values and want to save memory.

**Q: Which preset should I use?**  
A: 
- `minimal`: For light cleaning
- `basic`: For most cases (recommended by default)
- `full`: For exhaustive cleaning
- `analysis_ready`: To prepare data for analysis (replaces columns)

**Q: Can I create my own presets?**  
A: Yes, you can extend `_PRESETS` in `config.py` or use custom configuration.

**Q: Are the `_remove_accents` and `_handle_duplicate_columns` methods still available?**  
A: Yes, they are marked as deprecated but still work for compatibility.

## 🐛 Issue Reporting

If you encounter any issues with the refactoring, please report:
- Problem description
- Code that failed
- Expected vs actual behavior
- Previous version that worked (if applicable)

## 📝 Changelog

### v2.0.0 - Phase 1 Refactoring (2026-02-25)

**Added:**
- Configuration system with `NormalizationConfig`
- Presets: `minimal`, `basic`, `full`, `analysis_ready`
- `drop_original` parameter to replace columns
- Improved `standardize_nulls` parameter
- Customizable `suffix` parameter
- Support for `config` dict/object
- Specialized normalizers: `ColumnNormalizer`, `StringNormalizer`, `NullNormalizer`
- 53 new tests

**Changed:**
- Refactored `NormalizeMixin` to use specialized normalizers
- Improved code modularity

**Maintained:**
- 100% backward compatibility
- All existing methods continue working
- No breaking changes

---

**Thank you for using the EDA Toolkit!** 🚀
