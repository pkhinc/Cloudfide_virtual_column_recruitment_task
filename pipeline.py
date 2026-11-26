from pathlib import Path
import pandas as pd
from solution import add_virtual_column

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "sales.csv"
OUTPUT_FILE = BASE_DIR / "revenue_by_region.csv"

def load_data(file_path: Path) -> pd.DataFrame:
    return pd.read_csv(file_path, dtype=str)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )

    return df

def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # Remove repeated header and summary row
    df = df[~df["order_id"].isin(["TOTAL", "Order ID"])]

    # Remove duplicate rows
    df = df.drop_duplicates(keep="first")

    return df.reset_index(drop=True)

def clean_values(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # Normalize region names
    df["region"] = df["region"].str.strip().str.title()

    # Remove thousands separator
    df["quantity"] = pd.to_numeric(
        df["quantity"].str.replace(" ", "", regex=False)
    )

    # Replace decimal commas
    df["unit_price"] = pd.to_numeric(
        df["unit_price"].str.replace(",", ".", regex=False)
    )

    # Missing discount means no discount
    df["discount"] = pd.to_numeric(
        df["discount"].fillna("0")
    )

    df["order_date"] = pd.to_datetime(
        df["order_date"], format="%Y-%m-%d"
    )

    return df

def fill_missing_prices(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # Find products with one unique known price
    prices = df.groupby("product")["unit_price"].agg(
        ["nunique", "first"]
    )

    price_mapping = prices.loc[
        prices["nunique"] == 1, "first"
    ]

    # Fill missing prices using product name
    df["unit_price"] = df["unit_price"].fillna(
        df["product"].map(price_mapping)
    )

    return df

def validate_data(df: pd.DataFrame) -> None:

    if df.isna().any().any():
        raise ValueError("Missing values remain after cleaning")

    numeric_columns = ["quantity", "unit_price", "discount"]

    if df[numeric_columns].isin(
        [float("inf"), float("-inf")]
    ).any().any():
        raise ValueError("Invalid numeric values")

    if (df["unit_price"] < 0).any():
        raise ValueError("Negative unit price")

    if (df["discount"] < 0).any():
        raise ValueError("Negative discount")

def calculate_revenue(df: pd.DataFrame) -> pd.DataFrame:

    result = add_virtual_column(
        df,
        "quantity * unit_price - discount",
        "revenue"
    )

    if "revenue" not in result.columns:
        raise ValueError("Revenue calculation failed")

    return result

def aggregate_revenue(df: pd.DataFrame) -> pd.DataFrame:

    result = (
        df.groupby("region", as_index=False)["revenue"]
        .sum()
    )

    result["revenue"] = result["revenue"].round(2)
    return result

def run_pipeline(
    input_path: Path = INPUT_FILE,
    output_path: Path = OUTPUT_FILE
) -> pd.DataFrame:

    df = load_data(input_path)
    print(f"Loaded {len(df)} rows")

    df = normalize_columns(df)

    rows_before = len(df)
    df = remove_invalid_rows(df)

    print(f"Removed {rows_before - len(df)} rows")
    print(f"Remaining rows: {len(df)}")

    df = clean_values(df)
    df = fill_missing_prices(df)

    validate_data(df)

    df = calculate_revenue(df)
    result = aggregate_revenue(df)

    result.to_csv(
        output_path,
        index=False,
        float_format="%.2f"
    )

    print(result)
    print(f"Total revenue: {result['revenue'].sum():.2f}")
    print(f"Results saved to {output_path}")

    return result

def main():
    run_pipeline()

if __name__ == "__main__":
    main()