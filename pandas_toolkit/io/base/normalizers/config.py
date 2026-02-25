"""
Configuration system for data normalization.

Provides centralized configuration with preset support for consistent
normalization across the toolkit.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


# Define presets as a module-level constant
_PRESETS: Dict[str, Dict[str, Any]] = {
        'minimal': {
            'strings': {'trim': True, 'case': None, 'remove_special': False},
            'nulls': {'standardize': True, 'values': ['', 'nan']},
            'dates': {'normalize': False},
            'numbers': {'normalize': False},
            'booleans': {'normalize': False},
            'types': {'auto_detect': False},
            'categories': {'standardize': False},
            'columns': {'drop_original': False, 'suffix': '_norm', 'drop_empty': False}
        },
        'basic': {
            'strings': {'trim': True, 'case': 'lower', 'remove_special': False},
            'nulls': {'standardize': True, 'values': ['', 'N/A', 'null', 'None', 'nan', '-', '--']},
            'dates': {'normalize': False},
            'numbers': {'normalize': False},
            'booleans': {'normalize': False},
            'types': {'auto_detect': False},
            'categories': {'standardize': False},
            'columns': {'drop_original': False, 'suffix': '_norm', 'drop_empty': False}
        },
        'full': {
            'strings': {'trim': True, 'case': 'lower', 'remove_special': True},
            'nulls': {
                'standardize': True,
                'values': ['', 'N/A', 'n/a', 'NA', 'null', 'NULL', 'None', 'NONE',
                          'nan', 'NaN', 'NAN', '-', '--', '---', 'nil', 'NIL']
            },
            'dates': {'normalize': True, 'format': '%Y-%m-%d', 'infer': True},
            'numbers': {
                'normalize': True,
                'remove_currency': True,
                'decimal_separator': '.',
                'thousand_separator': ',',
                'handle_percentages': True
            },
            'booleans': {
                'normalize': True,
                'true_values': ['yes', 'y', 'si', 'sí', '1', 'true', 't', 'verdadero'],
                'false_values': ['no', 'n', '0', 'false', 'f', 'falso']
            },
            'types': {'auto_detect': True},
            'categories': {
                'standardize': True,
                'fuzzy_threshold': 0.85,
                'mappings': {}
            },
            'columns': {'drop_original': False, 'suffix': '_norm', 'drop_empty': True}
        },
        'analysis_ready': {
            'strings': {'trim': True, 'case': 'lower', 'remove_special': False},
            'nulls': {
                'standardize': True,
                'values': ['', 'N/A', 'null', 'None', 'nan', '-', '--']
            },
            'dates': {'normalize': True, 'format': '%Y-%m-%d', 'infer': True},
            'numbers': {
                'normalize': True,
                'remove_currency': True,
                'decimal_separator': '.',
                'thousand_separator': ',',
                'handle_percentages': True
            },
            'booleans': {'normalize': True},
            'types': {'auto_detect': True},
            'categories': {'standardize': False},
            'columns': {'drop_original': True, 'suffix': '_norm', 'drop_empty': True}
        }
    }


@dataclass
class NormalizationConfig:
    """
    Configuration for data normalization operations.
    
    This class provides a centralized way to configure all normalization
    operations. It supports presets for common use cases and allows
    fine-grained control over each normalization aspect.
    
    Attributes
    ----------
    preset : str, optional
        Name of preset configuration ('basic', 'full', 'minimal', None).
    strings : dict
        Configuration for string normalization.
    nulls : dict
        Configuration for null value standardization.
    dates : dict
        Configuration for date normalization.
    numbers : dict
        Configuration for numeric normalization.
    booleans : dict
        Configuration for boolean normalization.
    types : dict
        Configuration for type detection and conversion.
    categories : dict
        Configuration for category standardization.
    columns : dict
        Configuration for column handling.
    
    Examples
    --------
    >>> # Use a preset
    >>> config = NormalizationConfig.from_preset('basic')
    
    >>> # Custom configuration
    >>> config = NormalizationConfig(
    ...     strings={'trim': True, 'case': 'lower'},
    ...     nulls={'standardize': True, 'values': ['', 'N/A', 'null']},
    ...     columns={'drop_original': False, 'suffix': '_norm'}
    ... )
    
    >>> # Modify preset
    >>> config = NormalizationConfig.from_preset('basic')
    >>> config.strings['case'] = 'upper'
    """
    
    preset: Optional[str] = None
    strings: Dict[str, Any] = field(default_factory=lambda: {
        'trim': True,
        'case': 'lower',
        'remove_special': False
    })
    nulls: Dict[str, Any] = field(default_factory=lambda: {
        'standardize': True,
        'values': ['', 'N/A', 'null', 'None', 'nan', '-', '--']
    })
    dates: Dict[str, Any] = field(default_factory=lambda: {
        'normalize': False,
        'format': '%Y-%m-%d',
        'infer': True
    })
    numbers: Dict[str, Any] = field(default_factory=lambda: {
        'normalize': False,
        'remove_currency': True,
        'decimal_separator': '.',
        'thousand_separator': ',',
        'handle_percentages': True
    })
    booleans: Dict[str, Any] = field(default_factory=lambda: {
        'normalize': False,
        'true_values': ['yes', 'y', 'si', 'sí', '1', 'true', 't'],
        'false_values': ['no', 'n', '0', 'false', 'f']
    })
    types: Dict[str, Any] = field(default_factory=lambda: {
        'auto_detect': False
    })
    categories: Dict[str, Any] = field(default_factory=lambda: {
        'standardize': False,
        'fuzzy_threshold': 0.85,
        'mappings': {}
    })
    columns: Dict[str, Any] = field(default_factory=lambda: {
        'drop_original': False,
        'suffix': '_norm',
        'drop_empty': False
    })
    
    @classmethod
    def from_preset(cls, preset: str) -> 'NormalizationConfig':
        """
        Create a NormalizationConfig from a preset.
        
        Parameters
        ----------
        preset : {'minimal', 'basic', 'full', 'analysis_ready'}
            Name of the preset to use.
        
        Returns
        -------
        NormalizationConfig
            Configuration object with preset values.
        
        Raises
        ------
        ValueError
            If preset name is not recognized.
        
        Examples
        --------
        >>> config = NormalizationConfig.from_preset('basic')
        >>> print(config.strings['case'])
        'lower'
        """
        if preset not in _PRESETS:
            available = ', '.join(_PRESETS.keys())
            raise ValueError(
                f"Unknown preset '{preset}'. Available presets: {available}"
            )
        
        preset_config = _PRESETS[preset]
        return cls(
            preset=preset,
            strings=preset_config['strings'].copy(),
            nulls=preset_config['nulls'].copy(),
            dates=preset_config['dates'].copy(),
            numbers=preset_config['numbers'].copy(),
            booleans=preset_config['booleans'].copy(),
            types=preset_config['types'].copy(),
            categories=preset_config['categories'].copy(),
            columns=preset_config['columns'].copy()
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'NormalizationConfig':
        """
        Create a NormalizationConfig from a dictionary.
        
        Parameters
        ----------
        config_dict : dict
            Dictionary with configuration values.
        
        Returns
        -------
        NormalizationConfig
            Configuration object.
        
        Examples
        --------
        >>> config_dict = {
        ...     'strings': {'trim': True, 'case': 'upper'},
        ...     'nulls': {'standardize': False}
        ... }
        >>> config = NormalizationConfig.from_dict(config_dict)
        """
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns
        -------
        dict
            Dictionary representation of configuration.
        """
        return {
            'preset': self.preset,
            'strings': self.strings,
            'nulls': self.nulls,
            'dates': self.dates,
            'numbers': self.numbers,
            'booleans': self.booleans,
            'types': self.types,
            'categories': self.categories,
            'columns': self.columns
        }
    
    def merge(self, other: Dict[str, Any]) -> 'NormalizationConfig':
        """
        Merge another configuration dict into this one.
        
        Parameters
        ----------
        other : dict
            Configuration dictionary to merge.
        
        Returns
        -------
        NormalizationConfig
            New configuration with merged values.
        
        Examples
        --------
        >>> config = NormalizationConfig.from_preset('basic')
        >>> custom = {'strings': {'case': 'upper'}}
        >>> new_config = config.merge(custom)
        """
        current = self.to_dict()
        
        for key, value in other.items():
            if key in current and isinstance(current[key], dict) and isinstance(value, dict):
                current[key].update(value)
            else:
                current[key] = value
        
        return NormalizationConfig.from_dict(current)
