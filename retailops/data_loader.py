"""
RetailOps data loading utilities.

Provides functions to load and validate CSV data files used throughout
the RetailOps CLI Suite. All loading functions return list of dicts.
"""

import csv
import os
import warnings

from retailops.errors import FileLoadError, DataValidationError
from retailops.validators import (
    validate_sales_record, validate_inventory_record,
    validate_customer_record, validate_order_record,
    validate_return_record, validate_store_record,
    validate_monthly_revenue_record,
)


def read_csv_rows(file_path):
    """
    Read a CSV file and return all rows as list of dicts.

    Args:
        file_path: Path to the CSV file.

    Returns:
        List of dicts with column names as keys.

    Raises:
        FileLoadError: If the file does not exist or cannot be read.
        DataValidationError: If the file is empty.
    """
    if not os.path.exists(file_path):
        raise FileLoadError(f"File not found: {file_path}")

    if not os.path.isfile(file_path):
        raise FileLoadError(f"Path is not a file: {file_path}")

    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
    except PermissionError:
        raise FileLoadError(f"Permission denied reading file: {file_path}")
    except Exception as e:
        raise FileLoadError(f"Failed to read file {file_path}: {e}")

    if not rows:
        raise DataValidationError(f"File is empty or has no data rows: {file_path}")

    return rows


def require_columns(rows, required_columns):
    """
    Verify that all rows contain the required columns.

    Args:
        rows: List of dicts representing CSV rows.
        required_columns: List of column names that must be present.

    Raises:
        DataValidationError: If any required column is missing from a row.
    """
    if not rows:
        raise DataValidationError("Cannot validate columns on empty data.")

    first_row = rows[0]
    for col in required_columns:
        if col not in first_row:
            raise DataValidationError(
                f"Required column '{col}' not found. "
                f"Available columns: {list(first_row.keys())}"
            )


def _validate_rows(rows, validator_fn, record_label):
    """
    Validate all rows using the given validator function.

    Applies the validator to each row. Rows that fail validation
    are skipped with a warning rather than failing the entire load.

    Args:
        rows: List of dict rows to validate.
        validator_fn: A validator function (e.g., validate_sales_record).
        record_label: Label for warning messages (e.g., "sales").

    Returns:
        List of validated (cleaned) dicts.
    """
    validated = []
    for i, row in enumerate(rows, 1):
        try:
            cleaned = validator_fn(row)
            validated.append(cleaned)
        except DataValidationError as e:
            warnings.warn(f"Row {i} in {record_label} data is invalid: {e}")
    if not validated:
        raise DataValidationError(
            f"No valid {record_label} records found after validation."
        )
    return validated


def load_sales(file_path):
    """
    Load and validate sales/orders CSV data.

    Expected columns: order_id, customer_id, store_id, product_id,
    product_name, category, quantity, unit_price, order_date, total_amount.

    Each row is validated via validate_sales_record(). Invalid rows
    produce warnings and are excluded from the result.

    Args:
        file_path: Path to the sales CSV file.

    Returns:
        List of validated dicts representing sales records.
    """
    required = [
        "order_id", "customer_id", "store_id", "product_id",
        "product_name", "category", "quantity", "unit_price",
        "order_date", "total_amount"
    ]
    rows = read_csv_rows(file_path)
    require_columns(rows, required)
    return _validate_rows(rows, validate_sales_record, "sales")


def load_inventory(file_path):
    """
    Load and validate inventory CSV data.

    Expected columns: product_id, product_name, category, current_stock,
    reorder_point, unit_cost, supplier.

    Each row is validated via validate_inventory_record(). Invalid rows
    produce warnings and are excluded from the result.

    Args:
        file_path: Path to the inventory CSV file.

    Returns:
        List of validated dicts representing inventory records.
    """
    required = [
        "product_id", "product_name", "category", "current_stock",
        "reorder_point", "unit_cost", "supplier"
    ]
    rows = read_csv_rows(file_path)
    require_columns(rows, required)
    return _validate_rows(rows, validate_inventory_record, "inventory")


def load_customers(file_path):
    """
    Load and validate customer CSV data.

    Expected columns: customer_id, name, email, city, signup_date.

    Each row is validated via validate_customer_record(). Invalid rows
    produce warnings and are excluded from the result.

    Args:
        file_path: Path to the customers CSV file.

    Returns:
        List of validated dicts representing customer records.
    """
    required = ["customer_id", "name", "email", "city", "signup_date"]
    rows = read_csv_rows(file_path)
    require_columns(rows, required)
    return _validate_rows(rows, validate_customer_record, "customer")


def load_orders(file_path):
    """
    Load and validate orders CSV data.

    Expected columns: order_id, customer_id, store_id, product_id,
    quantity, unit_price, order_date.

    Each row is validated via validate_order_record(). Invalid rows
    produce warnings and are excluded from the result.

    Args:
        file_path: Path to the orders CSV file.

    Returns:
        List of validated dicts representing order records.
    """
    required = [
        "order_id", "customer_id", "store_id", "product_id",
        "quantity", "unit_price", "order_date"
    ]
    rows = read_csv_rows(file_path)
    require_columns(rows, required)
    return _validate_rows(rows, validate_order_record, "order")


def load_returns(file_path):
    """
    Load and validate returns CSV data.

    Expected columns: return_id, order_id, product_id, quantity,
    return_amount, return_reason, return_date.

    Each row is validated via validate_return_record(). Invalid rows
    produce warnings and are excluded from the result.

    Args:
        file_path: Path to the returns CSV file.

    Returns:
        List of validated dicts representing return records.
    """
    required = [
        "return_id", "order_id", "product_id", "quantity",
        "return_amount", "return_reason", "return_date"
    ]
    rows = read_csv_rows(file_path)
    require_columns(rows, required)
    return _validate_rows(rows, validate_return_record, "return")


def load_stores(file_path):
    """
    Load and validate store CSV data.

    Expected columns: store_id, store_name, city, state, manager,
    open_date, size_sqft.

    Each row is validated via validate_store_record(). Invalid rows
    produce warnings and are excluded from the result.

    Args:
        file_path: Path to the stores CSV file.

    Returns:
        List of validated dicts representing store records.
    """
    required = [
        "store_id", "store_name", "city", "state", "manager",
        "open_date", "size_sqft"
    ]
    rows = read_csv_rows(file_path)
    require_columns(rows, required)
    return _validate_rows(rows, validate_store_record, "store")


def load_monthly_revenue(file_path):
    """
    Load and validate monthly revenue CSV data.

    Expected columns: year, month, store_id, total_revenue, total_orders.

    Each row is validated via validate_monthly_revenue_record(). Invalid rows
    produce warnings and are excluded from the result.

    Args:
        file_path: Path to the monthly revenue CSV file.

    Returns:
        List of validated dicts representing monthly revenue records.
    """
    required = ["year", "month", "store_id", "total_revenue", "total_orders"]
    rows = read_csv_rows(file_path)
    require_columns(rows, required)
    return _validate_rows(rows, validate_monthly_revenue_record, "monthly_revenue")


def _print_loader_summary(name, rows):
    """Print a summary of loaded data for self-test output."""
    if rows:
        print(f"[OK] {name}: loaded {len(rows)} record(s)")
        print(f"     Columns: {list(rows[0].keys())}")
    else:
        print(f"[WARN] {name}: loaded 0 records")


if __name__ == "__main__":
    print("=" * 60)
    print("RetailOps Data Loader Self-Test")
    print("=" * 60)

    base = os.path.join(os.path.dirname(__file__), "..", "examples")

    tests = [
        ("sales.csv", load_sales),
        ("inventory.csv", load_inventory),
        ("customers.csv", load_customers),
        ("orders.csv", load_orders),
        ("returns.csv", load_returns),
        ("stores.csv", load_stores),
        ("monthly_revenue.csv", load_monthly_revenue),
    ]

    all_ok = True
    for filename, loader_func in tests:
        file_path = os.path.abspath(os.path.join(base, filename))
        try:
            rows = loader_func(file_path)
            _print_loader_summary(filename, rows)
        except (FileLoadError, DataValidationError) as e:
            print(f"[FAIL] {filename}: {e}")
            all_ok = False

    print("=" * 60)
    if all_ok:
        print("All loaders passed.")
    else:
        print("Some loaders failed.")
    print("=" * 60)