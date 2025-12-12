import pandas as pd
from pandas_toolkit.io.csv_reader import CSVReader
import pytest


# Usamos fixtures de pytest para manejar carpetas temporales
@pytest.fixture
def tmp_csv(tmp_path):
    """
    Crea un CSV temporal con contenido simple.
    """
    data = "col1,col2\n1,2\n3,4"
    p = tmp_path / "test.csv"
    p.write_text(data, encoding="utf-8")
    return p


def test_csvreader_basic_read(tmp_csv):
    reader = CSVReader()

    df = reader.read(tmp_csv)

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["col1", "col2"]
    assert df.iloc[0]["col1"] == 1


def test_csvreader_custom_delimiter(tmp_path):
    p = tmp_path / "test_pipe.csv"
    p.write_text("a|b\n1|2", encoding="utf-8")

    reader = CSVReader(delimiters=["|"])

    df = reader.read(p)

    assert df.shape == (1, 2)
    assert df.iloc[0]["a"] == 1


def test_csvreader_read_multiple_files(tmp_path):
    # Creamos 2 CSVs
    (tmp_path / "file1.csv").write_text("x,y\n1,2")
    (tmp_path / "file2.csv").write_text("x,y\n3,4")

    reader = CSVReader()

    df = reader.read_multiple_files(tmp_path)

    assert df.shape == (2, 2)
    assert df["x"].tolist() == [1, 3]


def test_csvreader_export_to_csv(tmp_path):
    reader = CSVReader(output_dir=str(tmp_path))
    df = pd.DataFrame({"a": [1, 2]})

    reader.export(df, method="csv", filename="output.csv")

    output_file = tmp_path / "output.csv"
    assert output_file.exists()

    loaded = pd.read_csv(output_file)
    assert loaded.shape == (2, 1)
    assert loaded.iloc[1]["a"] == 2


def test_csvreader_export_to_excel(tmp_path):
    reader = CSVReader(output_dir=str(tmp_path))
    df = pd.DataFrame({"a": [1, 2]})

    reader.export(df, method="excel", filename="output.xlsx")

    output_file = tmp_path / "output.xlsx"
    assert output_file.exists()

    loaded = pd.read_excel(output_file)
    assert loaded.shape == (2, 1)

