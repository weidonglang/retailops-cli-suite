"""
RetailOps CLI Suite - Main Command-Line Entrypoint.

Provides a unified command-line interface for all retail analytics modules.
Supports sales, inventory, customers, returns, stores, revenue analysis,
report generation, and data validation.

Usage:
    python -m retailops.cli sales <file>
    python -m retailops.cli inventory <file>
    python -m retailops.cli customers <customers_file> <orders_file>
    python -m retailops.cli returns <returns_file> <orders_file>
    python -m retailops.cli stores <stores_file> <sales_file>
    python -m retailops.cli revenue <file>
    python -m retailops.cli report --output <path>
    python -m retailops.cli validate <file>
"""

import argparse
import sys
import os

from retailops.errors import RetailOpsError, DataValidationError, FileLoadError
from retailops.data_loader import (
    load_sales, load_inventory, load_customers, load_orders,
    load_returns, load_stores, load_monthly_revenue, read_csv_rows,
)
from retailops.validators import (
    validate_sales_record, validate_inventory_record,
    validate_customer_record, validate_order_record,
    validate_return_record, validate_store_record,
    validate_monthly_revenue_record,
)
from retailops.sales import (
    calculate_total_revenue, calculate_total_quantity,
    calculate_average_order_revenue, group_revenue_by_product,
    group_revenue_by_category, group_revenue_by_store,
    find_top_group, build_sales_summary, print_sales_summary,
)
from retailops.inventory import (
    enrich_inventory_items, summarize_inventory_by_category,
    find_top_reorder_item, find_top_inventory_category,
    build_inventory_summary, print_inventory_summary,
)
from retailops.customers import (
    calculate_customer_order_counts, calculate_customer_revenue,
    assign_customer_segment, build_customer_profiles,
    summarize_segments, find_top_customers, build_customer_summary,
    print_customer_summary,
)
from retailops.returns import (
    calculate_return_count, calculate_return_amount,
    group_returns_by_reason, group_returns_by_product,
    calculate_return_rate, find_top_return_reason,
    find_top_return_product, build_returns_summary,
    print_returns_summary,
)
from retailops.stores import (
    group_revenue_by_store, join_store_metadata,
    calculate_average_revenue_per_store, find_top_store,
    find_lowest_store, build_store_summary, print_store_summary,
)
from retailops.revenue import (
    aggregate_monthly_revenue, calculate_total_monthly_revenue,
    calculate_average_monthly_revenue, calculate_growth_rates,
    calculate_moving_average, find_best_month, find_worst_month,
    build_revenue_summary, print_revenue_summary,
)
from retailops.report_builder import (
    build_sales_section, build_inventory_section,
    build_customer_section, build_returns_section,
    build_stores_section, build_revenue_section,
    build_full_report, write_report,
)


def cmd_sales(args):
    """Run sales analytics on a sales/orders CSV file."""
    try:
        orders = load_sales(args.file)
        summary = build_sales_summary(orders)
        print_sales_summary(summary)
        return 0
    except (FileLoadError, DataValidationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_inventory(args):
    """Run inventory analytics on an inventory CSV file."""
    try:
        items = load_inventory(args.file)
        summary = build_inventory_summary(items)
        print_inventory_summary(summary)
        return 0
    except (FileLoadError, DataValidationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_customers(args):
    """Run customer analytics on customers and orders CSV files."""
    try:
        customers = load_customers(args.customers_file)
        orders = load_orders(args.orders_file)
        summary = build_customer_summary(customers, orders)
        print_customer_summary(summary)
        return 0
    except (FileLoadError, DataValidationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_returns(args):
    """Run returns analytics on returns and orders CSV files."""
    try:
        returns = load_returns(args.returns_file)
        orders = load_orders(args.orders_file)
        summary = build_returns_summary(returns, orders)
        print_returns_summary(summary)
        return 0
    except (FileLoadError, DataValidationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_stores(args):
    """Run store analytics on stores and sales CSV files."""
    try:
        stores = load_stores(args.stores_file)
        sales = load_sales(args.sales_file)
        summary = build_store_summary(stores, sales)
        print_store_summary(summary)
        return 0
    except (FileLoadError, DataValidationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_revenue(args):
    """Run revenue trend analytics on a monthly revenue CSV file."""
    try:
        rows = load_monthly_revenue(args.file)
        summary = build_revenue_summary(rows)
        print_revenue_summary(summary)
        return 0
    except (FileLoadError, DataValidationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_report(args):
    """Generate a full Markdown analytics report."""
    examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
    try:
        print("Loading example data...")
        sales_data = load_sales(os.path.join(examples_dir, "sales.csv"))
        inventory_data = load_inventory(os.path.join(examples_dir, "inventory.csv"))
        customers_data = load_customers(os.path.join(examples_dir, "customers.csv"))
        orders_data = load_orders(os.path.join(examples_dir, "orders.csv"))
        returns_data = load_returns(os.path.join(examples_dir, "returns.csv"))
        stores_data = load_stores(os.path.join(examples_dir, "stores.csv"))
        revenue_data = load_monthly_revenue(os.path.join(examples_dir, "monthly_revenue.csv"))

        print("Building analytics summaries...")
        sales_summary = build_sales_summary(orders_data)
        inventory_summary = build_inventory_summary(inventory_data)
        customer_summary = build_customer_summary(customers_data, orders_data)
        returns_summary = build_returns_summary(returns_data, orders_data)
        store_summary = build_store_summary(stores_data, sales_data)
        revenue_summary = build_revenue_summary(revenue_data)

        sections = {
            "sales": build_sales_section(sales_summary),
            "inventory": build_inventory_section(inventory_summary),
            "customers": build_customer_section(customer_summary),
            "returns": build_returns_section(returns_summary),
            "stores": build_stores_section(store_summary),
            "revenue": build_revenue_section(revenue_summary),
        }

        print("Generating Markdown report...")
        report = build_full_report(sections)

        output_path = args.output
        if not output_path:
            reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
            os.makedirs(reports_dir, exist_ok=True)
            output_path = os.path.join(reports_dir, "generated_report.md")

        write_report(report, output_path)
        print("Report generated successfully.")
        return 0
    except (FileLoadError, DataValidationError, RetailOpsError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def _detect_csv_type(columns):
    """
    Detect the CSV file type based on its column headers.

    Args:
        columns: Set of column names from the CSV header.

    Returns:
        String identifier for the detected type, or None if unknown.
    """
    col_set = set(columns)

    # sales.csv: order_id, customer_id, store_id, product_id, product_name, category, quantity, unit_price, order_date, total_amount
    if col_set >= {"product_name", "total_amount", "category", "order_id"}:
        return "sales"
    # inventory.csv: product_id, product_name, category, current_stock, reorder_point, unit_cost, supplier
    if col_set >= {"current_stock", "reorder_point", "unit_cost", "supplier"}:
        return "inventory"
    # customers.csv: customer_id, name, email, city, signup_date
    if col_set >= {"name", "email", "city", "signup_date", "customer_id"}:
        return "customer"
    # orders.csv: order_id, customer_id, store_id, product_id, quantity, unit_price, order_date
    if col_set >= {"order_id", "customer_id", "store_id", "product_id", "quantity", "unit_price", "order_date"}:
        return "order"
    # returns.csv: return_id, order_id, product_id, quantity, return_amount, return_reason, return_date
    if col_set >= {"return_id", "return_amount", "return_reason", "return_date"}:
        return "return"
    # stores.csv: store_id, store_name, city, state, manager, open_date, size_sqft
    if col_set >= {"store_id", "store_name", "manager", "size_sqft"}:
        return "store"
    # monthly_revenue.csv: year, month, store_id, total_revenue, total_orders
    if col_set >= {"year", "month", "total_revenue", "total_orders"}:
        return "monthly_revenue"

    return None


def _get_validator(csv_type):
    """
    Get the appropriate record validator for a CSV type.

    Args:
        csv_type: String identifier from _detect_csv_type().

    Returns:
        Validator function, or None if unknown type.
    """
    validators = {
        "sales": validate_sales_record,
        "inventory": validate_inventory_record,
        "customer": validate_customer_record,
        "order": validate_order_record,
        "return": validate_return_record,
        "store": validate_store_record,
        "monthly_revenue": validate_monthly_revenue_record,
    }
    return validators.get(csv_type)


def cmd_validate(args):
    """
    Validate a CSV file against expected schema.

    Automatically detects the CSV type by column headers and applies
    the corresponding record validator.
    """
    try:
        rows = read_csv_rows(args.file)
        if not rows:
            print(f"Error: File is empty: {args.file}", file=sys.stderr)
            return 1

        columns = list(rows[0].keys())
        csv_type = _detect_csv_type(columns)
        validator_fn = _get_validator(csv_type) if csv_type else None

        print(f"Validating file: {args.file}")
        print(f"Detected type: {csv_type if csv_type else 'unknown'}")
        print(f"Total rows: {len(rows)}")
        print(f"Total columns: {len(columns)}")
        print(f"Columns: {', '.join(columns)}")
        print()

        if not validator_fn:
            print("Warning: Unknown CSV schema. No specific validation available.", file=sys.stderr)
            print(f"Found {len(rows)} rows with {len(columns)} columns.")
            return 0

        errors_found = 0
        for i, row in enumerate(rows, 1):
            try:
                validator_fn(row)
            except DataValidationError as e:
                print(f"  Row {i}: {e}")
                errors_found += 1

        if errors_found == 0:
            print("All rows are valid.")
        else:
            print(f"Found {errors_found} row(s) with validation errors.")

        return 0 if errors_found == 0 else 1
    except FileNotFoundError as e:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1
    except DataValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="retailops",
        description="RetailOps CLI Suite - A multi-language retail operations "
                    "CLI toolkit with analytics, tests, Windows executables, "
                    "and release packaging.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m retailops.cli sales examples/sales.csv\n"
            "  python -m retailops.cli inventory examples/inventory.csv\n"
            "  python -m retailops.cli report --output reports/my_report.md\n"
        ),
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # sales command
    sales_parser = subparsers.add_parser("sales", help="Analyze sales data")
    sales_parser.add_argument("file", help="Path to sales/orders CSV file")
    sales_parser.set_defaults(func=cmd_sales)

    # inventory command
    inv_parser = subparsers.add_parser("inventory", help="Analyze inventory data")
    inv_parser.add_argument("file", help="Path to inventory CSV file")
    inv_parser.set_defaults(func=cmd_inventory)

    # customers command
    cust_parser = subparsers.add_parser("customers", help="Analyze customer data")
    cust_parser.add_argument("customers_file", help="Path to customers CSV file")
    cust_parser.add_argument("orders_file", help="Path to orders CSV file")
    cust_parser.set_defaults(func=cmd_customers)

    # returns command
    ret_parser = subparsers.add_parser("returns", help="Analyze returns data")
    ret_parser.add_argument("returns_file", help="Path to returns CSV file")
    ret_parser.add_argument("orders_file", help="Path to orders CSV file (for return rate)")
    ret_parser.set_defaults(func=cmd_returns)

    # stores command
    store_parser = subparsers.add_parser("stores", help="Analyze store performance")
    store_parser.add_argument("stores_file", help="Path to stores CSV file")
    store_parser.add_argument("sales_file", help="Path to sales CSV file")
    store_parser.set_defaults(func=cmd_stores)

    # revenue command
    rev_parser = subparsers.add_parser("revenue", help="Analyze monthly revenue trends")
    rev_parser.add_argument("file", help="Path to monthly revenue CSV file")
    rev_parser.set_defaults(func=cmd_revenue)

    # report command
    report_parser = subparsers.add_parser("report", help="Generate full Markdown analytics report")
    report_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output path for the generated report (default: reports/generated_report.md)",
    )
    report_parser.set_defaults(func=cmd_report)

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a CSV file format")
    validate_parser.add_argument("file", help="Path to CSV file to validate")
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main():
    """Main entry point: parse arguments and execute the appropriate command."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    try:
        exit_code = args.func(args)
        sys.exit(exit_code)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except FileLoadError as e:
        print(f"File load error: {e}", file=sys.stderr)
        sys.exit(1)
    except DataValidationError as e:
        print(f"Data validation error: {e}", file=sys.stderr)
        sys.exit(1)
    except RetailOpsError as e:
        print(f"RetailOps error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()