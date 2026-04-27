import pandas as pd
from pathlib import Path
from typing import Optional, Union, Dict, Any, Tuple
import warnings
import time

from .normalizers import (
    NormalizationConfig,
    ColumnNormalizer,
    StringNormalizer,
    NullNormalizer,
    DateNormalizer,
    NumericNormalizer,
    NormalizationReport,
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
        preset: Optional[str] = None,
        verbose: bool = False,
        return_report: bool = False
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, NormalizationReport]]:
        """
        Normalize DataFrame cell values with comprehensive transformations.
        
        Can create new columns with suffix (default behavior) or replace
        original columns (if drop_original=True).
        
        Transformations applied:
        1. Standardize null values (if standardize_nulls=True)
        2. Trim leading/trailing whitespace (if trim_strings=True)
        3. Convert to specified case (if convert_case is set)
        4. Normalize dates (if dates.normalize=True in config)
        5. Normalize numbers (if numbers.normalize=True in config)
        6. Convert empty strings to None
        7. Drop empty rows/columns (if configured)
        
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
        verbose : bool, default False
            Print progress messages during normalization.
        return_report : bool, default False
            Return tuple of (DataFrame, NormalizationReport) instead of just DataFrame.
        
        Returns
        -------
        pd.DataFrame or tuple
            Normalized DataFrame, or tuple of (DataFrame, NormalizationReport) if return_report=True.
        
        Examples
        --------
        >>> # Basic usage with verbose
        >>> df = reader.normalize(df, preset='basic', verbose=True)
        [NORMALIZE] Starting normalization with preset 'basic'...
        [NORMALIZE] → Standardized 23 null values
        [NORMALIZE] ✓ Complete (0.45s)
        
        >>> # With report
        >>> df, report = reader.normalize(df, preset='full', return_report=True)
        >>> print(report.summary())
        """
        # Start timing
        start_time = time.time()
        
        # Initialize report
        report = NormalizationReport(preset_used=preset if preset else None)
        report.rows_processed = len(df)
        report.columns_processed = len(df.columns)
        
        if verbose:
            preset_msg = f" with preset '{preset}'" if preset else ""
            print(f"[NORMALIZE] Starting normalization{preset_msg}...")
        
        # Work with copy
        df = df.copy()
        
        # Handle configuration
        if preset is not None:
            config =NormalizationConfig.from_preset(preset)
        elif isinstance(config, dict):
            config = NormalizationConfig.from_dict(config)
        elif config is None:
            # Build config from individual parameters
            config = NormalizationConfig(
                strings={'trim': trim_strings, 'case': convert_case, 'remove_special': False},
                nulls={'standardize': standardize_nulls, 'values': null_values or []},
                columns={'drop_original': drop_original, 'suffix': suffix, 'drop_empty': drop_empty_cols}
            )
        
        # Store config in report
        report.config_used = config.to_dict()
        
        # Apply configuration parameters
        drop_empty_rows = drop_empty_rows or config.columns.get('drop_empty', False)
        drop_empty_cols = config.columns.get('drop_empty', drop_empty_cols)
        drop_original = config.columns.get('drop_original', drop_original)
        suffix = config.columns.get('suffix', suffix)
        
        # Step 1: Standardize null values
        if config.nulls.get('standardize', True):
            if verbose:
                print("[NORMALIZE] → Standardizing null values...")
            
            custom_nulls = config.nulls.get('values', [])
            original_nulls = df.isna().sum().sum()
            df = NullNormalizer.normalize(df, null_values=custom_nulls, include_defaults=True)
            new_nulls = df.isna().sum().sum()
            nulls_added = new_nulls - original_nulls
            
            if nulls_added > 0:
                report.add_transformation(
                    name='null_standardization',
                    description='Standardized null values',
                    values_changed=nulls_added,
                    details={'null_values': config.nulls.get('values', []) + NullNormalizer.DEFAULT_NULL_VALUES[:7]}
                )
                if verbose:
                    print(f"[NORMALIZE]   Standardized {nulls_added} null values")
        
        # Step 2: Drop empty rows
        if drop_empty_rows:
            original_rows = len(df)
            df = df.dropna(how='all')
            rows_dropped = original_rows - len(df)
            
            if rows_dropped > 0:
                report.add_transformation(
                    name='drop_empty_rows',
                    description='Dropped empty rows',
                    values_changed=rows_dropped
                )
                if verbose:
                    print(f"[NORMALIZE] → Dropped {rows_dropped} empty rows")
        
        # Step 3: Drop empty columns
        if drop_empty_cols:
            original_cols = len(df.columns)
            df = df.dropna(axis=1, how='all')
            cols_dropped = original_cols - len(df.columns)
            
            if cols_dropped > 0:
                report.add_transformation(
                    name='drop_empty_columns',
                    description='Dropped empty columns',
                    values_changed=cols_dropped
                )
                if verbose:
                    print(f"[NORMALIZE] → Dropped {cols_dropped} empty columns")
        
        # Step 4: Normalize dates
        if config.dates.get('normalize', False):
            if verbose:
                print("[NORMALIZE] → Normalizing dates...")
            
            output_format = config.dates.get('format', '%d/%m/%Y')
            infer = config.dates.get('infer', True)
            
            date_cols_processed = 0
            total_dates_normalized = 0
            
            for col in df.columns:
                if DateNormalizer.is_date_column(df[col]):
                    normalized_dates, stats = DateNormalizer.normalize(
                        df[col],
                        output_format=output_format,
                        infer_format=infer
                    )
                    
                    if stats['successful_parses'] > 0:
                        if drop_original:
                            df[col] = normalized_dates
                        else:
                            df[f"{col}{suffix}"] = normalized_dates
                        
                        date_cols_processed += 1
                        total_dates_normalized += stats['successful_parses']
                        
                        # Track formats detected
                        report.add_column_change(
                            column=col,
                            changes={
                                'type': 'date',
                                'formats_detected': stats.get('formats_detected', {}),
                                'output_format': output_format,
                                'successful_parses': stats['successful_parses'],
                                'failed_parses': stats['failed_parses']
                            }
                        )
                        
                        if stats['failed_parses'] > 0:
                            report.warnings.append(
                                f"Column '{col}': {stats['failed_parses']} dates could not be parsed"
                            )
            
            if total_dates_normalized > 0:
                formats_found = {}
                for col_info in report.column_changes.values():
                    if 'changes' in col_info and 'formats_detected' in col_info['changes']:
                        for fmt, count in col_info['changes']['formats_detected'].items():
                            formats_found[fmt] = formats_found.get(fmt, 0) + count
                
                report.add_transformation(
                    name='date_normalization',
                    description=f'Normalized dates to {output_format}',
                    values_changed=total_dates_normalized,
                    details={
                        'columns_processed': date_cols_processed,
                        'formats_detected': formats_found,
                        'output_format': output_format
                    }
                )
                if verbose:
                    print(f"[NORMALIZE]   Normalized {total_dates_normalized} dates in {date_cols_processed} columns")
        
        # Step 5: Normalize numbers
        if config.numbers.get('normalize', False):
            if verbose:
                print("[NORMALIZE] → Normalizing numeric values...")
            
            remove_currency = config.numbers.get('remove_currency', True)
            handle_percentages = config.numbers.get('handle_percentages', True)
            
            numeric_cols_processed = 0
            total_numbers_normalized = 0
            
            for col in df.columns:
                if NumericNormalizer.is_numeric_column(df[col]):
                    normalized_numbers, stats = NumericNormalizer.normalize(
                        df[col],
                        remove_currency=remove_currency,
                        handle_percentages=handle_percentages
                    )
                    
                    if stats['successful_conversions'] > 0:
                        if drop_original:
                            df[col] = normalized_numbers
                        else:
                            df[f"{col}{suffix}"] = normalized_numbers
                        
                        numeric_cols_processed += 1
                        total_numbers_normalized += stats['successful_conversions']
                        
                        report.add_column_change(
                            column=col,
                            changes={
                                'type': 'numeric',
                                'currency_removed': stats['currency_symbols_removed'],
                                'separators_removed': stats['separators_removed'],
                                'percentages_converted': stats['percentages_converted'],
                                'successful_conversions': stats['successful_conversions'],
                                'failed_conversions': stats['failed_conversions']
                            }
                        )
                        
                        if stats['failed_conversions'] > 0:
                            report.warnings.append(
                                f"Column '{col}': {stats['failed_conversions']} values could not be converted to numeric"
                            )
            
            if total_numbers_normalized > 0:
                total_currency = sum(c['changes'].get('currency_removed', 0) for c in report.column_changes.values() if 'changes' in c)
                total_percentages = sum(c['changes'].get('percentages_converted', 0) for c in report.column_changes.values() if 'changes' in c)
                
                report.add_transformation(
                    name='numeric_normalization',
                    description='Normalized numeric values',
                    values_changed=total_numbers_normalized,
                    details={
                        'columns_processed': numeric_cols_processed,
                        'currency_symbols_removed': total_currency,
                        'percentages_converted': total_percentages
                    }
                )
                if verbose:
                    print(f"[NORMALIZE]   Normalized {total_numbers_normalized} numeric values in {numeric_cols_processed} columns")
        
        # Step 6: Normalize string values
        trim = config.strings.get('trim', True)
        case = config.strings.get('case', 'lower')
        remove_special = config.strings.get('remove_special', False)
        
        if trim or case or remove_special:
            if verbose:
                print("[NORMALIZE] → Normalizing string values...")
            
            string_cols_processed = 0
            total_strings_normalized = 0
            
            for col in df.columns:
                # Only process object/string columns (skip already processed numeric/date columns)
                if StringNormalizer.is_string_column(df[col]):
                    # Skip if already processed as date or numeric
                    if col in report.column_changes:
                        col_type = report.column_changes[col].get('changes', {}).get('type')
                        if col_type in ['date', 'numeric']:
                            continue
                    
                    normalized_values = StringNormalizer.normalize(
                        df[col],
                        trim=trim,
                        convert_case=case,
                        remove_special_chars=remove_special
                    )
                    
                    # Count changes by comparing non-null values with same index
                    mask = df[col].notna()
                    if mask.any():
                        original_non_null = df[col][mask].astype(str)
                        normalized_non_null = normalized_values[mask].astype(str)
                        changes = (original_non_null != normalized_non_null).sum()
                    else:
                        changes = 0
                    
                    if changes > 0 or drop_original:
                        if drop_original:
                            df[col] = normalized_values
                        else:
                            normalized_col = f"{col}{suffix}"
                            df[normalized_col] = normalized_values
                        
                        string_cols_processed += 1
                        total_strings_normalized += changes
            
            if total_strings_normalized > 0:
                report.add_transformation(
                    name='string_normalization',
                    description=f'Normalized string values (trim={trim}, case={case})',
                    values_changed=total_strings_normalized,
                    details={
                        'trim': trim,
                        'case': case,
                        'remove_special': remove_special,
                        'columns_processed': string_cols_processed
                    }
                )
                if verbose:
                    print(f"[NORMALIZE]   Normalized {total_strings_normalized} string values in {string_cols_processed} columns")
        
        # Finalize report
        report.time_elapsed = time.time() - start_time
        
        if verbose:
            total_changes = sum(report.stats.values())
            print(f"[NORMALIZE] ✓ Normalization complete ({report.time_elapsed:.2f}s, {total_changes:,} values modified)")
        
        # Return based on return_report flag
        if return_report:
            return df, report
        else:
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