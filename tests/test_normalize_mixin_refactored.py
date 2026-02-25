"""
Tests for refactored NormalizeMixin.

Tests to ensure backward compatibility and new functionality of the
refactored normalization system.
"""

import pytest
import pandas as pd
import numpy as np
from pandas_toolkit.io.readers import CSVReader
from pandas_toolkit.io.base import NormalizationConfig


class TestNormalizeMixinBackwardCompatibility:
    """Test backward compatibility of refactored NormalizeMixin."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reader = CSVReader()
    
    def test_normalize_columns_backward_compatible(self):
        """Test that normalize_columns still works as before."""
        df = pd.DataFrame(columns=["First Name", "  Last Name  ", "Émployee-ID"])
        normalized = self.reader.normalize_columns(df)
        
        assert normalized.columns.tolist() == ['first_name', 'last_name', 'employee_id']
    
    def test_normalize_values_backward_compatible(self):
        """Test that normalize (values) works as before."""
        df = pd.DataFrame({
            "Name": ["  JUAN  ", "  MARIA  "],
            "Status": ["  ACTIVE  ", "  "]
        })
        normalized = self.reader.normalize(df, trim_strings=True, convert_case="lower")
        
        # Should create _norm columns
        assert 'Name_norm' in normalized.columns
        assert 'Status_norm' in normalized.columns
        # Original columns should still exist
        assert 'Name' in normalized.columns
        assert 'Status' in normalized.columns
    
    def test_legacy_private_methods(self):
        """Test that legacy private methods still work."""
        # _remove_accents
        assert self.reader._remove_accents("Café") == "Cafe"
        
        # _handle_duplicate_columns
        cols = ["name", "name", "age"]
        result = self.reader._handle_duplicate_columns(cols)
        assert result == ['name', 'name_1', 'age']


class TestNormalizeMixinNewFeatures:
    """Test new features in refactored NormalizeMixin."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reader = CSVReader()
    
    def test_drop_original_columns(self):
        """Test drop_original parameter."""
        df = pd.DataFrame({
            "Name": ["  JUAN  ", "  MARIA  "],
            "Status": ["  ACTIVE  ", "  INACTIVE  "]
        })
        normalized = self.reader.normalize(
            df,
            drop_original=True,
            trim_strings=True,
            convert_case="lower"
        )
        
        # Should NOT create _norm columns
        assert 'Name_norm' not in normalized.columns
        assert 'Status_norm' not in normalized.columns
        # Original columns should exist with normalized values
        assert 'Name' in normalized.columns
        assert 'Status' in normalized.columns
        assert normalized['Name'].tolist() == ['juan', 'maria']
    
    def test_custom_suffix(self):
        """Test custom suffix for normalized columns."""
        df = pd.DataFrame({
            "Name": ["  JUAN  ", "  MARIA  "]
        })
        normalized = self.reader.normalize(
            df,
            suffix="_clean",
            drop_original=False
        )
        
        assert 'Name_clean' in normalized.columns
        assert 'Name_norm' not in normalized.columns
    
    def test_standardize_nulls(self):
        """Test null value standardization."""
        df = pd.DataFrame({
            "Name": ["Juan", "N/A", "null", "Maria"],
            "Age": ["25", "30", "", "35"]
        })
        normalized = self.reader.normalize(
            df,
            standardize_nulls=True,
            drop_original=True
        )
        
        # Should convert N/A and null to NaN
        assert normalized['Name'].isna().sum() >= 2
    
    def test_custom_null_values(self):
        """Test custom null values."""
        df = pd.DataFrame({
            "Status": ["Active", "MISSING", "UNKNOWN", "Inactive"]
        })
        normalized = self.reader.normalize(
            df,
            standardize_nulls=True,
            null_values=["MISSING", "UNKNOWN"],
            drop_original=True
        )
        
        assert normalized['Status'].isna().sum() >= 2
    
    def test_preset_basic(self):
        """Test using basic preset."""
        df = pd.DataFrame({
            "Name": ["  JUAN  ", "  MARIA  "],
            "Status": ["  ACTIVE  ", "N/A"]
        })
        normalized = self.reader.normalize(df, preset='basic')
        
        # Should apply basic normalization
        assert 'Name_norm' in normalized.columns
        # Should standardize nulls
        assert normalized['Status_norm'].isna().sum() >= 1
    
    def test_preset_minimal(self):
        """Test using minimal preset."""
        df = pd.DataFrame({
            "Name": ["  JUAN  ", "  MARIA  "]
        })
        normalized = self.reader.normalize(df, preset='minimal')
        
        # Minimal should only trim
        assert 'Name_norm' in normalized.columns
    
    def test_preset_full(self):
        """Test using full preset."""
        df = pd.DataFrame({
            "Name": ["  JUAN  ", "  MARIA  "],
            "Status": ["  ACTIVE  ", ""]
        })
        normalized = self.reader.normalize(df, preset='full')
        
        # Full should apply comprehensive normalization
        assert 'Name_norm' in normalized.columns
        assert normalized['Status_norm'].isna().sum() >= 1
    
    def test_config_object(self):
        """Test using config object."""
        config = NormalizationConfig(
            strings={'trim': True, 'case': 'upper'},
            columns={'drop_original': True, 'suffix': '_clean'}
        )
        
        df = pd.DataFrame({
            "Name": ["  juan  ", "  maria  "]
        })
        normalized = self.reader.normalize(df, config=config)
        
        # Should apply config settings
        assert 'Name' in normalized.columns
        assert 'Name_norm' not in normalized.columns
        # Should be uppercase (from config)
        assert normalized['Name'].str.isupper().all()
    
    def test_config_dict(self):
        """Test using config dictionary."""
        config_dict = {
            'strings': {'trim': True, 'case': 'upper'},
            'columns': {'drop_original': False, 'suffix': '_test'}
        }
        
        df = pd.DataFrame({
            "Name": ["  juan  ", "  maria  "]
        })
        normalized = self.reader.normalize(df, config=config_dict)
        
        # Should create column with custom suffix
        assert 'Name_test' in normalized.columns
    
    def test_drop_empty_rows_and_cols(self):
        """Test dropping empty rows and columns."""
        df = pd.DataFrame({
            "Name": ["Juan", np.nan, "Maria"],
            "Empty": [np.nan, np.nan, np.nan],
            "Age": [25, np.nan, 30]
        })
        
        normalized = self.reader.normalize(
            df,
            drop_empty_cols=True,
            drop_empty_rows=True,
            drop_original=True
        )
        
        # Empty column should be removed
        assert 'Empty' not in normalized.columns
        # Row with all NaN should be removed
        assert len(normalized) < len(df)
    
    def test_mixed_column_types(self):
        """Test normalization with mixed column types."""
        df = pd.DataFrame({
            "Name": ["  JUAN  ", "  MARIA  "],
            "Age": [25, 30],
            "Salary": [50000.0, 60000.0]
        })
        
        normalized = self.reader.normalize(df, drop_original=False)
        
        # Should only create _norm columns for string columns
        assert 'Name_norm' in normalized.columns
        # Numeric columns should not be duplicated
        # (or if they are, it's acceptable behavior)
        assert 'Age' in normalized.columns
        assert 'Salary' in normalized.columns
    
    def test_remove_special_chars_in_values(self):
        """Test removing special characters from values."""
        config = NormalizationConfig(
            strings={'remove_special': True},
            columns={'drop_original': True}
        )
        
        df = pd.DataFrame({
            "Email": ["user@email.com", "test#user"]
        })
        
        normalized = self.reader.normalize(df, config=config)
        
        # Special chars should be removed
        assert '@' not in str(normalized['Email'].iloc[0])
        assert '#' not in str(normalized['Email'].iloc[1])


class TestNormalizeMixinEdgeCases:
    """Test edge cases and error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reader = CSVReader()
    
    def test_empty_dataframe(self):
        """Test normalization on empty DataFrame."""
        df = pd.DataFrame()
        normalized = self.reader.normalize(df)
        
        assert len(normalized) == 0
    
    def test_dataframe_with_nulls_only(self):
        """Test DataFrame with only null values."""
        df = pd.DataFrame({
            "A": [np.nan, np.nan],
            "B": [np.nan, np.nan]
        })
        
        normalized = self.reader.normalize(
            df,
            drop_empty_cols=True,
            drop_empty_rows=True
        )
        
        # Should remove all rows and columns
        assert len(normalized) == 0 or len(normalized.columns) == 0
    
    def test_single_column_dataframe(self):
        """Test normalization on single column DataFrame."""
        df = pd.DataFrame({"Name": ["  JUAN  ", "  MARIA  "]})
        normalized = self.reader.normalize(df, drop_original=False)
        
        assert 'Name' in normalized.columns
        assert 'Name_norm' in normalized.columns
    
    def test_single_row_dataframe(self):
        """Test normalization on single row DataFrame."""
        df = pd.DataFrame({"Name": ["  JUAN  "], "Age": [25]})
        normalized = self.reader.normalize(df)
        
        assert len(normalized) == 1
    
    def test_unicode_values(self):
        """Test normalization with Unicode characters."""
        df = pd.DataFrame({
            "Name": ["José", "François", "北京"]
        })
        
        normalized = self.reader.normalize(df, drop_original=False)
        
        # Should handle Unicode without errors
        assert 'Name_norm' in normalized.columns
        assert len(normalized) == 3
