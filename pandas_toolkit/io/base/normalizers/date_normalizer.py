"""
Date normalization.

Provides specialized functionality for parsing, detecting, and standardizing
dates in various formats.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import re


class DateNormalizer:
    """
    Specialized normalizer for date values.
    
    Handles:
    - Auto-detection of date formats
    - Parsing multiple date formats
    - Standardization to a single format
    - Handling invalid dates
    """
    
    # Common date formats to try (in order of preference)
    COMMON_FORMATS = [
        '%d/%m/%Y',      # 25/12/2023
        '%d-%m-%Y',      # 25-12-2023
        '%Y-%m-%d',      # 2023-12-25 (ISO)
        '%m/%d/%Y',      # 12/25/2023 (US)
        '%m-%d-%Y',      # 12-25-2023 (US)
        '%d/%m/%y',      # 25/12/23
        '%d-%m-%y',      # 25-12-23
        '%Y/%m/%d',      # 2023/12/25
        '%d.%m.%Y',      # 25.12.2023
        '%d %b %Y',      # 25 Dec 2023
        '%d %B %Y',      # 25 December 2023
        '%b %d, %Y',     # Dec 25, 2023
        '%B %d, %Y',     # December 25, 2023
        '%Y%m%d',        # 20231225
    ]
    
    # Format descriptions for user reference
    FORMAT_DESCRIPTIONS = {
        '%d/%m/%Y': 'DD/MM/YYYY (e.g., 25/12/2023)',
        '%d-%m-%Y': 'DD-MM-YYYY (e.g., 25-12-2023)',
        '%Y-%m-%d': 'YYYY-MM-DD (e.g., 2023-12-25) [ISO]',
        '%m/%d/%Y': 'MM/DD/YYYY (e.g., 12/25/2023) [US]',
        '%m-%d-%Y': 'MM-DD-YYYY (e.g., 12-25-2023) [US]',
        '%d/%m/%y': 'DD/MM/YY (e.g., 25/12/23)',
        '%d-%m-%y': 'DD-MM-YY (e.g., 25-12-23)',
        '%Y/%m/%d': 'YYYY/MM/DD (e.g., 2023/12/25)',
        '%d.%m.%Y': 'DD.MM.YYYY (e.g., 25.12.2023)',
        '%d %b %Y': 'DD Mon YYYY (e.g., 25 Dec 2023)',
        '%d %B %Y': 'DD Month YYYY (e.g., 25 December 2023)',
        '%b %d, %Y': 'Mon DD, YYYY (e.g., Dec 25, 2023)',
        '%B %d, %Y': 'Month DD, YYYY (e.g., December 25, 2023)',
        '%Y%m%d': 'YYYYMMDD (e.g., 20231225)',
    }
    
    @staticmethod
    def get_available_formats() -> Dict[str, str]:
        """
        Get available date formats with descriptions.
        
        Returns
        -------
        dict
            Dictionary mapping format codes to descriptions.
        
        Examples
        --------
        >>> formats = DateNormalizer.get_available_formats()
        >>> for fmt, desc in formats.items():
        ...     print(f"{fmt}: {desc}")
        """
        return DateNormalizer.FORMAT_DESCRIPTIONS.copy()
    
    @staticmethod
    def detect_date_format(series: pd.Series, sample_size: int = 100) -> Optional[str]:
        """
        Detect the most likely date format in a series.
        
        Parameters
        ----------
        series : pd.Series
            Series containing date strings.
        sample_size : int, default 100
            Number of samples to test.
        
        Returns
        -------
        str or None
            Detected format string, or None if no format matches.
        
        Examples
        --------
        >>> s = pd.Series(['25/12/2023', '26/12/2023', '27/12/2023'])
        >>> fmt = DateNormalizer.detect_date_format(s)
        >>> print(fmt)
        '%d/%m/%Y'
        """
        # Get non-null sample
        sample = series.dropna().astype(str).head(sample_size)
        
        if len(sample) == 0:
            return None
        
        # Try each format
        format_scores = {}
        
        for fmt in DateNormalizer.COMMON_FORMATS:
            successful_parses = 0
            
            for value in sample:
                try:
                    datetime.strptime(value.strip(), fmt)
                    successful_parses += 1
                except (ValueError, AttributeError):
                    continue
            
            if successful_parses > 0:
                format_scores[fmt] = successful_parses / len(sample)
        
        if not format_scores:
            return None
        
        # Return format with highest success rate
        best_format = max(format_scores.items(), key=lambda x: x[1])
        
        # Only return if at least 80% of samples match
        if best_format[1] >= 0.8:
            return best_format[0]
        
        return None
    
    @staticmethod
    def detect_all_formats(series: pd.Series) -> Dict[str, int]:
        """
        Detect all date formats present in a series.
        
        Parameters
        ----------
        series : pd.Series
            Series containing date strings.
        
        Returns
        -------
        dict
            Dictionary mapping format strings to occurrence counts.
        
        Examples
        --------
        >>> s = pd.Series(['25/12/2023', '2023-12-26', '27/12/2023'])
        >>> formats = DateNormalizer.detect_all_formats(s)
        >>> print(formats)
        {'%d/%m/%Y': 2, '%Y-%m-%d': 1}
        """
        format_counts = {}
        sample = series.dropna().astype(str)
        
        for value in sample:
            value_str = value.strip()
            matched = False
            
            for fmt in DateNormalizer.COMMON_FORMATS:
                try:
                    datetime.strptime(value_str, fmt)
                    format_counts[fmt] = format_counts.get(fmt, 0) + 1
                    matched = True
                    break  # Use first matching format
                except (ValueError, AttributeError):
                    continue
            
            if not matched:
                format_counts['unknown'] = format_counts.get('unknown', 0) + 1
        
        return format_counts
    
    @staticmethod
    def normalize(
        series: pd.Series,
        output_format: str = '%d/%m/%Y',
        input_formats: Optional[List[str]] = None,
        infer_format: bool = True,
        dayfirst: bool = True
    ) -> Tuple[pd.Series, Dict[str, any]]:
        """
        Normalize date values to a standard format.
        
        Parameters
        ----------
        series : pd.Series
            Series with date values (strings or datetime objects).
        output_format : str, default '%d/%m/%Y'
            Target date format for output.
        input_formats : list of str, optional
            Specific formats to try (if None, tries common formats).
        infer_format : bool, default True
            Whether to automatically detect formats.
        dayfirst : bool, default True
            Interpret day first in ambiguous dates (25/12/2023 vs 12/25/2023).
        
        Returns
        -------
        tuple of (pd.Series, dict)
            Normalized series and statistics dictionary with:
            - 'formats_detected': dict of format counts
            - 'successful_parses': int
            - 'failed_parses': int
            - 'null_values': int
        
        Examples
        --------
        >>> s = pd.Series(['25/12/2023', '26-12-2023', 'invalid'])
        >>> normalized, stats = DateNormalizer.normalize(s)
        >>> print(normalized.tolist())
        ['25/12/2023', '26/12/2023', NaN]
        >>> print(stats['successful_parses'])
        2
        """
        stats = {
            'formats_detected': {},
            'successful_parses': 0,
            'failed_parses': 0,
            'null_values': series.isna().sum()
        }
        
        # Work with copy
        result = series.copy()
        
        # Convert to string for processing
        result = result.astype(str)
        
        # Track formats if inferring
        if infer_format:
            stats['formats_detected'] = DateNormalizer.detect_all_formats(series)
        
        # Determine which formats to try
        formats_to_try = input_formats or DateNormalizer.COMMON_FORMATS
        
        # Parse dates
        parsed_dates = []
        
        for value in result:
            if pd.isna(value) or value == 'nan' or value.strip() == '':
                parsed_dates.append(None)
                continue
            
            value_str = value.strip()
            parsed = None
            
            # Try each format
            for fmt in formats_to_try:
                try:
                    parsed = datetime.strptime(value_str, fmt)
                    stats['successful_parses'] += 1
                    break
                except (ValueError, AttributeError):
                    continue
            
            # If no format worked, try pandas parser as fallback
            if parsed is None:
                try:
                    parsed = pd.to_datetime(value_str, dayfirst=dayfirst)
                    stats['successful_parses'] += 1
                except:
                    stats['failed_parses'] += 1
            
            parsed_dates.append(parsed)
        
        # Convert to series
        result = pd.Series(parsed_dates, index=series.index)
        
        # Format output
        result = result.apply(
            lambda x: x.strftime(output_format) if pd.notna(x) and isinstance(x, datetime) else None
        )
        
        return result, stats
    
    @staticmethod
    def is_date_column(series: pd.Series, threshold: float = 0.7) -> bool:
        """
        Check if a series likely contains dates.
        
        Parameters
        ----------
        series : pd.Series
            Series to check.
        threshold : float, default 0.7
            Minimum proportion of values that must parse as dates.
        
        Returns
        -------
        bool
            True if series appears to contain dates.
        
        Examples
        --------
        >>> s = pd.Series(['25/12/2023', '26/12/2023', 'text'])
        >>> DateNormalizer.is_date_column(s, threshold=0.6)
        True
        """
        if len(series) == 0:
            return False
        
        # Try to detect a format
        detected_format = DateNormalizer.detect_date_format(series)
        
        if detected_format is None:
            return False
        
        # Count successful parses
        sample = series.dropna().astype(str).head(100)
        successful = 0
        
        for value in sample:
            try:
                datetime.strptime(value.strip(), detected_format)
                successful += 1
            except:
                continue
        
        return (successful / len(sample)) >= threshold if len(sample) > 0 else False
    
    @staticmethod
    def to_datetime(
        series: pd.Series,
        input_formats: Optional[List[str]] = None,
        dayfirst: bool = True
    ) -> pd.Series:
        """
        Convert series to pandas datetime objects.
        
        Parameters
        ----------
        series : pd.Series
            Series with date strings.
        input_formats : list of str, optional
            Specific formats to try.
        dayfirst : bool, default True
            Interpret day first in ambiguous dates.
        
        Returns
        -------
        pd.Series
            Series with datetime objects.
        """
        formats_to_try = input_formats or DateNormalizer.COMMON_FORMATS
        
        result = series.copy().astype(str)
        parsed_dates = []
        
        for value in result:
            if pd.isna(value) or value == 'nan' or value.strip() == '':
                parsed_dates.append(pd.NaT)
                continue
            
            value_str = value.strip()
            parsed = None
            
            for fmt in formats_to_try:
                try:
                    parsed = datetime.strptime(value_str, fmt)
                    break
                except (ValueError, AttributeError):
                    continue
            
            if parsed is None:
                try:
                    parsed = pd.to_datetime(value_str, dayfirst=dayfirst)
                except:
                    parsed = pd.NaT
            
            parsed_dates.append(parsed)
        
        return pd.Series(parsed_dates, index=series.index)
