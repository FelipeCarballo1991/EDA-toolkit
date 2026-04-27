"""
Tests for Phase 2 normalization features: dates, numbers, and reporting.
"""

import pandas as pd
import pytest
import numpy as np
import json
from datetime import datetime

from pandas_toolkit.io.base.normalizers import (
    DateNormalizer,
    NumericNormalizer,
    NormalizationReport,
    NormalizationConfig,
)
from pandas_toolkit.io.readers import CSVReader


class TestDateNormalizer:
    """Test date normalization functionality."""
    
    def test_normalize_single_format(self):
        """Test normalizing dates in a single format."""
        series = pd.Series(['01/12/2024', '15/12/2024', '31/12/2024'])
        normalized, stats = DateNormalizer.normalize(series, output_format='%Y-%m-%d')
        
        assert normalized[0] == '2024-12-01'
        assert normalized[1] == '2024-12-15'
        assert normalized[2] == '2024-12-31'
        assert stats['successful_parses'] == 3
        assert stats['failed_parses'] == 0
    
    def test_normalize_multiple_formats(self):
        """Test normalizing dates in multiple formats."""
        series = pd.Series([
            '01/12/2024',      # dd/mm/yyyy
            '2024-12-15',      # yyyy-mm-dd
            '12/31/2024',      # mm/dd/yyyy
            '2024.12.20'       # yyyy.mm.dd
        ])
        normalized, stats = DateNormalizer.normalize(series, output_format='%d/%m/%Y')
        
        assert stats['successful_parses'] >= 3  # At least 3 should parse
        assert normalized[0] == '01/12/2024'
        assert normalized[1] == '15/12/2024'
    
    def test_is_date_column(self):
        """Test date column detection."""
        date_series = pd.Series(['01/12/2024', '15/12/2024', '31/12/2024'])
        string_series = pd.Series(['apple', 'banana', 'cherry'])
        number_series = pd.Series([1, 2, 3])
        
        assert DateNormalizer.is_date_column(date_series) is True
        assert DateNormalizer.is_date_column(string_series) is False
        assert DateNormalizer.is_date_column(number_series) is False
    
    def test_get_available_formats(self):
        """Test getting available date formats."""
        formats = DateNormalizer.get_available_formats()
        
        assert len(formats) > 0
        assert any('dd/mm/yyyy' in fmt.lower() for fmt in formats.values())
        assert any('iso' in fmt.lower() for fmt in formats.values())
    
    def test_detect_date_format(self):
        """Test date format detection."""
        # Test dd/mm/yyyy
        series = pd.Series(['25/12/2024', '26/12/2024', '27/12/2024'])
        fmt = DateNormalizer.detect_date_format(series)
        assert fmt == '%d/%m/%Y'
        
        # Test yyyy-mm-dd (ISO)
        series = pd.Series(['2024-12-25', '2024-12-26', '2024-12-27'])
        fmt = DateNormalizer.detect_date_format(series)
        assert fmt == '%Y-%m-%d'
    
    def test_handle_invalid_dates(self):
        """Test handling of invalid date values."""
        series = pd.Series(['01/12/2024', 'not a date', '31/12/2024', None])
        normalized, stats = DateNormalizer.normalize(series, output_format='%Y-%m-%d')
        
        assert stats['successful_parses'] == 2
        assert stats['failed_parses'] >= 1
        assert pd.isna(normalized[1])  # Invalid date should be NaN


class TestNumericNormalizer:
    """Test numeric normalization functionality."""
    
    def test_normalize_currency(self):
        """Test normalizing currency values."""
        series = pd.Series(['$1,234.56', '€500.00', '£1,000'])
        normalized, stats = NumericNormalizer.normalize(series)
        
        assert normalized[0] == 1234.56
        assert normalized[1] == 500.00
        assert normalized[2] == 1000.00
        assert stats['currency_symbols_removed'] == 3
    
    def test_normalize_percentages(self):
        """Test normalizing percentage values."""
        series = pd.Series(['50%', '75.5%', '100%'])
        normalized, stats = NumericNormalizer.normalize(series, handle_percentages=True)
        
        assert normalized[0] == 0.50
        assert normalized[1] == 0.755
        assert normalized[2] == 1.00
        assert stats['percentages_converted'] == 3
    
    def test_normalize_thousand_separators(self):
        """Test normalizing thousand separators."""
        series = pd.Series(['1,234,567', '1.234.567', '1 234 567'])
        normalized, stats = NumericNormalizer.normalize(series)
        
        # At least US format should work
        assert normalized[0] == 1234567
        assert stats['separators_removed'] >= 1
    
    def test_is_numeric_column(self):
        """Test numeric column detection."""
        numeric_series = pd.Series(['$123', '€456', '789'])
        string_series = pd.Series(['apple', 'banana', 'cherry'])
        
        assert NumericNormalizer.is_numeric_column(numeric_series) is True
        assert NumericNormalizer.is_numeric_column(string_series) is False
    
    def test_clean_for_math(self):
        """Test cleaning numeric values for math operations."""
        # clean_for_math works on a Series
        series = pd.Series(['$1,234.56'])
        cleaned = NumericNormalizer.clean_for_math(series)
        
        assert cleaned[0] == 1234.56
        assert isinstance(cleaned[0], float)
    
    def test_handle_negative_numbers(self):
        """Test handling negative numbers."""
        series = pd.Series(['-$123.45', '($456.78)', '-789'])
        normalized, stats = NumericNormalizer.normalize(series)
        
        assert normalized[0] == -123.45
        assert normalized[2] == -789
    
    def test_handle_invalid_numbers(self):
        """Test handling invalid numeric values."""
        series = pd.Series(['$123', 'not a number', '456', None])
        normalized, stats = NumericNormalizer.normalize(series)
        
        assert stats['successful_conversions'] == 2
        assert stats['failed_conversions'] >= 1
        assert pd.isna(normalized[1])


class TestNormalizationReport:
    """Test normalization reporting functionality."""
    
    def test_create_report(self):
        """Test creating a normalization report."""
        report = NormalizationReport(preset_used='basic')
        report.rows_processed = 100
        report.columns_processed = 5
        
        assert report.preset_used == 'basic'
        assert report.rows_processed == 100
        assert report.columns_processed == 5
    
    def test_add_transformation(self):
        """Test adding transformations to report."""
        report = NormalizationReport()
        report.add_transformation(
            name='string_normalization',
            description='Trimmed and lowercased strings',
            values_changed=150
        )
        
        assert len(report.transformations) == 1
        assert report.transformations[0].name == 'string_normalization'
        assert report.stats['string_normalization'] == 150
    
    def test_add_column_change(self):
        """Test adding column changes to report."""
        report = NormalizationReport()
        report.add_column_change(
            column='price',
            changes={'type': 'numeric', 'currency_removed': 10}
        )
        
        assert 'price' in report.column_changes
        assert report.column_changes['price']['changes']['type'] == 'numeric'
    
    def test_summary(self):
        """Test generating report summary."""
        report = NormalizationReport(preset_used='basic')
        report.rows_processed = 100
        report.columns_processed = 5
        report.add_transformation('test', 'Test transformation', 50)
        
        summary = report.summary()
        
        assert 'basic' in summary
        assert '100' in summary
        assert '5' in summary
        assert '50' in summary
    
    def test_to_json(self, tmp_path):
        """Test JSON export."""
        report = NormalizationReport()
        report.add_transformation('test', 'Test', 10)
        
        json_path = tmp_path / 'report.json'
        report.to_json(str(json_path))
        
        # Verify file was created and contains data
        assert json_path.exists()
        with open(json_path) as f:
            data = json.load(f)
            assert 'transformations' in data
            assert len(data['transformations']) == 1
    
    def test_to_markdown(self, tmp_path):
        """Test markdown export."""
        report = NormalizationReport()
        report.add_transformation('test', 'Test', 10)
        
        md_path = tmp_path / 'report.md'
        report.to_markdown(str(md_path))
        
        # Verify file was created and contains data
        assert md_path.exists()
        content = md_path.read_text()
        assert '# Normalization Report' in content
        assert 'test' in content.lower()


class TestIntegratedNormalization:
    """Test integrated normalization with dates, numbers, and reporting."""
    
    def test_normalize_with_dates_and_report(self, tmp_path):
        """Test normalizing dates with report generation."""
        # Create test CSV
        csv_path = tmp_path / "dates.csv"
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'event_date': ['01/12/2024', '15/12/2024', '31/12/2024']
        })
        df.to_csv(csv_path, index=False)
        
        # Read and normalize with config
        reader = CSVReader()
        df = reader.read(str(csv_path))
        
        config = NormalizationConfig.from_preset('full')
        config.dates['normalize'] = True
        config.dates['format'] = '%Y-%m-%d'
        
        normalized, report = reader.normalize(df, config=config, return_report=True)
        
        # Verify dates were normalized
        assert 'date_normalization' in report.stats or len(report.column_changes) > 0
        
        # Verify report
        assert report.rows_processed == 3
        assert report.columns_processed == 2
    
    def test_normalize_with_numbers_and_report(self, tmp_path):
        """Test normalizing numbers with report generation."""
        # Create test CSV
        csv_path = tmp_path / "numbers.csv"
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'price': ['$1,234.56', '$500.00', '$2,000.00'],
            'discount': ['10%', '25%', '5%']
        })
        df.to_csv(csv_path, index=False)
        
        # Read and normalize with config
        reader = CSVReader()
        df = reader.read(str(csv_path))
        
        config = NormalizationConfig.from_preset('full')
        config.numbers['normalize'] = True
        
        normalized, report = reader.normalize(df, config=config, return_report=True)
        
        # Verify numbers were normalized
        assert 'numeric_normalization' in report.stats or len(report.column_changes) > 0
        
        # Verify report
        assert report.rows_processed == 3
    
    def test_normalize_verbose_mode(self, tmp_path, capsys):
        """Test verbose mode output."""
        # Create test CSV
        csv_path = tmp_path / "test.csv"
        df = pd.DataFrame({
            'name': ['  JOHN  ', '  JANE  '],
            'price': ['$100', '$200']
        })
        df.to_csv(csv_path, index=False)
        
        # Read and normalize with verbose
        reader = CSVReader()
        df = reader.read(str(csv_path))
        
        normalized = reader.normalize(df, preset='basic', verbose=True)
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify verbose output
        assert '[NORMALIZE]' in captured.out
        assert 'Starting normalization' in captured.out
    
    def test_normalize_full_workflow(self, tmp_path):
        """Test complete normalization workflow with all features."""
        # Create comprehensive test CSV
        csv_path = tmp_path / "full.csv"
        df = pd.DataFrame({
            'id': [1, 2, 3, 4],
            'name': ['  JOHN  ', '  JANE  ', 'BOB', '  '],
            'event_date': ['01/12/2024', '2024-12-15', '31/12/2024', None],
            'price': ['$1,234.56', '€500.00', '$750', 'N/A'],
            'discount': ['10%', '25%', '5%', '0%']
        })
        df.to_csv(csv_path, index=False)
        
        # Read and normalize with full preset
        reader = CSVReader()
        df = reader.read(str(csv_path))
        
        normalized, report = reader.normalize(
            df,
            preset='full',
            verbose=False,
            return_report=True
        )
        
        # Verify comprehensive normalization
        assert report.rows_processed == 4
        assert report.columns_processed == 5
        assert len(report.transformations) > 0
        
        # Verify report can be exported
        summary = report.summary()
        assert len(summary) > 0
        
        json_path = tmp_path / 'report.json'
        report.to_json(str(json_path))
        assert json_path.exists()
        
        md_path = tmp_path / 'report.md'
        report.to_markdown(str(md_path))
        assert md_path.exists()


class TestConfig:
    """Test configuration presets with dates and numbers."""
    
    def test_full_preset_has_dates_and_numbers(self):
        """Test that 'full' preset includes date and number normalization."""
        config = NormalizationConfig.from_preset('full')
        
        assert config.dates['normalize'] is True
        assert config.numbers['normalize'] is True
        assert 'format' in config.dates
        assert 'remove_currency' in config.numbers
    
    def test_analysis_ready_preset(self):
        """Test 'analysis_ready' preset configuration."""
        config = NormalizationConfig.from_preset('analysis_ready')
        
        assert config.dates['normalize'] is True
        assert config.numbers['normalize'] is True
        assert config.columns['drop_original'] is True  # Replaces columns
    
    def test_config_date_format_options(self):
        """Test that date formats are configurable."""
        config = NormalizationConfig.from_preset('full')
        
        # Default format
        assert config.dates['format'] == '%Y-%m-%d'
        
        # Custom format
        config.dates['format'] = '%d/%m/%Y'
        assert config.dates['format'] == '%d/%m/%Y'
    
    def test_config_number_options(self):
        """Test that number options are configurable."""
        config = NormalizationConfig.from_preset('full')
        
        assert config.numbers['remove_currency'] is True
        assert config.numbers['handle_percentages'] is True
        assert 'decimal_separator' in config.numbers
        assert 'thousand_separator' in config.numbers


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
