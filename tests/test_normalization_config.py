"""
Tests for NormalizationConfig.

Tests the configuration system for data normalization including presets
and custom configurations.
"""

import pytest
from pandas_toolkit.io.base.normalizers import NormalizationConfig


class TestNormalizationConfig:
    """Test suite for NormalizationConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = NormalizationConfig()
        
        assert config.strings['trim'] is True
        assert config.strings['case'] == 'lower'
        assert config.nulls['standardize'] is True
        assert config.columns['drop_original'] is False
        assert config.columns['suffix'] == '_norm'
    
    def test_preset_basic(self):
        """Test basic preset configuration."""
        config = NormalizationConfig.from_preset('basic')
        
        assert config.preset == 'basic'
        assert config.strings['trim'] is True
        assert config.strings['case'] == 'lower'
        assert 'N/A' in config.nulls['values']
        assert config.columns['drop_original'] is False
    
    def test_preset_full(self):
        """Test full preset configuration."""
        config = NormalizationConfig.from_preset('full')
        
        assert config.preset == 'full'
        assert config.strings['remove_special'] is True
        assert config.dates['normalize'] is True
        assert config.numbers['normalize'] is True
        assert config.booleans['normalize'] is True
        assert config.types['auto_detect'] is True
    
    def test_preset_minimal(self):
        """Test minimal preset configuration."""
        config = NormalizationConfig.from_preset('minimal')
        
        assert config.preset == 'minimal'
        assert config.strings['case'] is None
        assert config.dates['normalize'] is False
        assert config.numbers['normalize'] is False
    
    def test_preset_analysis_ready(self):
        """Test analysis_ready preset configuration."""
        config = NormalizationConfig.from_preset('analysis_ready')
        
        assert config.preset == 'analysis_ready'
        assert config.columns['drop_original'] is True
        assert config.dates['normalize'] is True
        assert config.numbers['normalize'] is True
    
    def test_invalid_preset(self):
        """Test that invalid preset raises ValueError."""
        with pytest.raises(ValueError, match="Unknown preset"):
            NormalizationConfig.from_preset('invalid_preset')
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            'strings': {'trim': False, 'case': 'upper'},
            'nulls': {'standardize': False},
            'columns': {'drop_original': True}
        }
        
        config = NormalizationConfig.from_dict(config_dict)
        
        assert config.strings['trim'] is False
        assert config.strings['case'] == 'upper'
        assert config.nulls['standardize'] is False
        assert config.columns['drop_original'] is True
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = NormalizationConfig.from_preset('basic')
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'strings' in config_dict
        assert 'nulls' in config_dict
        assert 'columns' in config_dict
        assert config_dict['preset'] == 'basic'
    
    def test_merge(self):
        """Test merging configurations."""
        config = NormalizationConfig.from_preset('basic')
        
        custom = {
            'strings': {'case': 'upper'},
            'columns': {'drop_original': True}
        }
        
        merged = config.merge(custom)
        
        # Should keep other basic settings
        assert merged.strings['trim'] is True
        # Should update merged settings
        assert merged.strings['case'] == 'upper'
        assert merged.columns['drop_original'] is True
    
    def test_custom_config(self):
        """Test creating completely custom configuration."""
        config = NormalizationConfig(
            strings={'trim': False, 'case': None, 'remove_special': True},
            nulls={'standardize': False, 'values': []},
            columns={'drop_original': True, 'suffix': '_clean'}
        )
        
        assert config.strings['trim'] is False
        assert config.strings['case'] is None
        assert config.strings['remove_special'] is True
        assert config.nulls['standardize'] is False
        assert config.columns['drop_original'] is True
        assert config.columns['suffix'] == '_clean'
