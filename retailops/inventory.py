"""
RetailOps inventory analytics module.

Provides functions for analyzing inventory data, including stock valuation,
reorder calculations, stock status assignment, and summary generation.
"""

import csv
import os
import sys


# Stock status constants
OUT_OF_STOCK = "OUT_OF_STOCK"
LOW_STOCK = "LOW_STOCK"
OK = "OK"


def calculate_inventory_value(item):
    """
    Calculate the total inventory value for a single item.

    Args:
        item: Dict containing 'current_stock' and 'unit_cost'.

    Returns:
        Total value as float (current_stock * unit_cost).
    """
    stock = int(item.get("current_stock", 0))
    cost = float(item.get("unit_cost", 0.0))
    return stock * cost


def calculate_reorder_quantity(item):
    """
    Calculate the recommended reorder quantity for an item.

    Reorder quantity is defined as (reorder_point * 2) - current_stock,
    but at least reorder_point.

    Args:
        item: Dict containing 'current_stock' and 'reorder_point'.

    Returns:
        Recommended reorder quantity as int.
    """
    stock = int(item.get("current_stock", 0))
    reorder_point = int(item.get("reorder_point", 0))
    suggested = (reorder_point * 2) - stock
    return max(suggested, reorder_point)


def calculate_days_of_stock_left(item, daily_demand=5):
    """
    Calculate estimated days of stock remaining.

    Args:
        item: Dict containing 'current_stock'.
        daily_demand: Estimated daily demand rate (default 5).

    Returns:
        Estimated days of stock remaining, or 0 if no stock.
    """
    stock = int(item.get("current_stock", 0))
    if stock <= 0:
        return 0
    return stock // daily_demand


def assign_stock_status(item):
    """
    Assign a stock status string based on current stock quantity.

    Status rules:
        OUT_OF_STOCK: current_stock == 0
        LOW_STOCK: current_stock <= reorder_point
        OK: current_stock > reorder_point

    Args:
        item: Dict containing 'current_stock' and 'reorder_point'.

    Returns:
        One of OUT_OF_STOCK, LOW_STOCK, OK.
    """
    stock = int(item.get("current_stock", 0))
    reorder_point = int(item.get("reorder_point", 0))

    if stock == 0:
        return OUT_OF_STOCK
    elif stock <= reorder_point:
        return LOW_STOCK
    else:
        return OK


def enrich_inventory_item(item):
    """
    Enrich a single inventory item with calculated fields.

    Adds:
        - inventory_value: total value
        - reorder_quantity: recommended reorder
        - days_of_stock: estimated days remaining
        - stock_status: string status

    Args:
        item: Raw inventory record dict.

    Returns:
        Enriched dict with calculated fields.
    """
    enriched = dict(item)
    enriched["inventory_value"] = calculate_inventory_value(item)
    enriched["reorder_quantity"] = calculate_reorder_quantity(item)
    enriched["days_of_stock"] = calculate_days_of_stock_left(item)
    enriched["stock_status"] = assign_stock_status(item)
    return enriched


def enrich_inventory_items(items):
    """
    Enrich a list of inventory items.

    Args:
        items: List of raw inventory record dicts.

    Returns:
        List of enriched inventory dicts.
    """
    return [enrich_inventory_item(item) for item in items]


def summarize_inventory_by_category(items):
    """
    Summarize inventory data grouped by category.

    Args:
        items: List of enriched inventory dicts.

    Returns:
        Dict mapping category -> {
            'item_count', 'total_stock', 'total_value',
            'low_stock_count', 'out_of_stock_count'
        }
    """
    summary = {}
    for item in items:
        category = item.get("category", "Unknown")
        if category not in summary:
            summary[category] = {
                "item_count": 0,
                "total_stock": 0,
                "total_value": 0.0,
                "low_stock_count": 0,
                "out_of_stock_count": 0,
            }
        summary[category]["item_count"] += 1
        summary[category]["total_stock"] += int(item.get("current_stock", 0))
        summary[category]["total_value"] += float(item.get("inventory_value", 0))
        status = item.get("stock_status", OK)
        if status == LOW_STOCK:
            summary[category]["low_stock_count"] += 1
        elif status == OUT_OF_STOCK:
            summary[category]["out_of_stock_count"] += 1

    return summary


def find_top_reorder_item(items):
    """
    Find the item with the highest reorder quantity.

    Args:
        items: List of enriched inventory dicts.

    Returns:
        The item dict with highest reorder_quantity, or None.
    """
    if not items:
        return None
    return max(items, key=lambda x: int(x.get("reorder_quantity", 0)))


def find_top_inventory_category(category_summary):
    """
    Find the category with the highest total inventory value.

    Args:
        category_summary: Dict from summarize_inventory_by_category().

    Returns:
        Tuple of (category_name, category_data) or None.
    """
    if not category_summary:
        return None
    return max(category_summary.items(), key=lambda x: x[1]["total_value"])


def build_inventory_summary(items):
    """
    Build a comprehensive inventory summary dict.

    Args:
        items: List of raw inventory record dicts.

    Returns:
        Dict containing:
        - total_items
        - total_stock
        - total_value
        - low_stock_count
        - out_of_stock_count
        - average_stock_per_item
        - average_value_per_item
        - category_summary
        - top_reorder_item
        - top_category
    """
    enriched = enrich_inventory_items(items)

    total_items = len(enriched)
    total_stock = sum(int(i.get("current_stock", 0)) for i in enriched)
    total_value = sum(float(i.get("inventory_value", 0)) for i in enriched)

    low_stock_count = sum(
        1 for i in enriched if i.get("stock_status") == LOW_STOCK
    )
    out_of_stock_count = sum(
        1 for i in enriched if i.get("stock_status") == OUT_OF_STOCK
    )

    average_stock_per_item = total_stock / total_items if total_items > 0 else 0
    average_value_per_item = total_value / total_items if total_items > 0 else 0.0

    category_summary = summarize_inventory_by_category(enriched)
    top_reorder_item = find_top_reorder_item(enriched)
    top_category = find_top_inventory_category(category_summary)

    return {
        "total_items": total_items,
        "total_stock": total_stock,
        "total_value": total_value,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "average_stock_per_item": average_stock_per_item,
        "average_value_per_item": average_value_per_item,
        "category_summary": category_summary,
        "top_reorder_item": top_reorder_item,
        "top_category": top_category,
    }


def print_inventory_summary(summary):
    """
    Print a formatted inventory summary to stdout.

    Args:
        summary: Dict from build_inventory_summary().
    """
    print("=" * 60)
    print("INVENTORY ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Items:           {summary['total_items']}")
    print(f"Total Stock Units:     {summary['total_stock']:,}")
    print(f"Total Inventory Value: ${summary['total_value']:,.2f}")
    print(f"Average Stock/Item:    {summary['average_stock_per_item']:.1f}")
    print(f"Average Value/Item:    ${summary['average_value_per_item']:,.2f}")
    print(f"Low Stock Items:       {summary['low_stock_count']}")
    print(f"Out of Stock Items:    {summary['out_of_stock_count']}")
    print()

    print("--- Category Summary ---")
    cat = summary["category_summary"]
    for cat_name in sorted(cat.keys()):
        data = cat[cat_name]
        print(f"  {cat_name}:")
        print(f"    Items: {data['item_count']}, Stock: {data['total_stock']}, "
              f"Value: ${data['total_value']:,.2f}")
        print(f"    Low Stock: {data['low_stock_count']}, "
              f"Out of Stock: {data['out_of_stock_count']}")

    print()
    top_cat = summary["top_category"]
    if top_cat:
        print(f"Top Category: {top_cat[0]} "
              f"(${top_cat[1]['total_value']:,.2f})")

    top_reorder = summary["top_reorder_item"]
    if top_reorder:
        print(f"Top Reorder Item: {top_reorder.get('product_name', 'N/A')} "
              f"(qty: {top_reorder.get('reorder_quantity', 0)})")

    print("=" * 60)


def load_inventory_from_csv(filepath):
    """
    Load inventory data from a CSV file.

    Args:
        filepath: Path to inventory CSV file.

    Returns:
        List of inventory record dicts.
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    items = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)

    if not items:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    return items


def main():
    """Main entry point when run as a script."""
    examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
    filepath = os.path.abspath(os.path.join(examples_dir, "inventory.csv"))

    print(f"Loading inventory data from: {filepath}")
    items = load_inventory_from_csv(filepath)
    print(f"Loaded {len(items)} item(s).")
    print()

    summary = build_inventory_summary(items)
    print_inventory_summary(summary)


if __name__ == "__main__":
    main()