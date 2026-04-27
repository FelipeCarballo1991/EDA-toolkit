# Normalization Presets Guide

## Overview

The EDA Toolkit provides four predefined normalization presets, each designed for specific use cases. This guide details the exact transformations applied by each preset.

---

## Quick Comparison

| Preset | Use Case | Drop Original Columns | Date/Number Normalization |
|--------|----------|----------------------|---------------------------|
| **minimal** | Light cleanup, preserve data as-is | ❌ No | ❌ No |
| **basic** | Standard text normalization | ❌ No | ❌ No |
| **full** | Comprehensive normalization, keep originals | ❌ No | ✅ Yes |
| **analysis_ready** | Production ML/Analytics pipelines | ✅ Yes | ✅ Yes |

---

## Preset Details

### 1. `minimal` - Minimal Cleanup

**Purpose**: Light-touch data cleanup while preserving original values and formats.

**Best For**:
- Initial data exploration
- When you need to preserve exact original values
- Quick reports where formatting isn't critical

**String Transformations**:
- ✅ Trim leading/trailing whitespace
- ❌ No case conversion
- ❌ No special character removal

**Null Standardization**:
- ✅ Standardize basic null values:
  - Empty strings (`''`)
  - String 'nan'
- ❌ No extended null values

**Date Normalization**:
- ❌ Disabled

**Numeric Normalization**:
- ❌ Disabled

**Boolean Normalization**:
- ❌ Disabled

**Type Detection**:
- ❌ Disabled

**Category Standardization**:
- ❌ Disabled

**Column Behavior**:
- Creates new columns with `_norm` suffix
- Original columns preserved
- Empty columns retained

**Example**:
```python
# Input:  "  John  " → Output: "John"
# Input:  "MARIA"   → Output: "MARIA" (case preserved)
# Input:  "$1,234"  → Output: "$1,234" (no numeric cleaning)
```

---

### 2. `basic` - Basic Normalization

**Purpose**: Standard text normalization for consistent data presentation.

**Best For**:
- General-purpose data cleaning
- Text-heavy datasets
- User-facing reports and dashboards

**String Transformations**:
- ✅ Trim leading/trailing whitespace
- ✅ Convert to lowercase
- ❌ No special character removal

**Null Standardization**:
- ✅ Standardize common null values:
  - Empty strings (`''`)
  - `'N/A'`, `'null'`, `'None'`, `'nan'`
  - Single dash (`'-'`)
  - Double dash (`'--'`)

**Date Normalization**:
- ❌ Disabled

**Numeric Normalization**:
- ❌ Disabled

**Boolean Normalization**:
- ❌ Disabled

**Type Detection**:
- ❌ Disabled

**Category Standardization**:
- ❌ Disabled

**Column Behavior**:
- Creates new columns with `_norm` suffix
- Original columns preserved
- Empty columns retained

**Example**:
```python
# Input:  "  JOHN  " → Output: "john"
# Input:  "N/A"      → Output: NaN
# Input:  "ACTIVE"   → Output: "active"
# Input:  "$1,500"   → Output: "$1,500" (no numeric cleaning)
```

---

### 3. `full` - Full Normalization

**Purpose**: Comprehensive data normalization including dates and numbers, while preserving original data.

**Best For**:
- Data validation and auditing
- When you need both raw and clean versions
- Exploratory data analysis
- Data quality reports

**String Transformations**:
- ✅ Trim leading/trailing whitespace
- ✅ Convert to lowercase
- ✅ Remove special characters (except letters, numbers, spaces)

**Null Standardization**:
- ✅ Standardize extensive null values:
  - Empty strings (`''`)
  - `'N/A'`, `'n/a'`, `'NA'`
  - `'null'`, `'NULL'`
  - `'None'`, `'NONE'`
  - `'nan'`, `'NaN'`, `'NAN'`
  - Dashes: `'-'`, `'--'`, `'---'`
  - `'nil'`, `'NIL'`

**Date Normalization**:
- ✅ **Enabled**
- Output format: `%Y-%m-%d` (ISO 8601: 2024-12-25)
- Auto-detects 14 common date formats:
  - DD/MM/YYYY, DD-MM-YYYY
  - MM/DD/YYYY (US), MM-DD-YYYY
  - YYYY-MM-DD (ISO), YYYY/MM/DD
  - DD.MM.YYYY, YYYY.MM.DD
  - Month DD, YYYY (Dec 25, 2024)
  - DD Month YYYY (25 Dec 2024)
  - YYYYMMDD (compact)
  - And more...

**Numeric Normalization**:
- ✅ **Enabled**
- Remove currency symbols:
  - `$`, `€`, `£`, `¥`, `₹`, `R$`
  - Text: USD, EUR, GBP
- Handle thousand separators:
  - Comma: `1,234,567`
  - Period (EU): `1.234.567`
  - Space: `1 234 567`
- Handle decimal separators (both `.` and `,`)
- Convert percentages: `25%` → `0.25`
- Handle negative numbers: `($100)` → `-100`

**Boolean Normalization**:
- ✅ **Enabled**
- True values: `'yes'`, `'y'`, `'si'`, `'sí'`, `'1'`, `'true'`, `'t'`, `'verdadero'`
- False values: `'no'`, `'n'`, `'0'`, `'false'`, `'f'`, `'falso'`

**Type Detection**:
- ✅ Auto-detect and convert appropriate data types

**Category Standardization**:
- ✅ **Enabled**
- Fuzzy matching threshold: 0.85
- Standardizes similar category values
- Custom mappings supported

**Column Behavior**:
- Creates new columns with `_norm` suffix
- **Original columns preserved** ⭐
- Drops empty columns

**Example**:
```python
# Strings:
# Input:  "  JOHN!@#  " → Output: "john"

# Dates:
# Input:  "25/12/2024"  → Output: "2024-12-25"
# Input:  "Dec 25, 2024" → Output: "2024-12-25"

# Numbers:
# Input:  "$1,234.56"   → Output: 1234.56
# Input:  "€500,50"     → Output: 500.50
# Input:  "25%"         → Output: 0.25

# Booleans:
# Input:  "yes"         → Output: True
# Input:  "no"          → Output: False

# Result: df has both 'price' and 'price_norm' columns
```

---

### 4. `analysis_ready` - Analysis Ready

**Purpose**: Transform data into clean, analysis-ready format optimized for ML pipelines and statistical analysis.

**Best For**:
- Machine Learning pipelines
- Statistical analysis
- Production data workflows
- When storage space is a concern
- Final dataset preparation

**String Transformations**:
- ✅ Trim leading/trailing whitespace
- ✅ Convert to lowercase
- ❌ No special character removal (preserves data integrity)

**Null Standardization**:
- ✅ Standardize common null values:
  - Empty strings (`''`)
  - `'N/A'`, `'null'`, `'None'`, `'nan'`
  - Single dash (`'-'`)
  - Double dash (`'--'`)

**Date Normalization**:
- ✅ **Enabled**
- Output format: `%Y-%m-%d` (ISO 8601: 2024-12-25)
- Auto-detects 14 common date formats
- Infers format automatically

**Numeric Normalization**:
- ✅ **Enabled**
- Remove currency symbols: `$`, `€`, `£`, `¥`, etc.
- Handle thousand separators (comma, period, space)
- Decimal separator: period (`.`)
- Thousand separator: comma (`,`)
- Convert percentages: `25%` → `0.25`

**Boolean Normalization**:
- ✅ **Enabled**
- Standardizes yes/no, true/false, 1/0 variations

**Type Detection**:
- ✅ Auto-detect and convert appropriate data types

**Category Standardization**:
- ❌ Disabled (to preserve unique values for encoding)

**Column Behavior**:
- **Replaces original columns** ⚠️
- No `_norm` suffix needed
- Drops empty columns
- Optimized for memory efficiency

**Key Difference from `full`**:
- **Overwrites** original columns instead of creating new ones
- More memory efficient
- Cleaner column names (no suffixes)
- Cannot compare with original values

**Example**:
```python
# Original DataFrame:
# | name      | date       | price     | margin |
# |-----------|------------|-----------|--------|
# | "  JOHN " | 01/12/2024 | $1,234.56 | 15%    |

# After normalization (columns replaced):
# | name | date       | price   | margin |
# |------|------------|---------|--------|
# | john | 2024-12-01 | 1234.56 | 0.15   |

# Note: Only 4 columns total (originals replaced)
```

---

## Configuration Details

### String Normalization Settings

| Setting | minimal | basic | full | analysis_ready |
|---------|---------|-------|------|----------------|
| `trim` | ✅ | ✅ | ✅ | ✅ |
| `case` | None | `'lower'` | `'lower'` | `'lower'` |
| `remove_special` | ❌ | ❌ | ✅ | ❌ |

### Null Standardization Settings

All presets use `standardize: true` with varying null value lists:

- **minimal**: `['', 'nan']` (2 values)
- **basic**: `['', 'N/A', 'null', 'None', 'nan', '-', '--']` (7 values)
- **full**: Comprehensive list (16 values)
- **analysis_ready**: Common values (7 values)

### Date Normalization Settings

| Setting | minimal | basic | full | analysis_ready |
|---------|---------|-------|------|----------------|
| `normalize` | ❌ | ❌ | ✅ | ✅ |
| `format` | - | - | `'%Y-%m-%d'` | `'%Y-%m-%d'` |
| `infer` | - | - | ✅ | ✅ |

### Number Normalization Settings

| Setting | minimal | basic | full | analysis_ready |
|---------|---------|-------|------|----------------|
| `normalize` | ❌ | ❌ | ✅ | ✅ |
| `remove_currency` | - | - | ✅ | ✅ |
| `decimal_separator` | - | - | `'.'` | `'.'` |
| `thousand_separator` | - | - | `','` | `','` |
| `handle_percentages` | - | - | ✅ | ✅ |

### Column Management Settings

| Setting | minimal | basic | full | analysis_ready |
|---------|---------|-------|------|----------------|
| `drop_original` | ❌ | ❌ | ❌ | ✅ |
| `suffix` | `'_norm'` | `'_norm'` | `'_norm'` | `'_norm'` |
| `drop_empty` | ❌ | ❌ | ✅ | ✅ |

---

## Usage Examples

### Using Presets

```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader()
df = reader.read("data.csv")

# Option 1: Direct preset parameter
df_normalized = reader.normalize(df, preset='basic')

# Option 2: With reporting
df_normalized, report = reader.normalize(
    df, 
    preset='full', 
    return_report=True
)

# Option 3: Verbose mode
df_normalized = reader.normalize(
    df, 
    preset='analysis_ready', 
    verbose=True
)
```

### Custom Configuration from Preset

```python
from pandas_toolkit.io.base.normalizers import NormalizationConfig

# Start with a preset
config = NormalizationConfig.from_preset('full')

# Customize specific settings
config.dates['format'] = '%d/%m/%Y'  # European format
config.strings['case'] = 'upper'     # Uppercase instead

# Apply custom configuration
df_normalized = reader.normalize(df, config=config)
```

### Comparing Presets

```python
import pandas as pd

# Sample data
df = pd.DataFrame({
    'name': ['  JOHN  ', '  MARIA  '],
    'date': ['25/12/2024', '01/01/2025'],
    'price': ['$1,234.56', '€500.00']
})

# Compare presets
for preset in ['minimal', 'basic', 'full', 'analysis_ready']:
    result = reader.normalize(df.copy(), preset=preset)
    print(f"\n{preset.upper()}:")
    print(result)
```

---

## Choosing the Right Preset

### Decision Tree

```
Do you need date/number normalization?
│
├─ NO ─→ Do you need case conversion?
│        │
│        ├─ NO ─→ Use 'minimal'
│        └─ YES ─→ Use 'basic'
│
└─ YES ─→ Do you need to keep original data?
         │
         ├─ YES ─→ Use 'full'
         └─ NO ─→ Use 'analysis_ready'
```

### Common Scenarios

| Scenario | Recommended Preset | Reason |
|----------|-------------------|--------|
| Quick data exploration | `minimal` | Minimal changes, fast |
| Text cleaning for reports | `basic` | Standardized text, no data type changes |
| Data quality audit | `full` | Compare before/after, comprehensive |
| Training ML model | `analysis_ready` | Clean numeric data, memory efficient |
| API response formatting | `basic` | Consistent text, preserve structure |
| Statistical analysis | `analysis_ready` | Proper data types, ready for math |
| Data warehouse loading | `full` | Track transformations, keep history |

---

## Advanced Features

### Verbose Mode

All presets support verbose output to track transformation progress:

```python
df_normalized = reader.normalize(df, preset='full', verbose=True)

# Output:
# [NORMALIZE] Starting normalization with preset 'full'...
# [NORMALIZE] → Standardizing null values...
# [NORMALIZE]   Standardized 12 null values
# [NORMALIZE] → Normalizing dates...
# [NORMALIZE]   Normalized 45 dates in 3 columns
# [NORMALIZE] → Normalizing numeric values...
# [NORMALIZE]   Normalized 120 numeric values in 5 columns
# [NORMALIZE] ✓ Normalization complete (0.25s, 177 values modified)
```

### Reporting

Generate detailed reports of all transformations:

```python
df_normalized, report = reader.normalize(
    df, 
    preset='full', 
    return_report=True
)

# View summary
print(report.summary())

# Export reports
report.to_json('normalization_report.json')
report.to_markdown('normalization_report.md')

# Get transformation statistics
stats_df = report.get_transformation_stats()
```

### Report Contents

Each report includes:

- ✅ Timestamp and preset used
- ✅ Number of rows/columns processed
- ✅ Execution time
- ✅ List of all transformations applied
- ✅ Count of values changed per transformation
- ✅ Column-by-column change details
- ✅ Warnings for failed conversions
- ✅ Configuration snapshot

---

## Performance Considerations

### Speed Comparison (1M rows)

| Preset | Avg Time | Memory Usage |
|--------|----------|--------------|
| `minimal` | ~0.5s | Low |
| `basic` | ~0.8s | Low |
| `full` | ~2.5s | High (2x columns) |
| `analysis_ready` | ~2.2s | Medium |

### Optimization Tips

1. **For large datasets (>1M rows)**:
   - Use `analysis_ready` to avoid column duplication
   - Process in chunks if memory is limited

2. **For wide datasets (>100 columns)**:
   - Use `minimal` or `basic` if date/number normalization isn't needed
   - Consider selective normalization on specific columns

3. **For repeated processing**:
   - Cache the configuration object
   - Use `verbose=False` in production

---

## FAQ

**Q: Can I modify a preset without creating a custom config?**  
A: No, presets are immutable. Create a config from preset, then modify it.

**Q: What happens to columns not affected by normalization?**  
A: They remain unchanged (except in `analysis_ready` where empty columns are dropped).

**Q: Can I use multiple presets on the same data?**  
A: Yes, but normalize with one preset at a time. Presets are mutually exclusive.

**Q: Are transformations reversible?**  
A: Only if you use `full` preset (keeps originals). `analysis_ready` overwrites data.

**Q: What if date/number detection fails?**  
A: Failed conversions are reported as warnings and values remain unchanged (or set to NaN).

---

## Related Documentation

- [Quick Start Guide](QuickStart_Guide.md) - Basic usage
- [Normalization Guide](Normalization_Guide.md) - Detailed normalization features
- [Configuration Guide](Configuration_Guide.md) - Custom configuration
- [API Reference](../README.md) - Full API documentation

---

**Last Updated**: February 2026  
**Version**: 2.0 (Fase 2)
