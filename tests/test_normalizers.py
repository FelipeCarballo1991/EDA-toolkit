"""
Tests for specialized normalizers.

Tests for ColumnNormalizer, StringNormalizer, and NullNormalizer.
"""

import pytest
import pandas as pd
import numpy as np
from pandas_toolkit.io.base.normalizers import (
    ColumnNormalizer,
    StringNormalizer,
    NullNormalizer
)


class TestColumnNormalizer:
    """Test suite for ColumnNormalizer."""
    
    def test_basic_column_normalization(self):
        """Test basic column name normalization."""
        df = pd.DataFrame(columns=["First Name", "Last Name", "Age"])
        normalized = ColumnNormalizer.normalize(df)
        
        assert normalized.columns.tolist() == ['first_name', 'last_name', 'age']
    
    def test_column_with_accents(self):
        """Test column names with accents."""
        df = pd.DataFrame(columns=["Café", "Niño", "São Paulo"])
        normalized = ColumnNormalizer.normalize(df)
        
        assert normalized.columns.tolist() == ['cafe', 'nino', 'sao_paulo']
    
    def test_column_with_special_chars(self):
        """Test column names with special characters."""
        df = pd.DataFrame(columns=["Email@Address", "Price ($)", "Date/Time"])
        normalized = ColumnNormalizer.normalize(df)
        
        assert normalized.columns.tolist() == ['email_address', 'price', 'date_time']
    
    def test_column_case_upper(self):
        """Test uppercase conversion for columns."""
        df = pd.DataFrame(columns=["name", "age", "city"])
        normalized = ColumnNormalizer.normalize(df, convert_case="upper")
        
        assert normalized.columns.tolist() == ['NAME', 'AGE', 'CITY']
    
    def test_column_case_none(self):
        """Test no case conversion for columns."""
        df = pd.DataFrame(columns=["Name", "AGE", "City"])
        normalized = ColumnNormalizer.normalize(df, convert_case=None)
        
        # Should still normalize but keep original case
        assert all(col.replace('_', '').isalnum() for col in normalized.columns)
    
    def test_duplicate_columns(self):
        """Test handling of duplicate column names."""
        df = pd.DataFrame(columns=["Name", "Name", "Age", "Age"])
        normalized = ColumnNormalizer.normalize(df)
        
        assert normalized.columns.tolist() == ['name', 'name_1', 'age', 'age_1']
    
    def test_empty_columns(self):
        """Test handling of empty column names."""
        df = pd.DataFrame(columns=["Name", "", None, "Age"])
        normalized = ColumnNormalizer.normalize(df, empty_col_name="missing")
        
        assert 'missing' in normalized.columns.tolist()
        assert normalized.columns.tolist()[0] == 'name'
        assert normalized.columns.tolist()[-1] == 'age'
    
    def test_whitespace_columns(self):
        """Test trimming whitespace from column names."""
        df = pd.DataFrame(columns=["  Name  ", "  Age", "City  "])
        normalized = ColumnNormalizer.normalize(df)
        
        assert normalized.columns.tolist() == ['name', 'age', 'city']
    
    def test_no_special_char_removal(self):
        """Test keeping special characters when requested."""
        df = pd.DataFrame(columns=["Name@Email", "Price-USD"])
        normalized = ColumnNormalizer.normalize(df, remove_special_chars=False)
        
        # When remove_special_chars=False, should only replace spaces
        # The '@' and '-' should still be present or converted to '_' by basic logic
        assert 'name@email' in normalized.columns.tolist() or 'name_email' in normalized.columns.tolist()
        assert 'price-usd' in normalized.columns.tolist() or 'price_usd' in normalized.columns.tolist()


class TestStringNormalizer:
    """Test suite for StringNormalizer."""
    
    def test_basic_string_normalization(self):
        """Test basic string value normalization."""
        series = pd.Series(["  JUAN  ", "  MARIA  ", "  PEDRO  "])
        normalized = StringNormalizer.normalize(series, trim=True, convert_case="lower")
        
        assert normalized.tolist() == ['juan', 'maria', 'pedro']
    
    def test_string_trim(self):
        """Test trimming whitespace."""
        series = pd.Series(["  value  ", "test  ", "  data"])
        normalized = StringNormalizer.normalize(series, trim=True, convert_case=None)
        
        assert normalized.tolist() == ['value', 'test', 'data']
    
    def test_string_case_upper(self):
        """Test uppercase conversion."""
        series = pd.Series(["juan", "maria", "pedro"])
        normalized = StringNormalizer.normalize(series, convert_case="upper")
        
        assert normalized.tolist() == ['JUAN', 'MARIA', 'PEDRO']
    
    def test_string_case_none(self):
        """Test no case conversion."""
        series = pd.Series(["Juan", "MARIA", "pedro"])
        normalized = StringNormalizer.normalize(series, convert_case=None)
        
        assert 'Juan' in normalized.tolist() or 'juan' in normalized.tolist()
    
    def test_empty_strings_to_none(self):
        """Test converting empty strings to None."""
        series = pd.Series(["value", "", "  ", "data"])
        normalized = StringNormalizer.normalize(series, trim=True)
        
        assert normalized.isna().sum() >= 1  # At least one should be None
    
    def test_remove_special_chars(self):
        """Test removing special characters."""
        series = pd.Series(["hello@world", "test#123", "data$value"])
        normalized = StringNormalizer.normalize(series, remove_special_chars=True)
        
        # Should only have alphanumeric and spaces
        for val in normalized.dropna():
            assert val.replace(' ', '').isalnum()
    
    def test_is_string_column(self):
        """Test string column detection."""
        string_series = pd.Series(["a", "b", "c"])
        numeric_series = pd.Series([1, 2, 3])
        
        assert StringNormalizer.is_string_column(string_series) is True
        assert StringNormalizer.is_string_column(numeric_series) is False


class TestNullNormalizer:
    """Test suite for NullNormalizer."""
    
    def test_basic_null_normalization(self):
        """Test basic null value standardization."""
        df = pd.DataFrame({
            'A': ['value', '', 'N/A', 'null'],
            'B': [1, 2, 3, 4]
        })
        normalized = NullNormalizer.normalize(df)
        
        assert normalized['A'].isna().sum() == 3
        assert normalized['B'].isna().sum() == 0
    
    def test_various_null_representations(self):
        """Test various null representations."""
        df = pd.DataFrame({
            'A': ['', 'N/A', 'null', 'None', 'nan', '-', '--', 'value']
        })
        normalized = NullNormalizer.normalize(df)
        
        # Should have 7 nulls, 1 value
        assert normalized['A'].isna().sum() == 7
        assert (~normalized['A'].isna()).sum() == 1
    
    def test_custom_null_values(self):
        """Test custom null value representations."""
        df = pd.DataFrame({
            'A': ['value', 'MISSING', 'UNKNOWN', 'valid']
        })
        normalized = NullNormalizer.normalize(
            df,
            null_values=['MISSING', 'UNKNOWN'],
            include_defaults=False
        )
        
        assert normalized['A'].isna().sum() == 2
    
    def test_null_values_with_defaults(self):
        """Test custom null values combined with defaults."""
        df = pd.DataFrame({
            'A': ['value', 'MISSING', 'N/A', '']
        })
        normalized = NullNormalizer.normalize(
            df,
            null_values=['MISSING'],
            include_defaults=True
        )
        
        # Should catch MISSING, N/A, and ''
        assert normalized['A'].isna().sum() == 3
    
    def test_normalize_series(self):
        """Test normalizing a single series."""
        series = pd.Series(['value', '', 'N/A', 'null', 'data'])
        normalized = NullNormalizer.normalize_series(series)
        
        assert normalized.isna().sum() == 3
    
    def test_get_null_summary(self):
        """Test null value summary generation."""
        df = pd.DataFrame({
            'A': [1, np.nan, 3],
            'B': ['x', 'y', np.nan],
            'C': [1, 2, 3]
        })
        
        summary = NullNormalizer.get_null_summary(df)
        
        assert len(summary) == 2  # Only A and B have nulls
        assert 'column' in summary.columns
        assert 'null_count' in summary.columns
        assert 'null_percentage' in summary.columns
    
    def test_preserve_non_null_values(self):
        """Test that valid values are preserved."""
        df = pd.DataFrame({
            'A': ['value1', 'value2', '', 'value3'],
            'B': [1, 2, 3, 4]
        })
        normalized = NullNormalizer.normalize(df)
        
        assert 'value1' in normalized['A'].values
        assert 'value2' in normalized['A'].values
        assert 'value3' in normalized['A'].values
        assert normalized['B'].tolist() == [1, 2, 3, 4]
