"""
RetailOps data validation utilities.

Provides field-level validators and record-level validators for all
RetailOps CSV data types. All validators use only the Python standard
library and raise DataValidationError on failure.
"""

import re

from retailops.errors import DataValidationError


def validate_non_empty(value, field_name):
    """
    Validate that a string value is not None and not empty after stripping.

    Args:
        value: The string value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The stripped non-empty string.

    Raises:
        DataValidationError: If value is None, empty, or only whitespace.
    """
    if value is None:
        raise DataValidationError(f"Field '{field_name}' is missing (None).")
    stripped = value.strip()
    if not stripped:
        raise DataValidationError(f"Field '{field_name}' is empty.")
    return stripped


def parse_int(value, field_name):
    """
    Parse and return an integer from a string value.

    Args:
        value: String representation of an integer.
        field_name: Name of the field for error messages.

    Returns:
        The parsed integer value.

    Raises:
        DataValidationError: If value cannot be parsed as an integer.
    """
    if value is None:
        raise DataValidationError(f"Field '{field_name}' is missing (None), expected integer.")
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        raise DataValidationError(
            f"Field '{field_name}' value '{value}' is not a valid integer."
        )


def parse_float(value, field_name):
    """
    Parse and return a float from a string value.

    Args:
        value: String representation of a float.
        field_name: Name of the field for error messages.

    Returns:
        The parsed float value.

    Raises:
        DataValidationError: If value cannot be parsed as a float.
    """
    if value is None:
        raise DataValidationError(f"Field '{field_name}' is missing (None), expected float.")
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        raise DataValidationError(
            f"Field '{field_name}' value '{value}' is not a valid number."
        )


def parse_date(value, field_name):
    """
    Parse and return a date string in YYYY-MM-DD format.

    Validates that the date string follows the YYYY-MM-DD pattern and
    represents a valid calendar date.

    Args:
        value: Date string in YYYY-MM-DD format.
        field_name: Name of the field for error messages.

    Returns:
        The validated date string.

    Raises:
        DataValidationError: If value is not a valid YYYY-MM-DD date.
    """
    if value is None:
        raise DataValidationError(f"Field '{field_name}' is missing (None), expected date.")
    date_str = str(value).strip()

    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, date_str):
        raise DataValidationError(
            f"Field '{field_name}' value '{date_str}' is not in YYYY-MM-DD format."
        )

    parts = date_str.split("-")
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    if month < 1 or month > 12:
        raise DataValidationError(
            f"Field '{field_name}' value '{date_str}' has invalid month {month}."
        )

    if day < 1 or day > 31:
        raise DataValidationError(
            f"Field '{field_name}' value '{date_str}' has invalid day {day}."
        )

    if month == 2:
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            max_day = 29
        else:
            max_day = 28
        if day > max_day:
            raise DataValidationError(
                f"Field '{field_name}' value '{date_str}' has invalid day {day} "
                f"for February {year}."
            )
    elif month in (4, 6, 9, 11) and day > 30:
        raise DataValidationError(
            f"Field '{field_name}' value '{date_str}' has invalid day {day} "
            f"for month {month}."
        )

    return date_str


def validate_positive_int(value, field_name):
    """
    Validate that a value is a positive integer (> 0).

    Args:
        value: String or int to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated positive integer.

    Raises:
        DataValidationError: If value is not a positive integer.
    """
    parsed = parse_int(value, field_name)
    if parsed <= 0:
        raise DataValidationError(
            f"Field '{field_name}' value '{parsed}' is not a positive integer."
        )
    return parsed


def validate_non_negative_int(value, field_name):
    """
    Validate that a value is a non-negative integer (>= 0).

    Args:
        value: String or int to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated non-negative integer.

    Raises:
        DataValidationError: If value is not a non-negative integer.
    """
    parsed = parse_int(value, field_name)
    if parsed < 0:
        raise DataValidationError(
            f"Field '{field_name}' value '{parsed}' is negative."
        )
    return parsed


def validate_non_negative_float(value, field_name):
    """
    Validate that a value is a non-negative float (>= 0.0).

    Args:
        value: String or float to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated non-negative float.

    Raises:
        DataValidationError: If value is not a non-negative float.
    """
    parsed = parse_float(value, field_name)
    if parsed < 0.0:
        raise DataValidationError(
            f"Field '{field_name}' value '{parsed}' is negative."
        )
    return parsed


def validate_sales_record(record):
    """
    Validate and clean a single sales record.

    Args:
        record: Dict representing a sales/orders row.

    Returns:
        Cleaned dict with parsed numeric fields.

    Raises:
        DataValidationError: If any field fails validation.
    """
    cleaned = {}
    cleaned["order_id"] = validate_non_empty(record.get("order_id", ""), "order_id")
    cleaned["customer_id"] = validate_non_empty(record.get("customer_id", ""), "customer_id")
    cleaned["store_id"] = validate_non_empty(record.get("store_id", ""), "store_id")
    cleaned["product_id"] = validate_non_empty(record.get("product_id", ""), "product_id")
    cleaned["product_name"] = validate_non_empty(record.get("product_name", ""), "product_name")
    cleaned["category"] = validate_non_empty(record.get("category", ""), "category")
    cleaned["quantity"] = validate_positive_int(record.get("quantity", ""), "quantity")
    cleaned["unit_price"] = validate_non_negative_float(record.get("unit_price", ""), "unit_price")
    cleaned["order_date"] = parse_date(record.get("order_date", ""), "order_date")
    cleaned["total_amount"] = parse_float(record.get("total_amount", ""), "total_amount")
    return cleaned


def validate_inventory_record(record):
    """
    Validate and clean a single inventory record.

    Args:
        record: Dict representing an inventory row.

    Returns:
        Cleaned dict with parsed numeric fields.

    Raises:
        DataValidationError: If any field fails validation.
    """
    cleaned = {}
    cleaned["product_id"] = validate_non_empty(record.get("product_id", ""), "product_id")
    cleaned["product_name"] = validate_non_empty(record.get("product_name", ""), "product_name")
    cleaned["category"] = validate_non_empty(record.get("category", ""), "category")
    cleaned["current_stock"] = validate_non_negative_int(
        record.get("current_stock", ""), "current_stock"
    )
    cleaned["reorder_point"] = validate_non_negative_int(
        record.get("reorder_point", ""), "reorder_point"
    )
    cleaned["unit_cost"] = validate_non_negative_float(
        record.get("unit_cost", ""), "unit_cost"
    )
    cleaned["supplier"] = validate_non_empty(record.get("supplier", ""), "supplier")
    return cleaned


def validate_customer_record(record):
    """
    Validate and clean a single customer record.

    Args:
        record: Dict representing a customer row.

    Returns:
        Cleaned dict with parsed fields.

    Raises:
        DataValidationError: If any field fails validation.
    """
    cleaned = {}
    cleaned["customer_id"] = validate_non_empty(record.get("customer_id", ""), "customer_id")
    cleaned["name"] = validate_non_empty(record.get("name", ""), "name")
    cleaned["email"] = validate_non_empty(record.get("email", ""), "email")
    cleaned["city"] = validate_non_empty(record.get("city", ""), "city")
    cleaned["signup_date"] = parse_date(record.get("signup_date", ""), "signup_date")
    return cleaned


def validate_order_record(record):
    """
    Validate and clean a single order record.

    Args:
        record: Dict representing an order row.

    Returns:
        Cleaned dict with parsed numeric fields.

    Raises:
        DataValidationError: If any field fails validation.
    """
    cleaned = {}
    cleaned["order_id"] = validate_non_empty(record.get("order_id", ""), "order_id")
    cleaned["customer_id"] = validate_non_empty(record.get("customer_id", ""), "customer_id")
    cleaned["store_id"] = validate_non_empty(record.get("store_id", ""), "store_id")
    cleaned["product_id"] = validate_non_empty(record.get("product_id", ""), "product_id")
    cleaned["quantity"] = validate_positive_int(record.get("quantity", ""), "quantity")
    cleaned["unit_price"] = validate_non_negative_float(
        record.get("unit_price", ""), "unit_price"
    )
    cleaned["order_date"] = parse_date(record.get("order_date", ""), "order_date")
    return cleaned


def validate_return_record(record):
    """
    Validate and clean a single return record.

    Args:
        record: Dict representing a return row.

    Returns:
        Cleaned dict with parsed numeric fields.

    Raises:
        DataValidationError: If any field fails validation.
    """
    cleaned = {}
    cleaned["return_id"] = validate_non_empty(record.get("return_id", ""), "return_id")
    cleaned["order_id"] = validate_non_empty(record.get("order_id", ""), "order_id")
    cleaned["product_id"] = validate_non_empty(record.get("product_id", ""), "product_id")
    cleaned["quantity"] = validate_positive_int(record.get("quantity", ""), "quantity")
    cleaned["return_amount"] = validate_non_negative_float(
        record.get("return_amount", ""), "return_amount"
    )
    cleaned["return_reason"] = validate_non_empty(
        record.get("return_reason", ""), "return_reason"
    )
    cleaned["return_date"] = parse_date(record.get("return_date", ""), "return_date")
    return cleaned


def validate_store_record(record):
    """
    Validate and clean a single store record.

    Args:
        record: Dict representing a store row.

    Returns:
        Cleaned dict with parsed fields.

    Raises:
        DataValidationError: If any field fails validation.
    """
    cleaned = {}
    cleaned["store_id"] = validate_non_empty(record.get("store_id", ""), "store_id")
    cleaned["store_name"] = validate_non_empty(record.get("store_name", ""), "store_name")
    cleaned["city"] = validate_non_empty(record.get("city", ""), "city")
    cleaned["state"] = validate_non_empty(record.get("state", ""), "state")
    cleaned["manager"] = validate_non_empty(record.get("manager", ""), "manager")
    cleaned["open_date"] = parse_date(record.get("open_date", ""), "open_date")
    cleaned["size_sqft"] = validate_positive_int(
        record.get("size_sqft", ""), "size_sqft"
    )
    return cleaned


def validate_monthly_revenue_record(record):
    """
    Validate and clean a single monthly revenue record.

    Args:
        record: Dict representing a monthly revenue row.

    Returns:
        Cleaned dict with parsed numeric fields.

    Raises:
        DataValidationError: If any field fails validation.
    """
    cleaned = {}
    cleaned["year"] = validate_positive_int(record.get("year", ""), "year")
    cleaned["month"] = validate_positive_int(record.get("month", ""), "month")
    cleaned["store_id"] = validate_non_empty(record.get("store_id", ""), "store_id")
    cleaned["total_revenue"] = validate_non_negative_float(
        record.get("total_revenue", ""), "total_revenue"
    )
    cleaned["total_orders"] = validate_non_negative_int(
        record.get("total_orders", ""), "total_orders"
    )

    if cleaned["month"] < 1 or cleaned["month"] > 12:
        raise DataValidationError(
            f"Field 'month' value '{cleaned['month']}' is not between 1 and 12."
        )
    return cleaned


def _run_self_test():
    """Run a self-test demonstrating all validators."""
    import os
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from retailops.data_loader import (
        load_sales, load_inventory, load_customers,
        load_orders, load_returns, load_stores, load_monthly_revenue
    )

    base = os.path.join(os.path.dirname(__file__), "..", "examples")

    print("=" * 60)
    print("RetailOps Validators Self-Test")
    print("=" * 60)

    test_cases = [
        ("sales.csv", load_sales, validate_sales_record, "sales"),
        ("inventory.csv", load_inventory, validate_inventory_record, "inventory"),
        ("customers.csv", load_customers, validate_customer_record, "customer"),
        ("orders.csv", load_orders, validate_order_record, "order"),
        ("returns.csv", load_returns, validate_return_record, "return"),
        ("stores.csv", load_stores, validate_store_record, "store"),
        ("monthly_revenue.csv", load_monthly_revenue, validate_monthly_revenue_record, "revenue"),
    ]

    all_ok = True
    for filename, loader, validator, label in test_cases:
        file_path = os.path.abspath(os.path.join(base, filename))
        try:
            rows = loader(file_path)
            validated = [validator(r) for r in rows]
            print(f"[OK] {label}: validated {len(validated)} record(s)")
        except Exception as e:
            print(f"[FAIL] {label}: {e}")
            all_ok = False

    print("=" * 60)
    if all_ok:
        print("All validators passed.")
    else:
        print("Some validators failed.")
    print("=" * 60)

    test_single_validators()
    return all_ok


def test_single_validators():
    """Test field-level validators with known cases."""
    print()
    print("--- Field Validator Tests ---")

    try:
        result = validate_non_empty("hello", "test")
        assert result == "hello"
        print("[OK] validate_non_empty with valid string")
    except Exception as e:
        print(f"[FAIL] validate_non_empty valid string: {e}")

    try:
        validate_non_empty("", "test")
        print("[FAIL] validate_non_empty empty string should raise")
    except DataValidationError:
        print("[OK] validate_non_empty empty string raises error")

    try:
        result = parse_int("42", "test")
        assert result == 42
        print("[OK] parse_int valid string")
    except Exception as e:
        print(f"[FAIL] parse_int valid string: {e}")

    try:
        parse_int("abc", "test")
        print("[FAIL] parse_int invalid string should raise")
    except DataValidationError:
        print("[OK] parse_int invalid string raises error")

    try:
        result = parse_float("3.14", "test")
        assert abs(result - 3.14) < 0.001
        print("[OK] parse_float valid string")
    except Exception as e:
        print(f"[FAIL] parse_float valid string: {e}")

    try:
        parse_date("2026-01-15", "test")
        print("[OK] parse_date valid date")
    except Exception as e:
        print(f"[FAIL] parse_date valid date: {e}")

    try:
        parse_date("13-01-2026", "test")
        print("[FAIL] parse_date wrong format should raise")
    except DataValidationError:
        print("[OK] parse_date wrong format raises error")

    try:
        validate_positive_int("5", "test")
        print("[OK] validate_positive_int valid")
    except Exception as e:
        print(f"[FAIL] validate_positive_int valid: {e}")

    try:
        validate_positive_int("-1", "test")
        print("[FAIL] validate_positive_int negative should raise")
    except DataValidationError:
        print("[OK] validate_positive_int negative raises error")

    try:
        validate_non_negative_int("0", "test")
        print("[OK] validate_non_negative_int zero")
    except Exception as e:
        print(f"[FAIL] validate_non_negative_int zero: {e}")

    try:
        validate_non_negative_float("0.0", "test")
        print("[OK] validate_non_negative_float zero")
    except Exception as e:
        print(f"[FAIL] validate_non_negative_float zero: {e}")


if __name__ == "__main__":
    _run_self_test()