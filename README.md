# Virtual columns in pandas DataFrame

## Project description

Project uses Python and pandas to calculate new columns, clean sales data and calculate revenue by region. Tests use pytest.

## Setup

Clone repository and open project folder:

```powershell
git clone https://github.com/pkhinc/Cloudfide_virtual_column_recruitment_task.git
cd Cloudfide_virtual_column_recruitment_task
```

Create and activate virtual environment (Windows PowerShell):

```powershell
python -m venv data_eng_cloud
.\data_eng_cloud\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run pipeline and tests

Run pipeline:

```powershell
python pipeline.py
```

Output is saved to `revenue_by_region.csv`.

Run all tests with one command:

```powershell
python -m pytest -v
```

Expected result: 52 passed (6 original tests, 34 additional function tests and 12 pipeline tests).

## Virtual column function

Function `add_virtual_column(df, role, new_column)` returns new DataFrame with calculated column. Original DataFrame stays unchanged.

Example:

```python
import pandas as pd
from solution import add_virtual_column

df = pd.DataFrame({"quantity": [10], "price": [20]})
result = add_virtual_column(df, "quantity * price", "total")
print(result)
```

Expected value in `total` column: 200.

Assumptions:

- Column names can contain English letters and underscores only.
- Validate all column names, also columns not used in calculation.
- Support addition, subtraction and multiplication with standard operator order.
- Allow spaces in expression. Support expressions with multiple operators.
- No division, brackets, numeric constants or unary operators. Expression must contain at least one operator between column names.
- Use numeric columns only for calculation. Do not convert text to numbers or accept boolean columns.
- Reject duplicate column names and do not overwrite existing columns.
- Return empty DataFrame for invalid input or calculation errors handled by function.
- Keep missing numeric values in calculations. Empty input with valid numeric column types keeps its structure and gets new column.
- Use vectorized pandas operations, without Python eval().

## Sales data analysis and cleaning

Input file `sales.csv` contains 1507 rows and 7 columns. Data analysis commands are saved in `data_analysis.txt`.

| Problem | Rows affected | Solution |
| --- | ---: | --- |
| Column names with spaces and different case | Schema: 7 columns | Convert names to snake_case. |
| TOTAL summary row | 1 | Remove because it is not order line. |
| Repeated header inside data | 1 | Remove because it is not order line. |
| Exact duplicate rows | 5 extra rows (10 rows involved) | Keep first occurrence. |
| Empty discount | 963 (959 after duplicate removal) | Replace with 0. Empty discount means no discount. |
| Missing unit price in order lines | 4 | Fill using unique known price for same product. |
| Thousands separator in quantity | 4 | Remove spaces and convert to number. |
| Decimal comma in unit price | 7 | Replace comma with dot and convert to number. |
| Extra spaces in region | 8 | Use strip(). |
| Different letter case in region | 10 | Use title(). |
| Negative quantity | 6 | Keep as possible product returns. |
| Missing region, product and order date in TOTAL row | 1 | Already removed with TOTAL row. |

15 rows have inconsistent region names in total (3 rows have both extra spaces and different letter case).
Raw file has 5 missing unit prices, including TOTAL row. Four missing prices in actual order lines can be recovered.
No invalid order IDs or dates found after removing technical rows. Convert dates to datetime.
No extra spaces found in product names.

Counts are based on raw data or order lines before duplicate removal, as described above. Some problems affect same rows, so counts should not be added together.

## Pipeline assumptions

- Treat exact duplicate rows as export errors. Do not remove rows based only on order ID, because one order can have multiple order lines.
- Assume missing unit price is same as other observed prices for same product. Fill only when product has one unique known price. All 8 products in input have one known price each. Recover 2 prices for Printer paper (21.00) and 2 prices for Keyboard (89.00).
- Treat negative quantity as possible return. Keep negative quantity and use same revenue formula.
- Discount is amount for whole order line, not percentage or discount per item.
- Stop pipeline if missing values remain after cleaning or if invalid infinite values, negative unit price or negative discount are found.
- Use float calculations and round regional totals to 2 decimal places. Currency is not specified in input.

Revenue formula:

```text
revenue = quantity * unit_price - discount
```

Use `add_virtual_column` from `solution.py` to calculate revenue. Group by region and sum revenue. Save result without DataFrame index.

## Pipeline result

1507 input rows - 2 technical rows - 5 duplicate rows = 1500 order lines after cleaning. No other order lines removed.

| Region | Revenue |
| --- | ---: |
| Central | 515824.67 |
| East | 442219.91 |
| North | 665897.52 |
| South | 504036.04 |
| West | 442268.89 |
| **Total** | **2570247.03** |

## Project files

- `solution.py` - virtual column function
- `pipeline.py` - data cleaning and revenue calculation
- `sales.csv` - original input data
- `revenue_by_region.csv` - pipeline output
- `test_virtual_column.py` - original tests
- `test_solution.py` - additional function tests
- `test_pipeline.py` - unit and integration tests for pipeline
- `data_analysis.txt` - data analysis commands and findings
- `requirements.txt` - Python dependencies
- `.gitignore` - exclude virtual environment and cache files
- `README.md` - project documentation
