import re
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_bool_dtype


def is_valid_label(label: str) -> bool:
    return isinstance(label, str) and bool(re.fullmatch(r"[A-Za-z_]+", label))


def parse_role(role: str, df: pd.DataFrame):

    if not isinstance(role, str):
        return None

    pattern = r"\s*[A-Za-z_]+(?:\s*[+*-]\s*[A-Za-z_]+)+\s*"

    if not re.fullmatch(pattern, role):
        return None

    tokens = re.findall(r"[A-Za-z_]+|[+*-]", role)

    columns = tokens[::2]

    if not all(col in df.columns for col in columns):
        return None

    return tokens


def calculate_role(df: pd.DataFrame, tokens: list[str]) -> pd.Series:

    terms = []
    operators = []

    current_term = df[tokens[0]]

    # Multiplication 1st
    for i in range(1, len(tokens), 2):
        operator = tokens[i]
        next_column = df[tokens[i + 1]]

        if operator == "*":
            current_term = current_term * next_column
        else:
            terms.append(current_term)
            operators.append(operator)
            current_term = next_column

    terms.append(current_term)

    # Summing up and subtraction
    result = terms[0]

    for operator, term in zip(operators, terms[1:]):
        if operator == "+":
            result = result + term
        elif operator == "-":
            result = result - term

    return result

def add_virtual_column(df: pd.DataFrame, role: str, new_column: str) -> pd.DataFrame:

    """
    Add calculated column to a pandas DataFrame
    Returns:
        New DataFrame with the calculated column,
        or an empty DataFrame if validation fails
    """

    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()

    # Validate column names
    if not is_valid_label(new_column):
        return pd.DataFrame()

    if not all(is_valid_label(col) for col in df.columns):
        return pd.DataFrame()

    if not df.columns.is_unique:
        return pd.DataFrame()

    if new_column in df.columns:
        return pd.DataFrame()

    # Validate mathematical expression
    tokens = parse_role(role, df)

    if tokens is None:
        return pd.DataFrame()

    # Validate numeric columns
    for col in tokens[::2]:
        if not is_numeric_dtype(df[col]) or is_bool_dtype(df[col]):
            return pd.DataFrame()

    # Calculate new column
    try:
        result = df.copy()
        result[new_column] = calculate_role(df, tokens)
        return result

    except (TypeError, ValueError, ArithmeticError):
        return pd.DataFrame()