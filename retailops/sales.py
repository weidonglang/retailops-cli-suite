"""
RetailOps sales analytics module.

Provides functions for analyzing sales/orders data, including revenue
calculations, grouping, top performers, and summary generation.
"""

import csv
import os
import sys


def calculate_order_revenue(order):
    """
    Calculate the revenue for a single order.

    Args:
        order: Dict containing 'total_amount' key.

    Returns:
        Float value of total_amount, or 0.0 if missing/invalid.
    """
    try:
        return float(order.get("total_amount", 0))
    except (ValueError, TypeError):
        return 0.0


def calculate_total_revenue(orders):
    """
    Calculate total revenue across all orders.

    Args:
        orders: List of order dicts.

    Returns:
        Total revenue as float.
    """
    return sum(calculate_order_revenue(o) for o in orders)


def calculate_total_quantity(orders):
    """
    Calculate total quantity of items sold across all orders.

    Args:
        orders: List of order dicts with 'quantity' key.

    Returns:
        Total quantity as int.
    """
    total = 0
    for o in orders:
        try:
            total += int(o.get("quantity", 0))
        except (ValueError, TypeError):
            pass
    return total


def group_revenue_by_product(orders):
    """
    Group total revenue by product.

    Args:
        orders: List of order dicts with 'product_name' and 'total_amount'.

    Returns:
        Dict mapping product_name -> total_revenue.
    """
    groups = {}
    for o in orders:
        product = o.get("product_name", "Unknown")
        revenue = calculate_order_revenue(o)
        groups[product] = groups.get(product, 0.0) + revenue
    return groups


def group_revenue_by_category(orders):
    """
    Group total revenue by product category.

    Args:
        orders: List of order dicts with 'category' and 'total_amount'.

    Returns:
        Dict mapping category -> total_revenue.
    """
    groups = {}
    for o in orders:
        category = o.get("category", "Unknown")
        revenue = calculate_order_revenue(o)
        groups[category] = groups.get(category, 0.0) + revenue
    return groups


def group_revenue_by_store(orders):
    """
    Group total revenue by store.

    Args:
        orders: List of order dicts with 'store_id' and 'total_amount'.

    Returns:
        Dict mapping store_id -> total_revenue.
    """
    groups = {}
    for o in orders:
        store = o.get("store_id", "Unknown")
        revenue = calculate_order_revenue(o)
        groups[store] = groups.get(store, 0.0) + revenue
    return groups


def find_top_group(grouped, limit=5):
    """
    Find the top groups by revenue.

    Args:
        grouped: Dict mapping group_key -> revenue.
        limit: Maximum number of results.

    Returns:
        List of (key, revenue) tuples sorted descending by revenue.
    """
    sorted_groups = sorted(grouped.items(), key=lambda x: x[1], reverse=True)
    return sorted_groups[:limit]


def calculate_average_order_revenue(orders):
    """
    Calculate average revenue per order.

    Args:
        orders: List of order dicts.

    Returns:
        Average revenue as float, or 0.0 if no orders.
    """
    if not orders:
        return 0.0
    return calculate_total_revenue(orders) / len(orders)


def build_sales_summary(orders):
    """
    Build a comprehensive sales summary dict.

    Args:
        orders: List of order dicts.

    Returns:
        Dict containing:
        - total_revenue
        - total_quantity
        - order_count
        - average_revenue
        - top_products (top 5 by revenue)
        - top_categories (top 5 by revenue)
        - top_stores (top 5 by revenue)
    """
    total_revenue = calculate_total_revenue(orders)
    total_quantity = calculate_total_quantity(orders)
    order_count = len(orders)
    average_revenue = calculate_average_order_revenue(orders)

    product_groups = group_revenue_by_product(orders)
    category_groups = group_revenue_by_category(orders)
    store_groups = group_revenue_by_store(orders)

    return {
        "total_revenue": total_revenue,
        "total_quantity": total_quantity,
        "order_count": order_count,
        "average_revenue": average_revenue,
        "top_products": find_top_group(product_groups),
        "top_categories": find_top_group(category_groups),
        "top_stores": find_top_group(store_groups),
    }


def print_sales_summary(summary):
    """
    Print a formatted sales summary to stdout.

    Args:
        summary: Dict from build_sales_summary().
    """
    print("=" * 60)
    print("SALES ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Revenue:      ${summary['total_revenue']:,.2f}")
    print(f"Total Quantity:     {summary['total_quantity']:,}")
    print(f"Order Count:        {summary['order_count']:,}")
    print(f"Average Order Rev:  ${summary['average_revenue']:,.2f}")
    print()

    print("--- Top 5 Products by Revenue ---")
    for i, (product, rev) in enumerate(summary["top_products"], 1):
        print(f"  {i}. {product}: ${rev:,.2f}")
    print()

    print("--- Top 5 Categories by Revenue ---")
    for i, (cat, rev) in enumerate(summary["top_categories"], 1):
        print(f"  {i}. {cat}: ${rev:,.2f}")
    print()

    print("--- Top 5 Stores by Revenue ---")
    for i, (store, rev) in enumerate(summary["top_stores"], 1):
        print(f"  {i}. {store}: ${rev:,.2f}")
    print("=" * 60)


def load_orders_from_csv(filepath):
    """
    Load orders from a CSV file.

    Args:
        filepath: Path to CSV file.

    Returns:
        List of order dicts.
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    orders = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append(row)

    if not orders:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    return orders


def main():
    """Main entry point when run as a script."""
    examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
    filepath = os.path.abspath(os.path.join(examples_dir, "sales.csv"))

    print(f"Loading sales data from: {filepath}")
    orders = load_orders_from_csv(filepath)
    print(f"Loaded {len(orders)} order(s).")
    print()

    summary = build_sales_summary(orders)
    print_sales_summary(summary)


if __name__ == "__main__":
    main()