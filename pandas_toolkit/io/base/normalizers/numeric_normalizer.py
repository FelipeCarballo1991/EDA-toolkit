"""
Numeric value normalization.

Provides specialized functionality for cleaning and standardizing numeric
values for mathematical operations.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Optional
import re


class NumericNormalizer:
    """
    Specialized normalizer for numeric values.
    
    Handles:
    - Removing currency symbols ($, €, £, etc.)
    - Removing thousand separators (,)
    - Standardizing decimal separators (.,)
    - Converting percentages
    - Handling negative numbers
    - Scientific notation
    - Cleaning for mathematical operations
    """
    
    # Common currency symbols
    CURRENCY_SYMBOLS = ['$', '€', '£', '¥', '₹', 'R$', 'USD', 'EUR', 'GBP', 'JPY', 'INR', 'BRL']
    
    # Common separators
    THOUSAND_SEPARATORS = [',', '.', ' ', "'"]
    
    @staticmethod
    def normalize(
        series: pd.Series,
        remove_currency: bool = True,
        decimal_separator: str = '.',
        thousand_separator: str = ',',
        handle_percentages: bool = True,
        convert_to_float: bool = True
    ) -> Tuple[pd.Series, Dict[str, any]]:
        """
        Normalize numeric values for mathematical operations.
        
        Parameters
        ----------
        series : pd.Series
            Series with numeric values (potentially with formatting).
        remove_currency : bool, default True
            Remove currency symbols.
        decimal_separator : str, default '.'
            Character used for decimals in output.
        thousand_separator : str, default ','
            Character used for thousands in input (will be removed).
        handle_percentages : bool, default True
            Convert percentages to decimals (25% → 0.25) or keep as number (25% → 25).
        convert_to_float : bool, default True
            Convert result to float type.
        
        Returns
        -------
        tuple of (pd.Series, dict)
            Normalized series and statistics dictionary with:
            - 'currency_symbols_removed': int
            - 'separators_removed': int
            - 'percentages_converted': int
            - 'successful_conversions': int
            - 'failed_conversions': int
        
        Examples
        --------
        >>> s = pd.Series(['$1,234.56', '€2.500,00', '25%', '-$100'])
        >>> normalized, stats = NumericNormalizer.normalize(s)
        >>> print(normalized.tolist())
        [1234.56, 2500.0, 0.25, -100.0]
        """
        stats = {
            'currency_symbols_removed': 0,
            'separators_removed': 0,
            'percentages_converted': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'negative_numbers': 0
        }
        
        # Work with copy
        result = series.copy().astype(str)
        
        cleaned_values = []
        
        for value in result:
            if pd.isna(value) or value == 'nan' or value.strip() == '':
                cleaned_values.append(None)
                continue
            
            cleaned = value.strip()
            original = cleaned
            
            # Handle negative numbers with parentheses: (100) → -100
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
                stats['negative_numbers'] += 1
            
            # Remove currency symbols
            if remove_currency:
                for symbol in NumericNormalizer.CURRENCY_SYMBOLS:
                    if symbol in cleaned:
                        cleaned = cleaned.replace(symbol, '')
                        stats['currency_symbols_removed'] += 1
            
            # Handle percentages
            is_percentage = '%' in cleaned
            if is_percentage and handle_percentages:
                cleaned = cleaned.replace('%', '')
                stats['percentages_converted'] += 1
            
            # Remove spaces
            cleaned = cleaned.replace(' ', '')
            
            # Handle European format (1.234,56 → 1234.56)
            # Detect if using comma as decimal
            if ',' in cleaned and '.' in cleaned:
                # Both present - determine which is decimal
                comma_pos = cleaned.rfind(',')
                dot_pos = cleaned.rfind('.')
                
                if comma_pos > dot_pos:
                    # Comma is decimal: 1.234,56
                    cleaned = cleaned.replace('.', '')  # Remove thousand separator
                    cleaned = cleaned.replace(',', '.')  # Make comma the decimal
                    stats['separators_removed'] += 1
                else:
                    # Dot is decimal: 1,234.56
                    cleaned = cleaned.replace(',', '')  # Remove thousand separator
                    stats['separators_removed'] += 1
            elif ',' in cleaned:
                # Only comma - could be decimal or thousand separator
                comma_count = cleaned.count(',')
                if comma_count == 1 and cleaned.rfind(',') > len(cleaned) - 4:
                    # Likely decimal: 1234,56
                    cleaned = cleaned.replace(',', '.')
                else:
                    # Likely thousand separator: 1,234 or 1,234,567
                    cleaned = cleaned.replace(',', '')
                    stats['separators_removed'] += 1
            elif '.' in cleaned:
                # Check if it's a thousand separator (European style: 1.234)
                dot_count = cleaned.count('.')
                if dot_count > 1:
                    # Multiple dots = thousand separators: 1.234.567
                    cleaned = cleaned.replace('.', '')
                    stats['separators_removed'] += 1
                # Single dot = decimal, keep it
            
            # Remove any remaining non-numeric characters except minus and decimal point
            cleaned = re.sub(r'[^\d.\-+eE]', '', cleaned)
            
            # Try to convert to number
            try:
                num_value = float(cleaned) if cleaned else None
                
                if num_value is not None:
                    # Handle percentage conversion
                    if is_percentage and handle_percentages:
                        num_value = num_value / 100
                    
                    stats['successful_conversions'] += 1
                else:
                    stats['failed_conversions'] += 1
                
                cleaned_values.append(num_value)
            except (ValueError, TypeError):
                cleaned_values.append(None)
                stats['failed_conversions'] += 1
        
        # Create result series
        result = pd.Series(cleaned_values, index=series.index)
        
        # Convert to appropriate type
        if convert_to_float:
            result = pd.to_numeric(result, errors='coerce')
        
        return result, stats
    
    @staticmethod
    def is_numeric_column(series: pd.Series, threshold: float = 0.7) -> bool:
        """
        Check if a series likely contains numeric values.
        
        Parameters
        ----------
        series : pd.Series
            Series to check.
        threshold : float, default 0.7
            Minimum proportion of values that must be numeric.
        
        Returns
        -------
        bool
            True if series appears to contain numbers.
        
        Examples
        --------
        >>> s = pd.Series(['$1,234', '$2,500', 'text'])
        >>> NumericNormalizer.is_numeric_column(s, threshold=0.6)
        True
        """
        if len(series) == 0:
            return False
        
        # Try to normalize
        normalized, stats = NumericNormalizer.normalize(series.head(100))
        
        # Check success rate
        total = stats['successful_conversions'] + stats['failed_conversions']
        if total == 0:
            return False
        
        success_rate = stats['successful_conversions'] / total
        return success_rate >= threshold
    
    @staticmethod
    def clean_for_math(
        series: pd.Series,
        preserve_type: bool = False
    ) -> pd.Series:
        """
        Clean numeric values specifically for mathematical operations.
        
        Removes all non-numeric characters and converts to numeric type.
        
        Parameters
        ----------
        series : pd.Series
            Series with numeric values.
        preserve_type : bool, default False
            Try to preserve int vs float (if all are integers).
        
        Returns
        -------
        pd.Series
            Clean numeric series ready for math operations.
        
        Examples
        --------
        >>> s = pd.Series(['$1,234', '€2,500', '$3,750'])
        >>> clean = NumericNormalizer.clean_for_math(s)
        >>> print(clean.sum())
        7484.0
        """
        result, _ = NumericNormalizer.normalize(
            series,
            remove_currency=True,
            handle_percentages=True,
            convert_to_float=True
        )
        
        # Try to preserve integer type if appropriate
        if preserve_type and result.notna().any():
            if (result.dropna() % 1 == 0).all():
                result = result.astype('Int64')  # Nullable integer
        
        return result
    
    @staticmethod
    def extract_numeric(series: pd.Series) -> pd.Series:
        """
        Extract only numeric parts from strings.
        
        Parameters
        ----------
        series : pd.Series
            Series with mixed content.
        
        Returns
        -------
        pd.Series
            Series with extracted numbers.
        
        Examples
        --------
        >>> s = pd.Series(['Price: $1,234', 'Cost: 5000 USD'])
        >>> nums = NumericNormalizer.extract_numeric(s)
        >>> print(nums.tolist())
        [1234.0, 5000.0]
        """
        def extract(value):
            if pd.isna(value):
                return None
            
            # Remove currency and keep numbers
            cleaned = str(value)
            for symbol in NumericNormalizer.CURRENCY_SYMBOLS:
                cleaned = cleaned.replace(symbol, '')
            
            # Extract first number found
            match = re.search(r'[-+]?\d+[,.]?\d*', cleaned)
            if match:
                num_str = match.group().replace(',', '')
                try:
                    return float(num_str)
                except ValueError:
                    return None
            return None
        
        return series.apply(extract)
    
    @staticmethod
    def format_number(
        value: float,
        decimal_places: int = 2,
        thousand_separator: str = ',',
        decimal_separator: str = '.'
    ) -> str:
        """
        Format a number with specified separators.
        
        Parameters
        ----------
        value : float
            Number to format.
        decimal_places : int, default 2
            Number of decimal places.
        thousand_separator : str, default ','
            Character for thousand grouping.
        decimal_separator : str, default '.'
            Character for decimal point.
        
        Returns
        -------
        str
            Formatted number string.
        
        Examples
        --------
        >>> NumericNormalizer.format_number(1234.5, decimal_places=2)
        '1,234.50'
        >>> NumericNormalizer.format_number(1234.5, thousand_separator='.', decimal_separator=',')
        '1.234,50'
        """
        if pd.isna(value):
            return ''
        
        # Format with decimals
        formatted = f"{value:,.{decimal_places}f}"
        
        # Replace default separators if needed
        if thousand_separator != ',' or decimal_separator != '.':
            # Temporarily replace
            formatted = formatted.replace(',', 'TEMP')
            formatted = formatted.replace('.', decimal_separator)
            formatted = formatted.replace('TEMP', thousand_separator)
        
        return formatted
