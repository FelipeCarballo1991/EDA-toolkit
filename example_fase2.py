"""
Example: Using Fase 2 normalization features.
Demonstrates date normalization, numeric normalization, and reporting.
"""

import pandas as pd
from pandas_toolkit.io.readers import CSVReader
from pandas_toolkit.io.base.normalizers import DateNormalizer

# ============================================================
# EXAMPLE 1: View available date formats
# ============================================================
print("=" * 60)
print("AVAILABLE DATE FORMATS")
print("=" * 60)
formats = DateNormalizer.get_available_formats()
for code, description in list(formats.items())[:5]:  # Show first 5
    print(f"{code:15} → {description}")
print(f"...and {len(formats) - 5} more formats available\n")


# ============================================================
# EXAMPLE 2: Basic normalization with reporting
# ============================================================
print("=" * 60)
print("EXAMPLE 2: BASIC NORMALIZATION WITH REPORTING")
print("=" * 60)

# Create sample data
data = {
    'name': ['  JOHN  ', '  MARIA  ', 'BOB'],
    'date': ['01/12/2024', '15/12/2024', '31/12/2024'],
    'price': ['$1,234.56', '€500.00', '$750'],
    'discount': ['10%', '25%', '5%']
}

df = pd.DataFrame(data)
print("\n📊 ORIGINAL DATA:")
print(df)

# Create a temporary CSV
temp_file = 'temp_example.csv'
df.to_csv(temp_file, index=False)

# Read and normalize
reader = CSVReader()
df = reader.read(temp_file)

# Apply normalization with full preset
normalized, report = reader.normalize(
    df,
    preset='full',
    verbose=True,
    return_report=True
)

print("\n\n📋 NORMALIZATION REPORT:")
print(report.summary())

print("\n\n✨ NORMALIZED DATA (new columns created):")
print(normalized[['name', 'name_norm', 'date', 'date_norm', 'price', 'price_norm', 'discount', 'discount_norm']].head())


# ============================================================
# EXAMPLE 3: Custom configuration
# ============================================================
print("\n\n" + "=" * 60)
print("EXAMPLE 3: CUSTOM CONFIGURATION")
print("=" * 60)

from pandas_toolkit.io.base.normalizers import NormalizationConfig

# Create custom config
config = NormalizationConfig.from_preset('basic')
config.dates['normalize'] = True
config.dates['format'] = '%d/%m/%Y'  # European format
config.numbers['normalize'] = True

# Create new test data
df2 = pd.DataFrame({
    'event': ['Meeting', 'Call', 'Lunch'],
    'when': ['2024-12-25', '12/31/2024', '15-01-2025'],
    'cost': ['$100.00', '€50.50', '£75']
})

df2.to_csv(temp_file, index=False)
df2 = reader.read(temp_file)

normalized2, report2 = reader.normalize(
    df2,
    config=config,
    return_report=True,
    verbose=False
)

print("\n📊 ORIGINAL:")
print(df2)

print("\n✨ NORMALIZED (European date format):")
print(normalized2)

print("\n📋 TRANSFORMATION STATS:")
for trans in report2.transformations:
    print(f"  • {trans.description}: {trans.values_changed} values")


# ============================================================
# EXAMPLE 4: Analysis-ready preset (replaces columns)
# ============================================================
print("\n\n" + "=" * 60)
print("EXAMPLE 4: ANALYSIS-READY PRESET")
print("=" * 60)

df3 = pd.DataFrame({
    'product': ['  LAPTOP  ', '  MOUSE  ', '  KEYBOARD  '],
    'sale_date': ['01/12/2024', '15/12/2024', '20/12/2024'],
    'revenue': ['$1,500.00', '$25.50', '$89.99'],
    'margin': ['15%', '40%', '25%']
})

df3.to_csv(temp_file, index=False)
df3 = reader.read(temp_file)

print("\n📊 BEFORE normalization:")
print(df3)
print(f"Columns: {list(df3.columns)}")

# Use analysis_ready preset (replaces original columns)
normalized3, report3 = reader.normalize(
    df3,
    preset='analysis_ready',
    return_report=True,
    verbose=False
)

print("\n✨ AFTER normalization (columns replaced):")
print(normalized3)
print(f"Columns: {list(normalized3.columns)}")
print("\n💡 Notice: No '_norm' suffix - original columns were replaced!")

print("\n📋 Ready for analysis:")
print(f"  • revenue column type: {normalized3['revenue'].dtype}")
print(f"  • margin column type: {normalized3['margin'].dtype}")
print(f"  • Can now do math: Total revenue = ${normalized3['revenue'].sum():,.2f}")


# ============================================================ # EXAMPLE 5: Export reports
# ============================================================
print("\n\n" + "=" * 60)
print("EXAMPLE 5: EXPORT REPORTS")
print("=" * 60)

# Export to JSON
report.to_json('normalization_report.json')
print("✅ Report exported to: normalization_report.json")

# Export to Markdown  
report.to_markdown('normalization_report.md')
print("✅ Report exported to: normalization_report.md")

print("\n📊 Report Statistics:")
print(f"  • Total transformations: {len(report.transformations)}")
print(f"  • Total values modified: {sum(report.stats.values())}")
print(f"  • Time elapsed: {report.time_elapsed:.3f}s")
print(f"  • Warnings: {len(report.warnings)}")

# Clean up
import os
try:
    os.remove(temp_file)
    print("\n🧹 Cleaned up temporary file")
except:
    pass

print("\n" + "=" * 60)
print("✅ EXAMPLES COMPLETE!")
print("=" * 60)
print("\nNext steps:")
print("  1. Try with your own data")
print("  2. Experiment with different presets")
print("  3. Create custom configurations")
print("  4. Export and share normalization reports")
print("\nHappy normalizing! 🎉")
