"""
Normalization modules for data cleaning and standardization.

This package contains specialized normalizers for different data types and aspects:
- ColumnNormalizer: Column name normalization
- StringNormalizer: String value normalization
- NullNormalizer: Null value standardization
- NumericNormalizer: Numeric value normalization (future)
- DateNormalizer: Date normalization (future)
- BooleanNormalizer: Boolean value normalization (future)
- TypeDetector: Automatic type detection (future)
- CategoryNormalizer: Category standardization (future)
"""

from .config import NormalizationConfig
from .column_normalizer import ColumnNormalizer
from .string_normalizer import StringNormalizer
from .null_normalizer import NullNormalizer

__all__ = [
    "NormalizationConfig",
    "ColumnNormalizer",
    "StringNormalizer",
    "NullNormalizer",
]
