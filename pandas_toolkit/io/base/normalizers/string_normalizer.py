"""
String value normalization.

Provides specialized functionality for cleaning and standardizing string
values in DataFrames.
"""

import pandas as pd
from typing import Optional


class StringNormalizer:
    """
    Specialized normalizer for string values.
    
    Handles:
    - Trimming whitespace
    - Case conversion
    - Special character removal
    - Empty string handling
    """
    
    @staticmethod
    def normalize(
        series: pd.Series,
        trim: bool = True,
        convert_case: Optional[str] = "lower",
        remove_special_chars: bool = False
    ) -> pd.Series:
        """
        Normalize string values in a pandas Series.
        
        Parameters
        ----------
        series : pd.Series
            Series with string values to normalize.
        trim : bool, default True
            Strip leading/trailing whitespace.
        convert_case : {'lower', 'upper', None}, default 'lower'
            Case conversion for string values.
        remove_special_chars : bool, default False
            Whether to remove special characters (keeps only alphanumeric and spaces).
        
        Returns
        -------
        pd.Series
            Series with normalized string values.
        
        Examples
        --------
        >>> s = pd.Series(["  JUAN  ", "  MARIA  ", "  "])
        >>> normalized = StringNormalizer.normalize(s, trim=True, convert_case="lower")
        >>> print(normalized.tolist())
        ['juan', 'maria', None]
        """
        # Work with a copy
        result = series.copy()
        
        # Only process string columns
        if not pd.api.types.is_string_dtype(result):
            # Try to convert to string if possible
            result = result.astype(str)
        
        # Trim strings
        if trim:
            result = result.str.strip()
        
        # Remove special characters if requested
        if remove_special_chars:
            # Keep only alphanumeric characters and spaces
            result = result.str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
            # Clean up multiple spaces
            result = result.str.replace(r'\s+', ' ', regex=True)
            result = result.str.strip()
        
        # Convert empty strings to None
        result = result.replace('', None)
        result = result.replace('nan', None)
        
        # Convert case
        if convert_case == "lower":
            result = result.str.lower()
        elif convert_case == "upper":
            result = result.str.upper()
        
        return result
    
    @staticmethod
    def is_string_column(series: pd.Series) -> bool:
        """
        Check if a series contains primarily string values.
        
        Parameters
        ----------
        series : pd.Series
            Series to check.
        
        Returns
        -------
        bool
            True if series is string-based, False otherwise.
        """
        return pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series)
