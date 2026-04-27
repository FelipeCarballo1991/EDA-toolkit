"""
Normalization report system.

Provides detailed tracking and reporting of all normalization transformations
applied to DataFrames.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json


def _convert_to_python_types(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: _convert_to_python_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_convert_to_python_types(item) for item in obj]
    else:
        return obj


@dataclass
class Transformation:
    """Record of a single transformation."""
    name: str
    description: str
    values_changed: int
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


class NormalizationReport:
    """
    Report of normalization operations applied to a DataFrame.
    
    Tracks all transformations, statistics, and provides various
    output formats for analysis and auditing.
    
    Attributes
    ----------
    preset_used : str, optional
        Name of preset configuration used.
    rows_processed : int
        Number of rows in the DataFrame.
    columns_processed : int
        Number of columns processed.
    transformations : list of Transformation
        List of all transformations applied.
    stats : dict
        Summary statistics of transformations.
    time_elapsed : float
        Time taken for normalization (seconds).
    config_used : dict
        Configuration that was applied.
    
    Examples
    --------
    >>> df, report = reader.normalize(df, preset='basic', return_report=True)
    >>> print(report.summary())
    >>> report.to_json('report.json')
    """
    
    def __init__(
        self,
        preset_used: Optional[str] = None,
        config_used: Optional[Dict[str, Any]] = None
    ):
        """Initialize a new normalization report."""
        self.preset_used = preset_used
        self.config_used = config_used or {}
        self.rows_processed = 0
        self.columns_processed = 0
        self.transformations: List[Transformation] = []
        self.stats: Dict[str, int] = {}
        self.time_elapsed = 0.0
        self.timestamp = datetime.now()
        self.warnings: List[str] = []
        self.column_changes: Dict[str, Dict[str, Any]] = {}
        
    def add_transformation(
        self,
        name: str,
        description: str,
        values_changed: int = 0,
        details: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None
    ) -> None:
        """
        Add a transformation to the report.
        
        Parameters
        ----------
        name : str
            Name of the transformation.
        description : str
            Human-readable description.
        values_changed : int, default 0
            Number of values modified.
        details : dict, optional
            Additional details about the transformation.
        warnings : list of str, optional
            Warnings generated during transformation.
        """
        transformation = Transformation(
            name=name,
            description=description,
            values_changed=values_changed,
            details=details or {},
            warnings=warnings or []
        )
        self.transformations.append(transformation)
        
        # Update stats
        if name not in self.stats:
            self.stats[name] = 0
        self.stats[name] += values_changed
        
        # Collect warnings
        if warnings:
            self.warnings.extend(warnings)
    
    def add_column_change(
        self,
        column: str,
        original_name: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add column-specific changes.
        
        Parameters
        ----------
        column : str
            Column name.
        original_name : str, optional
            Original column name if it was renamed.
        changes : dict, optional
            Details of changes to this column.
        """
        if column not in self.column_changes:
            self.column_changes[column] = {
                'original_name': original_name or column,
                'changes': changes or {}
            }
        else:
            self.column_changes[column]['changes'].update(changes or {})
    
    def summary(self, verbose: bool = False) -> str:
        """
        Generate a summary of the normalization report.
        
        Parameters
        ----------
        verbose : bool, default False
            Include detailed information.
        
        Returns
        -------
        str
            Formatted summary string.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("NORMALIZATION REPORT")
        lines.append("=" * 60)
        
        # Basic info
        lines.append(f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        if self.preset_used:
            lines.append(f"Preset: {self.preset_used}")
        lines.append(f"Rows processed: {self.rows_processed:,}")
        lines.append(f"Columns processed: {self.columns_processed}")
        lines.append(f"Time elapsed: {self.time_elapsed:.2f}s")
        lines.append("")
        
        # Transformations
        if self.transformations:
            lines.append("TRANSFORMATIONS APPLIED:")
            lines.append("-" * 60)
            
            for trans in self.transformations:
                if trans.values_changed > 0:
                    lines.append(f"✓ {trans.description}: {trans.values_changed:,} values")
                    
                    if verbose and trans.details:
                        for key, value in trans.details.items():
                            lines.append(f"  - {key}: {value}")
                    
                    if trans.warnings:
                        for warning in trans.warnings:
                            lines.append(f"  ⚠️  {warning}")
            lines.append("")
        
        # Summary stats
        total_changes = sum(self.stats.values())
        if total_changes > 0:
            lines.append(f"TOTAL VALUES MODIFIED: {total_changes:,}")
            lines.append("")
        
        # Warnings
        if self.warnings:
            lines.append("WARNINGS:")
            lines.append("-" * 60)
            for warning in set(self.warnings):  # Unique warnings
                lines.append(f"⚠️  {warning}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def details(self) -> str:
        """
        Generate detailed report with column-by-column information.
        
        Returns
        -------
        str
            Detailed formatted report.
        """
        lines = [self.summary()]
        
        if self.column_changes:
            lines.append("\nDETAILED COLUMN CHANGES:")
            lines.append("=" * 60)
            
            for column, info in self.column_changes.items():
                lines.append(f"\nColumn: '{column}'")
                if info['original_name'] != column:
                    lines.append(f"  Original name: '{info['original_name']}'")
                
                if info['changes']:
                    for change_type, change_info in info['changes'].items():
                        lines.append(f"  - {change_type}: {change_info}")
        
        return "\n".join(lines)
    
    def get_transformation_stats(self) -> pd.DataFrame:
        """
        Get transformation statistics as a DataFrame.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with transformation statistics.
        """
        if not self.transformations:
            return pd.DataFrame()
        
        data = []
        for trans in self.transformations:
            data.append({
                'transformation': trans.name,
                'description': trans.description,
                'values_changed': trans.values_changed,
                'warnings': len(trans.warnings)
            })
        
        return pd.DataFrame(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert report to dictionary.
        
        Returns
        -------
        dict
            Dictionary representation of the report.
        """
        data = {
            'timestamp': self.timestamp.isoformat(),
            'preset_used': self.preset_used,
            'config_used': self.config_used,
            'rows_processed': self.rows_processed,
            'columns_processed': self.columns_processed,
            'time_elapsed': self.time_elapsed,
            'transformations': [
                {
                    'name': t.name,
                    'description': t.description,
                    'values_changed': t.values_changed,
                    'details': t.details,
                    'warnings': t.warnings
                }
                for t in self.transformations
            ],
            'stats': self.stats,
            'warnings': self.warnings,
            'column_changes': self.column_changes
        }
        
        # Convert all numpy types to Python native types
        return _convert_to_python_types(data)
    
    def to_json(self, filepath: str, indent: int = 2) -> None:
        """
        Save report to JSON file.
        
        Parameters
        ----------
        filepath : str
            Path to save JSON file.
        indent : int, default 2
            JSON indentation level.
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=indent, ensure_ascii=False)
    
    def to_markdown(self, filepath: str) -> None:
        """
        Save report to Markdown file.
        
        Parameters
        ----------
        filepath : str
            Path to save Markdown file.
        """
        lines = []
        lines.append("# Normalization Report\n")
        lines.append(f"**Generated:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if self.preset_used:
            lines.append(f"**Preset:** {self.preset_used}\n")
        
        lines.append(f"**Duration:** {self.time_elapsed:.2f}s\n")
        lines.append(f"**Rows:** {self.rows_processed:,}\n")
        lines.append(f"**Columns:** {self.columns_processed}\n")
        
        # Transformations table
        if self.transformations:
            lines.append("\n## Transformations Applied\n")
            lines.append("| Transformation | Values Changed | Warnings |")
            lines.append("|----------------|----------------|----------|")
            
            for trans in self.transformations:
                warnings_count = len(trans.warnings)
                lines.append(f"| {trans.description} | {trans.values_changed:,} | {warnings_count} |")
        
        # Warnings
        if self.warnings:
            lines.append("\n## Warnings\n")
            for warning in set(self.warnings):
                lines.append(f"- ⚠️ {warning}")
        
        # Column changes
        if self.column_changes:
            lines.append("\n## Column Changes\n")
            lines.append("| Column | Original Name | Changes |")
            lines.append("|--------|---------------|---------|")
            
            for column, info in self.column_changes.items():
                orig = info['original_name']
                changes = len(info['changes'])
                lines.append(f"| {column} | {orig} | {changes} |")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def __str__(self) -> str:
        """String representation of the report."""
        return self.summary()
    
    def __repr__(self) -> str:
        """Repr of the report."""
        return f"<NormalizationReport: {len(self.transformations)} transformations, {sum(self.stats.values())} values changed>"
