"""
Column name normalization.

Provides specialized functionality for cleaning and standardizing DataFrame
column names.
"""

import pandas as pd
import re
import unicodedata
from collections import defaultdict
from typing import List


class ColumnNormalizer:
    """
    Specialized normalizer for DataFrame column names.
    
    Handles:
    - Trimming whitespace
    - Case conversion (lower/upper/None)
    - Accent removal
    - Special character replacement
    - Duplicate handling
    - Empty column naming
    """
    
    @staticmethod
    def normalize(
        df: pd.DataFrame,
        convert_case: str = "lower",
        empty_col_name: str = "unnamed",
        remove_special_chars: bool = True
    ) -> pd.DataFrame:
        """
        Normalize DataFrame column names.
        
        Applies the following transformations:
        1. Remove leading/trailing whitespace
        2. Convert to specified case (lower/upper/None)
        3. Remove accents and special characters
        4. Replace spaces with underscores
        5. Handle duplicates by appending numeric suffixes
        6. Handle empty columns with default name
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with potentially messy column names.
        convert_case : {'lower', 'upper', None}, default 'lower'
            Case conversion for column names.
        empty_col_name : str, default 'unnamed'
            Name for empty/missing column names.
        remove_special_chars : bool, default True
            Whether to remove special characters from column names.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with normalized column names.
        
        Examples
        --------
        >>> df = pd.DataFrame(columns=["First Name", "  Last Name  ", "Émployee-ID"])
        >>> normalized = ColumnNormalizer.normalize(df)
        >>> print(normalized.columns.tolist())
        ['first_name', 'last_name', 'employee_id']
        """
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Step 1: Clean each column name
        cleaned_cols = []
        for col in df.columns:
            if pd.isna(col) or col == "":
                cleaned = empty_col_name
            else:
                # Convert to string
                col_str = str(col).strip()
                
                # Remove accents
                col_str = ColumnNormalizer._remove_accents(col_str)
                
                # Convert case
                if convert_case == "lower":
                    col_str = col_str.lower()
                elif convert_case == "upper":
                    col_str = col_str.upper()
                
                # Replace special chars and spaces with underscore
                if remove_special_chars:
                    col_str = re.sub(r'[^\w]+', '_', col_str)
                    # Remove leading/trailing underscores
                    col_str = col_str.strip('_')
                else:
                    # Only replace spaces
                    col_str = col_str.replace(' ', '_')
                
                # Replace empty with default name
                cleaned = col_str if col_str else empty_col_name
            
            cleaned_cols.append(cleaned)
        
        # Step 2: Handle duplicates
        final_cols = ColumnNormalizer._handle_duplicate_columns(cleaned_cols, empty_col_name)
        
        df.columns = final_cols
        return df
    
    @staticmethod
    def _remove_accents(text: str) -> str:
        """
        Remove accents and diacritical marks from text.
        
        Parameters
        ----------
        text : str
            Text with potential accents.
        
        Returns
        -------
        str
            Text without accents.
        
        Examples
        --------
        >>> ColumnNormalizer._remove_accents("Café")
        'Cafe'
        >>> ColumnNormalizer._remove_accents("Português")
        'Portugues'
        """
        nfd = unicodedata.normalize('NFD', text)
        return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    
    @staticmethod
    def _handle_duplicate_columns(cols: List[str], empty_name: str = "unnamed") -> List[str]:
        """
        Handle duplicate column names by appending numeric suffixes.
        
        Parameters
        ----------
        cols : list
            List of column names.
        empty_name : str
            Name to use for empty columns.
        
        Returns
        -------
        list
            List with unique column names (duplicates get numeric suffixes).
        
        Examples
        --------
        >>> cols = ["name", "name", "age", "age"]
        >>> ColumnNormalizer._handle_duplicate_columns(cols)
        ['name', 'name_1', 'age', 'age_1']
        """
        counter = defaultdict(int)
        result = []
        
        for col in cols:
            if counter[col] == 0:
                result.append(col)
            else:
                result.append(f"{col}_{counter[col]}")
            counter[col] += 1
        
        return result
