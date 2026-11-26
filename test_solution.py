import pandas as pd
import pytest
from solution import add_virtual_column

def test_operator_precedence():

    df = pd.DataFrame({
        "a": [10, 20],
        "b": [2, 3],
        "c": [5, 4]
    })

    expected = pd.DataFrame({
        "a": [10, 20],
        "b": [2, 3],
        "c": [5, 4],
        "total": [20, 32]
    })

    result = add_virtual_column(df, "a + b * c", "total")
    pd.testing.assert_frame_equal(result, expected)

def test_revenue_calculation():

    df = pd.DataFrame({
        "quantity": [10, 3, 5],
        "unit_price": [20, 5, 10],
        "discount": [15, 2, 0]
    })

    result = add_virtual_column(
        df, "quantity * unit_price - discount", "revenue"
    )

    assert result["revenue"].tolist() == [185, 13, 50]

def test_multiple_multiplications():

    df = pd.DataFrame({
        "a": [2, 3],
        "b": [3, 4],
        "c": [4, 5]
    })

    result = add_virtual_column(df, "a * b * c", "total")
    assert result["total"].tolist() == [24, 60]

def test_subtraction_order():

    df = pd.DataFrame({
        "a": [20],
        "b": [5],
        "c": [3]
    })

    result = add_virtual_column(df, "a - b - c", "total")
    assert result["total"].tolist() == [12]

# Testing invalid roles
@pytest.mark.parametrize("role", [
    "a / b",
    "a ** b",
    "a // b",
    "a % b",
    "a +",
    "+ b",
    "a + 10",
    "a + unknown",
    "a b",
    "",
    None
])
def test_invalid_role(role):

    df = pd.DataFrame({
        "a": [10],
        "b": [5]
    })

    result = add_virtual_column(df, role, "total")
    pd.testing.assert_frame_equal(result, pd.DataFrame())

@pytest.mark.parametrize("new_column", [
    "total123",
    "total price",
    "total-price",
    "total&price",
    "total.price",
    "",
    None,
    123
])

def test_invalid_new_column(new_column):

    df = pd.DataFrame({
        "a": [10],
        "b": [5]
    })

    result = add_virtual_column(df, "a + b", new_column)
    pd.testing.assert_frame_equal(result, pd.DataFrame())

def test_original_dataframe_unchanged():

    df = pd.DataFrame({
        "a": [10, 20],
        "b": [5, 10]
    })

    original = df.copy(deep=True)
    result = add_virtual_column(df, "a + b", "total")

    pd.testing.assert_frame_equal(df, original)
    assert "total" in result.columns
    assert "total" not in df.columns
    assert result is not df

@pytest.mark.parametrize("values", [
    ["10", "20"],
    ["apple", "banana"],
    [True, False]
])

def test_invalid_data_types(values):

    df = pd.DataFrame({
        "a": values,
        "b": [5, 10]
    })

    result = add_virtual_column(df, "a + b", "total")
    pd.testing.assert_frame_equal(result, pd.DataFrame())

def test_existing_column_name():

    df = pd.DataFrame({
        "a": [10],
        "b": [5]
    })

    result = add_virtual_column(df, "a + b", "a")
    pd.testing.assert_frame_equal(result, pd.DataFrame())

def test_duplicate_column_names():

    df = pd.DataFrame(
        [[10, 20, 5]],
        columns=["a", "a", "b"]
    )

    result = add_virtual_column(df, "a + b", "total")
    pd.testing.assert_frame_equal(result, pd.DataFrame())

def test_invalid_existing_column():

    df = pd.DataFrame({
        "a": [10],
        "b": [5],
        "column123": [20]
    })

    result = add_virtual_column(df, "a + b", "total")
    pd.testing.assert_frame_equal(result, pd.DataFrame())

def test_missing_values():

    df = pd.DataFrame({
        "a": [10.0, None, 20.0],
        "b": [5, 10, 5]
    })

    result = add_virtual_column(df, "a + b", "total")

    expected = pd.Series(
        [15.0, float("nan"), 25.0],
        name="total"
    )

    pd.testing.assert_series_equal(result["total"], expected)

def test_empty_dataframe():

    df = pd.DataFrame({
        "a": pd.Series(dtype="int64"),
        "b": pd.Series(dtype="int64")
    })

    result = add_virtual_column(df, "a + b", "total")
    assert result.empty
    assert result.columns.tolist() == ["a", "b", "total"]

def test_index_preserved():

    df = pd.DataFrame({
        "a": [10, 20],
        "b": [5, 10]
    }, index=[100, 200])

    result = add_virtual_column(df, "a + b", "total")
    assert result.index.equals(df.index)
    assert result["total"].tolist() == [15, 30]

def test_invalid_dataframe():

    result = add_virtual_column(None, "a + b", "total")
    pd.testing.assert_frame_equal(result, pd.DataFrame())