"""
RetailOps returns analytics module.

Provides functions for analyzing return data, including counts, amounts,
grouping by reason and product, return rate calculation, and summary generation.
"""

import csv
import os
import sys


def calculate_return_count(returns):
    """
    Calculate the total number of return records.

    Args:
        returns: List of return record dicts.

    Returns:
        Total return count as int.
    """
    return len(returns)


def calculate_return_amount(returns):
    """
    Calculate the total return amount across all returns.

    Args:
        returns: List of return record dicts with 'return_amount'.

    Returns:
        Total return amount as float.
    """
    total = 0.0
    for r in returns:
        try:
            total += float(r.get("return_amount", 0))
        except (ValueError, TypeError):
            pass
    return total


def group_returns_by_reason(returns):
    """
    Group return records by return reason and sum amounts.

    Args:
        returns: List of return record dicts with 'return_reason' and 'return_amount'.

    Returns:
        Dict mapping reason -> {'count': int, 'amount': float}.
    """
    summary = {}
    for r in returns:
        reason = r.get("return_reason", "Unknown")
        if reason not in summary:
            summary[reason] = {"count": 0, "amount": 0.0}
        summary[reason]["count"] += 1
        try:
            summary[reason]["amount"] += float(r.get("return_amount", 0))
        except (ValueError, TypeError):
            pass
    return summary


def group_returns_by_product(returns):
    """
    Group return records by product ID and sum amounts.

    Args:
        returns: List of return record dicts with 'product_id' and 'return_amount'.

    Returns:
        Dict mapping product_id -> {'count': int, 'amount': float}.
    """
    summary = {}
    for r in returns:
        pid = r.get("product_id", "Unknown")
        if pid not in summary:
            summary[pid] = {"count": 0, "amount": 0.0}
        summary[pid]["count"] += 1
        try:
            summary[pid]["amount"] += float(r.get("return_amount", 0))
        except (ValueError, TypeError):
            pass
    return summary


def calculate_return_rate(returns, orders):
    """
    Calculate the overall return rate as percentage.

    Return rate = (total returned items / total ordered items) * 100

    Args:
        returns: List of return record dicts with 'quantity'.
        orders: List of order dicts with 'quantity'.

    Returns:
        Return rate as float percentage (0.0 if no orders).
    """
    total_returned_qty = 0
    for r in returns:
        try:
            total_returned_qty += int(r.get("quantity", 0))
        except (ValueError, TypeError):
            pass

    total_ordered_qty = 0
    for o in orders:
        try:
            total_ordered_qty += int(o.get("quantity", 0))
        except (ValueError, TypeError):
            pass

    if total_ordered_qty == 0:
        return 0.0

    return (total_returned_qty / total_ordered_qty) * 100.0


def find_top_return_reason(reason_summary):
    """
    Find the return reason with the highest total amount.

    Args:
        reason_summary: Dict from group_returns_by_reason().

    Returns:
        Tuple of (reason, amount) for the top reason, or ("None", 0.0).
    """
    if not reason_summary:
        return ("None", 0.0)

    top_reason = max(reason_summary.items(), key=lambda x: x[1]["amount"])
    return (top_reason[0], top_reason[1]["amount"])


def find_top_return_product(product_summary):
    """
    Find the product with the highest return amount.

    Args:
        product_summary: Dict from group_returns_by_product().

    Returns:
        Tuple of (product_id, amount) for the top product, or ("None", 0.0).
    """
    if not product_summary:
        return ("None", 0.0)

    top_product = max(product_summary.items(), key=lambda x: x[1]["amount"])
    return (top_product[0], top_product[1]["amount"])


def build_returns_summary(returns, orders):
    """
    Build a comprehensive returns summary dict.

    Args:
        returns: List of return record dicts.
        orders: List of order dicts.

    Returns:
        Dict containing:
        - total_returns
        - total_return_amount
        - return_rate
        - reason_summary
        - product_summary
        - top_return_reason
        - top_return_product
    """
    total_returns = calculate_return_count(returns)
    total_return_amount = calculate_return_amount(returns)
    return_rate = calculate_return_rate(returns, orders)
    reason_summary = group_returns_by_reason(returns)
    product_summary = group_returns_by_product(returns)
    top_reason = find_top_return_reason(reason_summary)
    top_product = find_top_return_product(product_summary)

    return {
        "total_returns": total_returns,
        "total_return_amount": total_return_amount,
        "return_rate": return_rate,
        "reason_summary": reason_summary,
        "product_summary": product_summary,
        "top_return_reason": top_reason,
        "top_return_product": top_product,
    }


def print_returns_summary(summary):
    """
    Print a formatted returns summary to stdout.

    Args:
        summary: Dict from build_returns_summary().
    """
    print("=" * 60)
    print("RETURNS ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Returns:                {summary['total_returns']}")
    print(f"Total Return Amount:          ${summary['total_return_amount']:,.2f}")
    print(f"Return Rate:                  {summary['return_rate']:.2f}%")
    print()

    print("--- Returns by Reason ---")
    for reason, data in sorted(
        summary["reason_summary"].items(), key=lambda x: x[1]["amount"], reverse=True
    ):
        print(f"  {reason}: {data['count']} returns, ${data['amount']:,.2f}")
    print()

    print("--- Returns by Product ---")
    for pid, data in sorted(
        summary["product_summary"].items(), key=lambda x: x[1]["amount"], reverse=True
    )[:5]:
        print(f"  Product {pid}: {data['count']} returns, ${data['amount']:,.2f}")
    print()

    reason_name, reason_amount = summary["top_return_reason"]
    prod_id, prod_amount = summary["top_return_product"]
    print(f"Top Return Reason:            {reason_name} (${reason_amount:,.2f})")
    print(f"Top Return Product:           {prod_id} (${prod_amount:,.2f})")
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
    returns_path = os.path.abspath(os.path.join(examples_dir, "returns.csv"))
    orders_path = os.path.abspath(os.path.join(examples_dir, "orders.csv"))

    print(f"Loading returns from: {returns_path}")
    returns = load_csv(returns_path)
    print(f"Loading orders from: {orders_path}")
    orders = load_csv(orders_path)
    print(f"Loaded {len(returns)} returns and {len(orders)} orders.")
    print()

    summary = build_returns_summary(returns, orders)
    print_returns_summary(summary)


if __name__ == "__main__":
    main()