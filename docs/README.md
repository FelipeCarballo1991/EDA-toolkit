# EDA-Toolkit Documentation

Welcome to the complete EDA-Toolkit documentation. This folder contains detailed guides for all project components.

## 📚 Available Guides

### 🚀 Quick Start
- **[QuickStart_Guide.md](QuickStart_Guide.md)** - Start here. Quick start guide with basic examples to get started in 5 minutes.

### 📖 Readers

#### Delimited Files
- **[CSVReader_Guide.md](CSVReader_Guide.md)** - CSV reader with automatic encoding and delimiter detection. The most robust and widely used.
- **[DelimitedReaders_Guide.md](DelimitedReaders_Guide.md)** - TSVReader (tabs) and PipeReader (pipes). For files with specific delimiters.

#### Structured Formats
- **[ExcelReader_Guide.md](ExcelReader_Guide.md)** - Excel reader (.xlsx and .xls) with multi-sheet support and automatic engine detection.
- **[JSONReader_Guide.md](JSONReader_Guide.md)** - JSON and JSONL reader with multiple orientations (records, columns, etc.).
- **[HTMLReader_Guide.md](HTMLReader_Guide.md)** - HTML reader for tables (Oracle exports, web pages, etc.).

### 🏭 System Components

- **[Factory_Guide.md](Factory_Guide.md)** - ReaderFactory for automatic reader detection by file extension.
- **[Exporter_Guide.md](Exporter_Guide.md)** - FileExporter to export DataFrames to CSV, Excel, Parquet, JSON.
- **[Normalization_Guide.md](Normalization_Guide.md)** - Column and value normalization system.

## 🎯 Where to Start?

### If you're new to the toolkit:
1. Read [QuickStart_Guide.md](QuickStart_Guide.md)
2. Experiment with basic examples
3. Consult the specific guide for the format you need

### If you need to process a specific format:
- **Problematic CSV** → [CSVReader_Guide.md](CSVReader_Guide.md)
- **Excel with multiple sheets** → [ExcelReader_Guide.md](ExcelReader_Guide.md)
- **JSON API** → [JSONReader_Guide.md](JSONReader_Guide.md)
- **Oracle HTML export** → [HTMLReader_Guide.md](HTMLReader_Guide.md)
- **TSV/Pipe** → [DelimitedReaders_Guide.md](DelimitedReaders_Guide.md)

### If you want to automate:
- **Process any format** → [Factory_Guide.md](Factory_Guide.md)
- **Advanced export** → [Exporter_Guide.md](Exporter_Guide.md)
- **Data cleaning** → [Normalization_Guide.md](Normalization_Guide.md)

## 📋 Features Summary

### Available Readers

| Reader | Format | Main Features |
|--------|---------|----------------------------|
| **CSVReader** | `.csv`, `.txt`, `.dat` | Auto encoding/delimiter detection, bad lines capture |
| **TSVReader** | `.tsv` | Optimized for tabs, auto encoding detection |
| **PipeReader** | `.pipe` | Optimized for pipes, auto encoding detection |
| **ExcelReader** | `.xlsx`, `.xls` | Multi-sheet, auto engine fallback |
| **JSONReader** | `.json`, `.jsonl` | Multiple orientations, JSONL streaming |
| **HTMLReader** | `.html`, `.htm` | Multiple tables, Oracle exports |

### Common Features

All readers include:
- ✅ Column and value normalization
- ✅ Skip empty rows (leading/trailing)
- ✅ Export to CSV, Excel, Parquet, JSON
- ✅ Batch processing of multiple files
- ✅ Verbose mode for debugging
- ✅ Consistent API

### Factory and Exporter

- **ReaderFactory**: Automatic detection by extension
- **FileExporter**: Unified export to multiple formats

## 🔍 Quick Search

### By Use Case

| Use Case | Recommended Guide |
|-------------|------------------|
| File with unknown encoding | [CSVReader_Guide](CSVReader_Guide.md) |
| Excel with multiple sheets | [ExcelReader_Guide](ExcelReader_Guide.md) |
| API response | [JSONReader_Guide](JSONReader_Guide.md) |
| Oracle export | [HTMLReader_Guide](HTMLReader_Guide.md) |
| System logs (TSV) | [DelimitedReaders_Guide](DelimitedReaders_Guide.md) |
| Process folder with multiple formats | [Factory_Guide](Factory_Guide.md) |
| Split large Excel | [Exporter_Guide](Exporter_Guide.md) |
| Clean column names | [Normalization_Guide](Normalization_Guide.md) |
| Data from multiple sources | [Normalization_Guide](Normalization_Guide.md) |

### By Problem

| Problem | Solution |
|----------|----------|
| "UnicodeDecodeError" | [CSVReader - Encodings](CSVReader_Guide.md#automatic-detection) |
| "Columns don't match" | [CSVReader - Delimiters](CSVReader_Guide.md#automatic-detection) |
| "No module named 'openpyxl'" | [ExcelReader - Installation](ExcelReader_Guide.md#dependency-installation) |
| File too large for Excel | [Exporter - Excel Parts](Exporter_Guide.md#2-excel-parts-multiple-files) |
| Column names with accents | [Normalization - Columns](Normalization_Guide.md#column-normalization) |
| Values with extra spaces | [Normalization - Values](Normalization_Guide.md#value-normalization) |

## 📦 Guide Structure

Each guide includes:

1. **Description** - What it does and when to use it
2. **Main Features** - List of capabilities
3. **Installation** - Required dependencies
4. **Basic Usage** - Simple examples
5. **Methods** - Complete API with examples
6. **Complete Examples** - Real use cases
7. **Common Use Cases** - Typical scenarios
8. **Tips and Best Practices** - Recommendations
9. **Troubleshooting** - Problem solving
10. **Compatibility** - Requirements and platforms

## 💡 Quick Examples

### Basic Reading

```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader()
df = reader.read("data.csv", normalize=True, normalize_columns=True)
```

### With Factory (Recommended)

```python
from pandas_toolkit.io.factory import ReaderFactory

reader = ReaderFactory.create_reader("file.ext", verbose=True)
df = reader.read("file.ext", normalize=True)
```

### Export

```python
reader.export(df, method="excel", filename="report.xlsx")
```

## 🛠️ Additional Tools

### Example Scripts

In the project root:
- `ejemplo_oracle.py` - Complete script for Oracle HTML files
- `test_html_reader.py` - 9 HTMLReader examples

### Tests

In the `tests/` folder:
- Unit tests for each reader
- Usage examples
- Edge cases

### Notebooks

In `Testeos Jupyter/`:
- Interactive notebooks
- Step-by-step examples

## 📞 Support

- **Issues**: Report bugs on GitHub
- **Questions**: Open a discussion
- **Contribution**: Pull requests welcome

## 🎓 Suggested Reading Order

### For Beginners:
1. [QuickStart_Guide.md](QuickStart_Guide.md) - Fundamentals
2. [CSVReader_Guide.md](CSVReader_Guide.md) - Most used reader
3. [Factory_Guide.md](Factory_Guide.md) - Automation
4. [Exporter_Guide.md](Exporter_Guide.md) - Data output

### For Intermediate Users:
1. [Normalization_Guide.md](Normalization_Guide.md) - Advanced cleaning
2. [ExcelReader_Guide.md](ExcelReader_Guide.md) - Advanced Excel
3. Specific guides as needed

### For Advanced Users:
- All guides for reference
- Source code in `pandas_toolkit/`
- Tests for advanced examples

## 📊 Feature Comparison

| Feature | CSV | TSV | Pipe | Excel | JSON | HTML |
|---------|-----|-----|------|-------|------|------|
| Auto encoding | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Auto delimiter | ✅ | ✅ | ✅ | N/A | N/A | N/A |
| Multi-sheet/table | N/A | N/A | N/A | ✅ | N/A | ✅ |
| Normalization | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Batch processing | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Integrated export | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bad lines capture | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Streaming | ❌ | ❌ | ❌ | ❌ | ✅* | ❌ |

\* JSONL only

## 🔄 Updates

This directory is regularly updated. Check the dates in each guide.

**Last update**: February 2026

---

**Can't find what you're looking for?**

1. Check the main [README.md](../README.md)
2. Search in tests: `tests/`
3. Check examples: `test_*.py`
4. Open an issue on GitHub

---

*Happy Data Analyzing! 📊✨*
