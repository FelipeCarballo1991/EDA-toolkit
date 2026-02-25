"""
Null value normalization.

Provides specialized functionality for standardizing null/missing values
across different representations.
"""

import pandas as pd
import numpy as np
from typing import List, Union


class NullNormalizer:
    """
    Specialized normalizer for null/missing values.
    
    Handles standardization of various null representations:
    - Empty strings: ''
    - Text representations: 'N/A', 'null', 'None', 'nan', '-', '--'
    - Actual NaN values
    - Custom null values
    """
    
    # Default null value representations
    DEFAULT_NULL_VALUES = [
        '',
        'N/A', 'n/a', 'NA', 'na',
        'null', 'NULL', 'Null',
        'None', 'NONE',
        'nan', 'NaN', 'NAN',
        '-', '--', '---',
        'nil', 'NIL', 'Nil',
        '#N/A', '#NA', '#NULL!',
        'missing', 'MISSING', 'Missing'
    ]
    
    @staticmethod
    def normalize(
        df: pd.DataFrame,
        null_values: Union[List[str], None] = None,
        include_defaults: bool = True
    ) -> pd.DataFrame:
        """
        Standardize null values in a DataFrame.
        
        Converts various representations of null/missing values to proper
        pandas NaN (np.nan).
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with potentially varied null representations.
        null_values : list of str, optional
            Additional values to treat as null. If None, uses default list.
        include_defaults : bool, default True
            Whether to include default null values in addition to custom ones.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with standardized null values (all as np.nan).
        
        Examples
        --------
        >>> df = pd.DataFrame({
        ...     'A': ['value', '', 'N/A', 'null'],
        ...     'B': [1, 2, 3, 4]
        ... })
        >>> normalized = NullNormalizer.normalize(df)
        >>> print(normalized['A'].isna().sum())
        3
        """
        df = df.copy()
        
        # Build list of null values to replace
        values_to_replace = []
        
        if include_defaults:
            values_to_replace.extend(NullNormalizer.DEFAULT_NULL_VALUES)
        
        if null_values is not None:
            values_to_replace.extend(null_values)
        
        # Remove duplicates while preserving order
        values_to_replace = list(dict.fromkeys(values_to_replace))
        
        # Replace all null representations with np.nan
        if values_to_replace:
            df = df.replace(values_to_replace, np.nan)
        
        return df
    
    @staticmethod
    def normalize_series(
        series: pd.Series,
        null_values: Union[List[str], None] = None,
        include_defaults: bool = True
    ) -> pd.Series:
        """
        Standardize null values in a pandas Series.
        
        Parameters
        ----------
        series : pd.Series
            Series with potentially varied null representations.
        null_values : list of str, optional
            Additional values to treat as null.
        include_defaults : bool, default True
            Whether to include default null values.
        
        Returns
        -------
        pd.Series
            Series with standardized null values.
        
        Examples
        --------
        >>> s = pd.Series(['value', '', 'N/A', 'null'])
        >>> normalized = NullNormalizer.normalize_series(s)
        >>> print(normalized.isna().sum())
        3
        """
        result = series.copy()
        
        # Build list of null values to replace
        values_to_replace = []
        
        if include_defaults:
            values_to_replace.extend(NullNormalizer.DEFAULT_NULL_VALUES)
        
        if null_values is not None:
            values_to_replace.extend(null_values)
        
        # Remove duplicates
        values_to_replace = list(dict.fromkeys(values_to_replace))
        
        # Replace all null representations with np.nan
        if values_to_replace:
            result = result.replace(values_to_replace, np.nan)
        
        return result
    
    @staticmethod
    def get_null_summary(df: pd.DataFrame) -> pd.DataFrame:
        """
        Get summary of null values in DataFrame.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to analyze.
        
        Returns
        -------
        pd.DataFrame
            Summary with columns: column, null_count, null_percentage.
        
        Examples
        --------
        >>> df = pd.DataFrame({
        ...     'A': [1, np.nan, 3],
        ...     'B': ['x', 'y', np.nan]
        ... })
        >>> summary = NullNormalizer.get_null_summary(df)
        >>> print(summary)
          column  null_count  null_percentage
        0      A           1        33.333333
        1      B           1        33.333333
        """
        null_counts = df.isna().sum()
        total_rows = len(df)
        
        summary = pd.DataFrame({
            'column': null_counts.index,
            'null_count': null_counts.values,
            'null_percentage': (null_counts.values / total_rows * 100) if total_rows > 0 else 0
        })
        
        # Only show columns with nulls
        summary = summary[summary['null_count'] > 0]
        
        return summary.reset_index(drop=True)
