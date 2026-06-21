"""
RetailOps store analytics module.

Provides functions for analyzing store performance data, including revenue
grouping, metadata joining, performance ranking, and summary generation.
"""

import csv
import os
import sys


def group_revenue_by_store(sales):
    """
    Group sales records by store ID and calculate total revenue.

    Args:
        sales: List of sale record dicts with 'store_id' and 'total_amount'.

    Returns:
        Dict mapping store_id -> {'total_revenue': float, 'sale_count': int}.
    """
    summary = {}
    for s in sales:
        sid = s.get("store_id", "").strip()
        if not sid:
            continue
        if sid not in summary:
            summary[sid] = {"total_revenue": 0.0, "sale_count": 0}
        try:
            summary[sid]["total_revenue"] += float(s.get("total_amount", 0))
        except (ValueError, TypeError):
            pass
        summary[sid]["sale_count"] += 1
    return summary


def join_store_metadata(store_summary, stores):
    """
    Join store revenue summary with store metadata.

    Args:
        store_summary: Dict from group_revenue_by_store().
        stores: List of store dicts with store details.

    Returns:
        List of dicts with combined store info and revenue data,
        sorted by total_revenue descending.
    """
    store_lookup = {}
    for st in stores:
        sid = st.get("store_id", "").strip()
        store_lookup[sid] = st

    joined = []
    for sid, rev_data in store_summary.items():
        meta = store_lookup.get(sid, {})
        joined.append({
            "store_id": sid,
            "store_name": meta.get("store_name", "Unknown"),
            "city": meta.get("city", ""),
            "state": meta.get("state", ""),
            "manager": meta.get("manager", ""),
            "open_date": meta.get("open_date", ""),
            "size_sqft": meta.get("size_sqft", ""),
            "total_revenue": rev_data["total_revenue"],
            "sale_count": rev_data["sale_count"],
        })

    return sorted(joined, key=lambda x: x["total_revenue"], reverse=True)


def calculate_average_revenue_per_store(store_summary):
    """
    Calculate the average revenue across all stores.

    Args:
        store_summary: Dict from group_revenue_by_store().

    Returns:
        Average revenue as float, or 0.0 if no stores.
    """
    if not store_summary:
        return 0.0
    total = sum(v["total_revenue"] for v in store_summary.values())
    return total / len(store_summary)


def find_top_store(store_summary):
    """
    Find the store with the highest total revenue.

    Args:
        store_summary: Dict from group_revenue_by_store().

    Returns:
        Tuple of (store_id, revenue) or ("None", 0.0).
    """
    if not store_summary:
        return ("None", 0.0)
    top = max(store_summary.items(), key=lambda x: x[1]["total_revenue"])
    return (top[0], top[1]["total_revenue"])


def find_lowest_store(store_summary):
    """
    Find the store with the lowest total revenue.

    Args:
        store_summary: Dict from group_revenue_by_store().

    Returns:
        Tuple of (store_id, revenue) or ("None", 0.0).
    """
    if not store_summary:
        return ("None", 0.0)
    lowest = min(store_summary.items(), key=lambda x: x[1]["total_revenue"])
    return (lowest[0], lowest[1]["total_revenue"])


def build_store_summary(stores, sales):
    """
    Build a comprehensive store performance summary.

    Args:
        stores: List of store dicts.
        sales: List of sale record dicts.

    Returns:
        Dict containing:
        - total_stores
        - total_sales
        - total_revenue
        - average_revenue_per_store
        - top_store
        - lowest_store
        - store_details (joined data sorted by revenue)
    """
    store_summary = group_revenue_by_store(sales)
    total_stores = len(store_summary)
    total_sales = sum(v["sale_count"] for v in store_summary.values())
    total_revenue = sum(v["total_revenue"] for v in store_summary.values())
    avg_revenue = calculate_average_revenue_per_store(store_summary)
    top_store = find_top_store(store_summary)
    lowest_store = find_lowest_store(store_summary)
    store_details = join_store_metadata(store_summary, stores)

    return {
        "total_stores": total_stores,
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "average_revenue_per_store": avg_revenue,
        "top_store": top_store,
        "lowest_store": lowest_store,
        "store_details": store_details,
    }


def print_store_summary(summary):
    """
    Print a formatted store performance summary to stdout.

    Args:
        summary: Dict from build_store_summary().
    """
    print("=" * 60)
    print("STORE PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Total Stores:                 {summary['total_stores']}")
    print(f"Total Sales:                  {summary['total_sales']}")
    print(f"Total Revenue:                ${summary['total_revenue']:,.2f}")
    print(f"Avg Revenue per Store:        ${summary['average_revenue_per_store']:,.2f}")
    print()

    top_id, top_rev = summary["top_store"]
    low_id, low_rev = summary["lowest_store"]
    print(f"Top Store:                    Store {top_id} (${top_rev:,.2f})")
    print(f"Lowest Store:                 Store {low_id} (${low_rev:,.2f})")
    print()

    print("--- Store Detail Rankings ---")
    header = f"{'Rank':<5} {'Store Name':<25} {'City':<15} {'Revenue':<15} {'Sales':<8}"
    print(header)
    print("-" * len(header))
    for i, sd in enumerate(summary["store_details"], 1):
        name = sd["store_name"][:24]
        city = sd["city"][:14]
        rev = f"${sd['total_revenue']:,.2f}"
        print(f"{i:<5} {name:<25} {city:<15} {rev:<15} {sd['sale_count']:<8}")
    print("=" * 60)


def load_csv(filepath):
    """Load a CSV file and return list of dicts."""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    rows = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    if not rows:
        print(f"Error: Empty file: {filepath}", file=sys.stderr)
        sys.exit(1)
    return rows


def main():
    """Main entry point when run as a script."""
    examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
    stores_path = os.path.abspath(os.path.join(examples_dir, "stores.csv"))
    sales_path = os.path.abspath(os.path.join(examples_dir, "sales.csv"))

    print(f"Loading stores from: {stores_path}")
    stores = load_csv(stores_path)
    print(f"Loading sales from: {sales_path}")
    sales = load_csv(sales_path)
    print(f"Loaded {len(stores)} stores and {len(sales)} sales records.")
    print()

    summary = build_store_summary(stores, sales)
    print_store_summary(summary)


if __name__ == "__main__":
    main()