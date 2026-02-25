import pandas as pd
from pathlib import Path
from typing import Optional, Union, Dict, Any
import warnings

from .normalizers import (
    NormalizationConfig,
    ColumnNormalizer,
    StringNormalizer,
    NullNormalizer
)


class NormalizeMixin:
    """
    Mixin that adds data normalization methods to reader classes.
    
    Provides methods for:
    - Normalizing column names (remove accents, standardize casing)
    - Normalizing cell values (trim whitespace, convert case, handle nulls)
    - Handling empty rows and columns
    - Configuration-based normalization with presets
    
    Uses specialized normalizers:
    - ColumnNormalizer: For column name normalization
    - StringNormalizer: For string value normalization
    - NullNormalizer: For null value standardization
    """
    
    def normalize_columns(
        self,
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
        >>> normalized = reader.normalize_columns(df)
        >>> print(normalized.columns.tolist())
        ['first_name', 'last_name', 'employee_id']
        """
        return ColumnNormalizer.normalize(
            df,
            convert_case=convert_case,
            empty_col_name=empty_col_name,
            remove_special_chars=remove_special_chars
        )

    def normalize(
        self,
        df: pd.DataFrame,
        drop_empty_cols: bool = False,
        drop_empty_rows: bool = False,
        trim_strings: bool = True,
        convert_case: str = "lower",
        standardize_nulls: bool = True,
        null_values: Optional[list] = None,
        drop_original: bool = False,
        suffix: str = "_norm",
        config: Optional[Union[NormalizationConfig, Dict[str, Any]]] = None,
        preset: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Normalize DataFrame cell values.
        
        Can create new columns with suffix (default behavior) or replace
        original columns (if drop_original=True).
        
        Transformations applied:
        1. Standardize null values (if standardize_nulls=True)
        2. Trim leading/trailing whitespace (if trim_strings=True)
        3. Convert to specified case (if convert_case is set)
        4. Convert empty strings to None
        5. Drop empty rows/columns (if configured)
        
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
        standardize_nulls : bool, default True
            Standardize various null representations to np.nan.
        null_values : list of str, optional
            Additional values to treat as null (beyond defaults).
        drop_original : bool, default False
            If True, replaces original columns. If False, creates new columns with suffix.
        suffix : str, default '_norm'
            Suffix for normalized columns (only used if drop_original=False).
        config : NormalizationConfig or dict, optional
            Configuration object or dict. Overrides individual parameters.
        preset : str, optional
            Preset configuration name ('minimal', 'basic', 'full', 'analysis_ready').
            Shortcut for config=NormalizationConfig.from_preset(preset).
        
        Returns
        -------
        pd.DataFrame
            DataFrame with normalized values (either replaced or as new columns).
        
        Examples
        --------
        >>> # Basic usage (backward compatible)
        >>> df = pd.DataFrame({
        ...     "Name": ["  JUAN  ", "  MARIA  "],
        ...     "Status": ["  ACTIVE  ", "  "]
        ... })
        >>> normalized = reader.normalize(df, trim_strings=True, convert_case="lower")
        >>> print(normalized.columns.tolist())
        ['Name', 'Status', 'Name_norm', 'Status_norm']
        
        >>> # Replace original columns
        >>> normalized = reader.normalize(df, drop_original=True)
        >>> print(normalized.columns.tolist())
        ['Name', 'Status']
        
        >>> # Using preset
        >>> normalized = reader.normalize(df, preset='basic')
        
        >>> # Using config
        >>> config = NormalizationConfig.from_preset('full')
        >>> normalized = reader.normalize(df, config=config)
        """
        df = df.copy()
        
        # Handle configuration
        if preset is not None:
            config = NormalizationConfig.from_preset(preset)
        elif isinstance(config, dict):
            config = NormalizationConfig.from_dict(config)
        elif config is None:
            # Build config from individual parameters
            config = NormalizationConfig(
                strings={'trim': trim_strings, 'case': convert_case, 'remove_special': False},
                nulls={'standardize': standardize_nulls, 'values': null_values or []},
                columns={'drop_original': drop_original, 'suffix': suffix, 'drop_empty': drop_empty_cols}
            )
        
        # Apply configuration parameters
        drop_empty_rows = drop_empty_rows or config.columns.get('drop_empty', False)
        drop_empty_cols = config.columns.get('drop_empty', drop_empty_cols)
        drop_original = config.columns.get('drop_original', drop_original)
        suffix = config.columns.get('suffix', suffix)
        
        # Step 1: Standardize null values
        if config.nulls.get('standardize', True):
            custom_nulls = config.nulls.get('values', [])
            df = NullNormalizer.normalize(df, null_values=custom_nulls, include_defaults=True)
        
        # Step 2: Drop empty rows
        if drop_empty_rows:
            df = df.dropna(how='all')
        
        # Step 3: Drop empty columns
        if drop_empty_cols:
            df = df.dropna(axis=1, how='all')
        
        # Step 4: Normalize string values in each column
        trim = config.strings.get('trim', True)
        case = config.strings.get('case', 'lower')
        remove_special = config.strings.get('remove_special', False)
        
        for col in df.columns:
            # Only process object/string columns
            if StringNormalizer.is_string_column(df[col]):
                # Normalize the column
                normalized_values = StringNormalizer.normalize(
                    df[col],
                    trim=trim,
                    convert_case=case,
                    remove_special_chars=remove_special
                )
                
                if drop_original:
                    # Replace original column
                    df[col] = normalized_values
                else:
                    # Create new column with suffix
                    normalized_col = f"{col}{suffix}"
                    df[normalized_col] = normalized_values
        
        return df
    
    # Legacy support: delegate to specialized normalizers
    @staticmethod
    def _remove_accents(text: str) -> str:
        """
        Remove accents and diacritical marks from text.
        
        .. deprecated::
            Use ColumnNormalizer._remove_accents() instead.
            This method is kept for backward compatibility.
        """
        return ColumnNormalizer._remove_accents(text)
    
    @staticmethod
    def _handle_duplicate_columns(cols: list, empty_name: str = "unnamed") -> list:
        """
        Handle duplicate column names by appending numeric suffixes.
        
        .. deprecated::
            Use ColumnNormalizer._handle_duplicate_columns() instead.
            This method is kept for backward compatibility.
        """
        return ColumnNormalizer._handle_duplicate_columns(cols, empty_name)