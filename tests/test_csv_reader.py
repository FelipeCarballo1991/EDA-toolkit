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

    tablas = reader.read_multiple_files(tmp_path)

    df_concatenado = pd.concat(tablas)

    assert df_concatenado.shape == (2, 2)
    assert df_concatenado["x"].tolist() == [1, 3]


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


def test_csvreader_encoding_fallback(tmp_path):
    # Texto con acento, guardado en latin1
    content = "nombre,edad\nJosé,30"
    p = tmp_path / "latin1.csv"
    p.write_bytes(content.encode("latin1"))

    reader = CSVReader(encodings=["utf-8", "latin1"])

    df = reader.read(p)

    assert df.iloc[0]["nombre"] == "José"


def test_csvreader_delimiter_autodetect(tmp_path):
    p = tmp_path / "semicolon.csv"
    p.write_text("a;b;c\n1;2;3", encoding="utf-8")

    reader = CSVReader(delimiters=[",", ";"])

    df = reader.read(p)

    assert df.shape == (1, 3)
    assert list(df.columns) == ["a", "b", "c"]


def test_csvreader_read_and_normalize(tmp_path):
    p = tmp_path / "norm.csv"
    p.write_text("Name,City\n  Juan  , Buenos Aires ")

    reader = CSVReader()

    df = reader.read_and_normalize(p)

    assert "Name_norm" in df.columns
    assert "City_norm" in df.columns
    assert df.loc[0, "Name_norm"] == "juan"
    assert df.loc[0, "City_norm"] == "buenos aires"


def test_normalize_columns_lowercase():
    df = pd.DataFrame(
        columns=[
            "   Nombre y Apellido   ",
            "Edad",
            "Émployee-ID"
        ]
    )

    reader = CSVReader()
    normalized = reader.normalize_columns(df, convert_case="lower")

    assert normalized.columns.tolist() == [
        "nombre_y_apellido",
        "edad",
        "employee_id"
    ]


def test_normalize_columns_uppercase():
    df = pd.DataFrame(
        columns=[
            "   Nombre y Apellido   ",
            "Edad",
            "Émployee-ID"
        ]
    )

    reader = CSVReader()
    normalized = reader.normalize_columns(df, convert_case="upper")

    assert normalized.columns.tolist() == [
        "NOMBRE_Y_APELLIDO",
        "EDAD",
        "EMPLOYEE_ID"
    ]
