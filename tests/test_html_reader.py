"""
Unit tests for HTMLReader class.
Tests basic functionality of reading HTML files with multiple tables.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os
from pandas_toolkit.io.readers import HTMLReader


class TestHTMLReader:
    """Test suite for HTMLReader"""
    
    @pytest.fixture
    def sample_html_single_table(self):
        """Create a temporary HTML file with a single table"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Age</th>
                    <th>City</th>
                </tr>
                <tr>
                    <td>Alice</td>
                    <td>30</td>
                    <td>New York</td>
                </tr>
                <tr>
                    <td>Bob</td>
                    <td>25</td>
                    <td>Los Angeles</td>
                </tr>
                <tr>
                    <td>Charlie</td>
                    <td>35</td>
                    <td>Chicago</td>
                </tr>
            </table>
        </body>
        </html>
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def sample_html_multiple_tables(self):
        """Create a temporary HTML file with multiple tables"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Multiple Tables</title></head>
        <body>
            <h2>Employees</h2>
            <table>
                <tr><th>Name</th><th>Department</th></tr>
                <tr><td>Alice</td><td>IT</td></tr>
                <tr><td>Bob</td><td>HR</td></tr>
            </table>
            
            <h2>Products</h2>
            <table>
                <tr><th>Product</th><th>Price</th></tr>
                <tr><td>Laptop</td><td>1000</td></tr>
                <tr><td>Mouse</td><td>25</td></tr>
            </table>
            
            <h2>Sales</h2>
            <table>
                <tr><th>Date</th><th>Amount</th></tr>
                <tr><td>2024-01-01</td><td>5000</td></tr>
                <tr><td>2024-01-02</td><td>3000</td></tr>
            </table>
        </body>
        </html>
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_reader_initialization(self):
        """Test HTMLReader can be initialized"""
        reader = HTMLReader()
        assert reader is not None
        assert reader.output_dir == "."
        assert reader.verbose is False
    
    def test_reader_initialization_with_params(self):
        """Test HTMLReader initialization with parameters"""
        reader = HTMLReader(output_dir="exports", verbose=True)
        assert reader.output_dir == "exports"
        assert reader.verbose is True
    
    def test_read_single_table(self, sample_html_single_table):
        """Test reading a single table from HTML"""
        reader = HTMLReader()
        df = reader.read(sample_html_single_table)
        
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 3  # 3 rows
        assert df.shape[1] == 3  # 3 columns
        assert list(df.columns) == ['Name', 'Age', 'City']
        assert df['Name'].tolist() == ['Alice', 'Bob', 'Charlie']
    
    def test_read_first_table_from_multiple(self, sample_html_multiple_tables):
        """Test reading first table when multiple tables exist"""
        reader = HTMLReader()
        df = reader.read(sample_html_multiple_tables, table_index=0)
        
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 2
        assert 'Name' in df.columns
        assert 'Department' in df.columns
    
    def test_read_specific_table_by_index(self, sample_html_multiple_tables):
        """Test reading specific table by index"""
        reader = HTMLReader()
        
        # Read second table (index 1)
        df1 = reader.read(sample_html_multiple_tables, table_index=1)
        assert 'Product' in df1.columns
        assert 'Price' in df1.columns
        
        # Read third table (index 2)
        df2 = reader.read(sample_html_multiple_tables, table_index=2)
        assert 'Date' in df2.columns
        assert 'Amount' in df2.columns
    
    def test_read_invalid_table_index(self, sample_html_single_table):
        """Test that invalid table index raises ValueError"""
        reader = HTMLReader()
        
        with pytest.raises(ValueError, match="Table index.*out of range"):
            reader.read(sample_html_single_table, table_index=5)
    
    def test_read_nonexistent_file(self):
        """Test that reading nonexistent file raises FileNotFoundError"""
        reader = HTMLReader()
        
        with pytest.raises(FileNotFoundError):
            reader.read("nonexistent_file.html")
    
    def test_get_tables_count(self, sample_html_multiple_tables):
        """Test getting count of tables in HTML file"""
        reader = HTMLReader()
        count = reader.get_tables_count(sample_html_multiple_tables)
        
        assert count == 3
    
    def test_read_all_tables(self, sample_html_multiple_tables):
        """Test reading all tables from HTML file"""
        reader = HTMLReader()
        tables = reader.read_all_tables(sample_html_multiple_tables)
        
        assert isinstance(tables, list)
        assert len(tables) == 3
        assert all(isinstance(df, pd.DataFrame) for df in tables)
        
        # Check first table
        assert 'Name' in tables[0].columns
        # Check second table
        assert 'Product' in tables[1].columns
        # Check third table
        assert 'Date' in tables[2].columns
    
    def test_read_multiple_tables_dict(self, sample_html_multiple_tables):
        """Test reading multiple specific tables as dictionary"""
        reader = HTMLReader()
        tables = reader.read_multiple_tables(
            sample_html_multiple_tables,
            table_indices=[0, 2]
        )
        
        assert isinstance(tables, dict)
        assert len(tables) == 2
        assert 0 in tables
        assert 2 in tables
        assert 1 not in tables
    
    def test_read_multiple_tables_all(self, sample_html_multiple_tables):
        """Test reading all tables as dictionary (no indices specified)"""
        reader = HTMLReader()
        tables = reader.read_multiple_tables(sample_html_multiple_tables)
        
        assert isinstance(tables, dict)
        assert len(tables) == 3
        assert 0 in tables
        assert 1 in tables
        assert 2 in tables
    
    def test_normalize_columns(self, sample_html_single_table):
        """Test reading with column normalization"""
        reader = HTMLReader()
        df = reader.read(sample_html_single_table, normalize_columns=True)
        
        # Column names should be normalized (lowercase, no spaces)
        assert all(col.islower() or col.endswith('_norm') for col in df.columns)
    
    def test_normalize_values(self, sample_html_single_table):
        """Test reading with value normalization"""
        reader = HTMLReader()
        df = reader.read(sample_html_single_table, normalize=True)
        
        # Should have _norm columns for string columns
        norm_columns = [col for col in df.columns if col.endswith('_norm')]
        assert len(norm_columns) > 0
    
    def test_skip_empty_rows(self):
        """Test skipping empty rows in HTML tables"""
        html_content = """
        <html>
        <body>
            <table>
                <tr><td></td><td></td></tr>
                <tr><td>Data1</td><td>Data2</td></tr>
                <tr><td>Data3</td><td>Data4</td></tr>
                <tr><td></td><td></td></tr>
            </table>
        </body>
        </html>
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            reader = HTMLReader()
            df = reader.read(
                temp_path,
                skip_leading_empty_rows=True,
                skip_trailing_empty_rows=True
            )
            
            # Should have removed empty rows
            assert df.shape[0] == 2  # Only 2 data rows
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_tables_count_attribute(self, sample_html_multiple_tables):
        """Test that tables_count attribute is set after reading"""
        reader = HTMLReader()
        reader.read(sample_html_multiple_tables, table_index=0)
        
        assert reader.tables_count == 3
    
    def test_verbose_mode(self, sample_html_single_table, capsys):
        """Test verbose output"""
        reader = HTMLReader(verbose=True)
        reader.read(sample_html_single_table)
        
        captured = capsys.readouterr()
        assert "[DEBUG]" in captured.out or "[INFO]" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
