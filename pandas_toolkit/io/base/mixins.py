import pandas as pd
from pathlib import Path
from collections import defaultdict
import re
import unicodedata


class NormalizeMixin:
    """
    Mixin that adds data normalization methods to reader classes.
    
    Provides methods for:
    - Normalizing column names (remove accents, standardize casing)
    - Normalizing cell values (trim whitespace, convert case)
    - Handling empty rows and columns
    """
    
    def normalize_columns(
        self,
        df: pd.DataFrame,
        convert_case: str = "lower",
        empty_col_name: str = "unnamed"
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
        
        Returns
        -------
        pd.DataFrame
            DataFrame with normalized column names.
        
        Examples
        --------
        >>> df = pd.DataFrame(columns=["First Name", "  Last Name  ", "Émployee-ID"])
        >>> normalized = reader.normalize_columns(df)
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
                col_str = self._remove_accents(col_str)
                
                # Convert case
                if convert_case == "lower":
                    col_str = col_str.lower()
                elif convert_case == "upper":
                    col_str = col_str.upper()
                
                # Replace special chars and spaces with underscore
                col_str = re.sub(r'[^\w]+', '_', col_str)
                
                # Remove leading/trailing underscores
                col_str = col_str.strip('_')
                
                # Replace empty with default name
                cleaned = col_str if col_str else empty_col_name
            
            cleaned_cols.append(cleaned)
        
        # Step 2: Handle duplicates
        final_cols = self._handle_duplicate_columns(cleaned_cols, empty_col_name)
        
        df.columns = final_cols
        return df

    def normalize(
        self,
        df: pd.DataFrame,
        drop_empty_cols: bool = False,
        drop_empty_rows: bool = False,
        trim_strings: bool = True,
        convert_case: str = "lower"
    ) -> pd.DataFrame:
        """
        Normalize DataFrame cell values.
        
        Creates new columns with "_norm" suffix containing normalized values.
        Original columns are preserved.
        
        Transformations applied:
        1. Trim leading/trailing whitespace (if trim_strings=True)
        2. Convert to specified case (if convert_case is set)
        3. Convert empty strings to None
        4. Drop empty rows/columns (if configured)
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with potentially messy values.
        drop_empty_cols : bool, default False
            Remove columns with all NaN values.
        drop_empty_rows : bool, default False
            Remove rows with all NaN values.
        trim_strings : bool, default True
            Strip whitespace from string values.
        convert_case : {'lower', 'upper', None}, default 'lower'
            Case conversion for string values.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with original columns plus new "_norm" columns.
        
        Examples
        --------
        >>> df = pd.DataFrame({
        ...     "Name": ["  JUAN  ", "  MARIA  "],
        ...     "Status": ["  ACTIVE  ", "  "]
        ... })
        >>> normalized = reader.normalize(df, trim_strings=True, convert_case="lower")
        >>> print(normalized.columns.tolist())
        ['Name', 'Status', 'Name_norm', 'Status_norm']
        >>> print(normalized['Name_norm'].tolist())
        ['juan', 'maria']
        """
        df = df.copy()
        
        # Drop empty rows
        if drop_empty_rows:
            df = df.dropna(how='all')
        
        # Drop empty columns
        if drop_empty_cols:
            df = df.dropna(axis=1, how='all')
        
        # Create normalized columns
        for col in df.columns:
            normalized_col = f"{col}_norm"
            
            # Get the column values
            values = df[col].copy()
            
            # Convert to string for processing
            values = values.astype(str)
            
            # Trim strings
            if trim_strings:
                values = values.str.strip()
            
            # Convert empty strings and 'nan' to None
            values = values.replace('nan', None)
            values = values.replace('', None)
            
            # Convert case
            if convert_case == "lower":
                values = values.str.lower()
            elif convert_case == "upper":
                values = values.str.upper()
            
            # Add normalized column
            df[normalized_col] = values
        
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
        >>> NormalizeMixin._remove_accents("Café")
        'Cafe'
        >>> NormalizeMixin._remove_accents("Português")
        'Portugues'
        """
        nfd = unicodedata.normalize('NFD', text)
        return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')

    @staticmethod
    def _handle_duplicate_columns(cols: list, empty_name: str = "unnamed") -> list:
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
        >>> NormalizeMixin._handle_duplicate_columns(cols)
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