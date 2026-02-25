# Normalizers Module

## Overview

This module provides specialized normalizers for data cleaning and standardization. Each normalizer handles a specific aspect of data normalization, making the code more modular and maintainable.

## Components

### 1. NormalizationConfig
Central configuration system with preset support.

```python
from pandas_toolkit.io.base import NormalizationConfig

# Use a preset
config = NormalizationConfig.from_preset('basic')

# Custom configuration
config = NormalizationConfig(
    strings={'trim': True, 'case': 'lower'},
    nulls={'standardize': True},
    columns={'drop_original': False}
)
```

### 2. ColumnNormalizer
Specialized normalizer for column names.

```python
from pandas_toolkit.io.base import ColumnNormalizer

df = ColumnNormalizer.normalize(
    df,
    convert_case="lower",
    remove_special_chars=True
)
```

### 3. StringNormalizer
Specialized normalizer for string values.

```python
from pandas_toolkit.io.base import StringNormalizer

series = StringNormalizer.normalize(
    df['column'],
    trim=True,
    convert_case="lower",
    remove_special_chars=False
)
```

### 4. NullNormalizer
Specialized normalizer for null/missing values.

```python
from pandas_toolkit.io.base import NullNormalizer

# Standardize nulls
df = NullNormalizer.normalize(
    df,
    null_values=['MISSING', 'UNKNOWN']
)

# Get null summary
summary = NullNormalizer.get_null_summary(df)
```

## Presets

### Available Presets

#### `minimal`
- Trim whitespace only
- Minimal null standardization

#### `basic` (Recommended)
- Trim whitespace
- Lowercase conversion
- Standard null values

#### `full`
- Comprehensive normalization
- All transformations enabled
- Future normalizers included

#### `analysis_ready`
- Optimized for analysis
- Replaces original columns
- Comprehensive cleaning

## Architecture

```
normalizers/
├── __init__.py              # Public exports
├── config.py                # NormalizationConfig + presets
├── column_normalizer.py     # Column name normalization
├── string_normalizer.py     # String value normalization
└── null_normalizer.py       # Null value standardization
```

## Future Additions

The following normalizers are planned for future phases:

- **NumericNormalizer**: Number formatting and currency handling
- **DateNormalizer**: Date parsing and standardization
- **BooleanNormalizer**: Boolean value standardization
- **TypeDetector**: Automatic type detection and conversion
- **CategoryNormalizer**: Category standardization with fuzzy matching

## Usage Examples

### Example 1: Direct Normalizer Usage
```python
from pandas_toolkit.io.base.normalizers import (
    ColumnNormalizer,
    StringNormalizer,
    NullNormalizer
)

# Normalize column names
df = ColumnNormalizer.normalize(df, convert_case="lower")

# Standardize nulls
df = NullNormalizer.normalize(df)

# Normalize string column
df['name'] = StringNormalizer.normalize(df['name'], trim=True)
```

### Example 2: Via Mixin (Recommended)
```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader()

# Using presets
df = reader.normalize(df, preset='basic')

# Using config
config = NormalizationConfig.from_preset('full')
df = reader.normalize(df, config=config)

# Using parameters
df = reader.normalize(
    df,
    drop_original=True,
    standardize_nulls=True,
    trim_strings=True
)
```

## Tests

All normalizers have comprehensive test coverage:

- `tests/test_normalization_config.py`: Configuration tests
- `tests/test_normalizers.py`: Normalizer unit tests
- `tests/test_normalize_mixin_refactored.py`: Integration tests

Run tests:
```bash
pytest tests/test_normalizers.py -v
```

## Contributing

When adding new normalizers:

1. Create a new file `{name}_normalizer.py`
2. Implement the normalizer class
3. Add exports to `__init__.py`
4. Add configuration options to `config.py`
5. Write comprehensive tests
6. Update documentation

## See Also

- [Normalization Guide](../Normalization_Guide.md)
- [Phase 1 Refactoring Guide](../REFACTORING_PHASE1_GUIDE.md)
- [API Documentation](../README.md)
