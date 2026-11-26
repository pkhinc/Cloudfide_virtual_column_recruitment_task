import pandas as pd
import pytest

from pipeline import (
    INPUT_FILE,
    normalize_columns,
    remove_invalid_rows,
    clean_values,
    fill_missing_prices,
    validate_data,
    calculate_revenue,
    aggregate_revenue,
    run_pipeline
)

def test_normalize_columns():

    df = pd.DataFrame(columns=[
        "Order ID", "Quantity ", "Unit Price"
    ])

    result = normalize_columns(df)

    assert result.columns.tolist() == [
        "order_id", "quantity", "unit_price"
    ]

def test_remove_invalid_rows():

    df = pd.DataFrame({
        "order_id": [
            "SO-10001",
            "SO-10001",
            "SO-10001",
            "Order ID",
            "TOTAL"
        ],
        "product": [
            "Mouse", "Mouse", "Keyboard", "Product", None
        ]
    })

    result = remove_invalid_rows(df)
    assert len(result) == 2
    assert result["product"].tolist() == ["Mouse", "Keyboard"]

def test_clean_values():

    df = pd.DataFrame({
        "region": [" south ", "NORTH"],
        "quantity": ["1 762", "-2"],
        "unit_price": ["39,90", "89.00"],
        "discount": [None, "5.00"],
        "order_date": ["2026-01-10", "2026-01-11"]
    })

    result = clean_values(df)

    assert result["region"].tolist() == ["South", "North"]
    assert result["quantity"].tolist() == [1762, -2]
    assert result["unit_price"].tolist() == [39.9, 89.0]
    assert result["discount"].tolist() == [0.0, 5.0]

    assert pd.api.types.is_datetime64_any_dtype(
        result["order_date"]
    )

def test_fill_missing_prices():

    df = pd.DataFrame({
        "product": ["Mouse", "Mouse", "Keyboard", "Keyboard"],
        "unit_price": [29.5, None, 89.0, None]
    })

    result = fill_missing_prices(df)

    assert result["unit_price"].tolist() == [
        29.5, 29.5, 89.0, 89.0
    ]

def test_ambiguous_product_price():

    df = pd.DataFrame({
        "product": ["Mouse", "Mouse", "Mouse"],
        "unit_price": [29.5, 35.0, None]
    })

    result = fill_missing_prices(df)
    assert pd.isna(result.loc[2, "unit_price"])

    with pytest.raises(ValueError, match="Missing values"):
        validate_data(result)

@pytest.mark.parametrize("quantity, unit_price, discount", [
    (10, -20.0, 0.0),
    (10, 20.0, -5.0),
    (10, float("inf"), 0.0)
])

def test_invalid_numeric_values(quantity, unit_price, discount):

    df = pd.DataFrame({
        "quantity": [quantity],
        "unit_price": [unit_price],
        "discount": [discount]
    })

    with pytest.raises(ValueError):
        validate_data(df)

def test_calculate_revenue():

    df = pd.DataFrame({
        "quantity": [10, 3, -2],
        "unit_price": [20.0, 5.0, 10.0],
        "discount": [15.0, 2.0, 0.0]
    })

    result = calculate_revenue(df)

    assert result["revenue"].tolist() == [
        185.0, 13.0, -20.0
    ]

def test_aggregate_revenue():

    df = pd.DataFrame({
        "region": ["North", "South", "North", "South"],
        "revenue": [100.0, 200.0, 50.0, -20.0]
    })

    expected = pd.DataFrame({
        "region": ["North", "South"],
        "revenue": [150.0, 180.0]
    })

    result = aggregate_revenue(df)
    pd.testing.assert_frame_equal(result, expected)

def test_pipeline_with_sample_data(tmp_path):

    input_file = tmp_path / "sales.csv"
    output_file = tmp_path / "revenue_by_region.csv"

    df = pd.DataFrame({
        "Order ID": ["SO-1", "SO-2", "SO-3", "SO-3"],
        "Region": [" north ", "NORTH", "South", "South"],
        "Product": ["Mouse", "Mouse", "Keyboard", "Keyboard"],
        "Quantity ": ["10", "2", "3", "3"],
        "Unit Price": ["20,00", None, "50.00", "50.00"],
        "Discount": ["5.00", None, None, None],
        "Order Date": ["2026-01-10"] * 4
    })

    df.to_csv(input_file, index=False)
    result = run_pipeline(input_file, output_file)

    expected = pd.DataFrame({
        "region": ["North", "South"],
        "revenue": [235.0, 150.0]
    })

    pd.testing.assert_frame_equal(result, expected)

    assert output_file.exists()
    saved_result = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(saved_result, expected)

def test_pipeline_with_real_data(tmp_path):

    output_file = tmp_path / "revenue_by_region.csv"
    result = run_pipeline(INPUT_FILE, output_file)

    expected = pd.DataFrame({
        "region": ["Central", "East", "North", "South", "West"],
        "revenue": [
            515824.67,
            442219.91,
            665897.52,
            504036.04,
            442268.89
        ]
    })

    pd.testing.assert_frame_equal(result, expected)

    assert len(result) == 5
    assert result["revenue"].sum() == pytest.approx(2570247.03)
    assert output_file.exists()

    pd.testing.assert_frame_equal(
        pd.read_csv(output_file),
        expected
    )