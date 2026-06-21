"""
RetailOps customer analytics module.

Provides functions for analyzing customer data, including order counts,
revenue attribution, customer segmentation, and summary generation.
"""

import os
import sys

from retailops.errors import FileLoadError, DataValidationError
from retailops.data_loader import load_customers as load_customers_data, load_orders


# Customer segment constants
VIP = "VIP"
LOYAL = "LOYAL"
ACTIVE = "ACTIVE"
NEW = "NEW"


def calculate_customer_order_counts(customers, orders):
    """
    Calculate the number of orders for each customer.

    Args:
        customers: List of customer dicts with 'customer_id' key.
        orders: List of order dicts with 'customer_id' key.

    Returns:
        Dict mapping customer_id -> order_count.
    """
    counts = {}
    for c in customers:
        if isinstance(c, dict):
            cid = c.get("customer_id")
            if cid:
                counts[cid] = 0
    for o in orders:
        cid = o.get("customer_id")
        if cid in counts:
            counts[cid] += 1
    return counts


def calculate_customer_revenue(customers, orders):
    """
    Calculate total revenue for each customer.

    Computes revenue as quantity * unit_price for each order.

    Args:
        customers: List of customer dicts with 'customer_id'.
        orders: List of order dicts with 'customer_id', 'quantity', 'unit_price'.

    Returns:
        Dict mapping customer_id -> total_revenue.
    """
    revenue = {}
    for c in customers:
        if isinstance(c, dict):
            cid = c.get("customer_id")
            if cid:
                revenue[cid] = 0.0
    for o in orders:
        cid = o.get("customer_id")
        if cid in revenue:
            try:
                qty = int(o.get("quantity", 0))
                price = float(o.get("unit_price", 0))
                revenue[cid] += qty * price
            except (ValueError, TypeError):
                pass
    return revenue


def assign_customer_segment(total_revenue, order_count):
    """
    Assign a customer segment based on revenue and order count.

    Rules:
        VIP:   revenue >= 1000 or order_count >= 10
        LOYAL: revenue >= 500 or order_count >= 5
        ACTIVE: revenue > 0
        NEW:   revenue == 0

    Args:
        total_revenue: Total revenue for the customer.
        order_count: Total number of orders for the customer.

    Returns:
        Segment string: VIP, LOYAL, ACTIVE, or NEW.
    """
    if total_revenue >= 1000 or order_count >= 10:
        return VIP
    elif total_revenue >= 500 or order_count >= 5:
        return LOYAL
    elif total_revenue > 0:
        return ACTIVE
    else:
        return NEW


def build_customer_profiles(customers, orders):
    """
    Build enriched customer profiles with order counts, revenue, and segment.

    Args:
        customers: List of customer dicts.
        orders: List of order dicts.

    Returns:
        List of dicts containing customer info plus calculated fields.
    """
    counts = calculate_customer_order_counts(customers, orders)
    revenues = calculate_customer_revenue(customers, orders)
    profiles = []

    for c in customers:
        if not isinstance(c, dict):
            continue
        cid = c.get("customer_id", "")
        if not cid:
            continue
        order_count = counts.get(cid, 0)
        total_revenue = revenues.get(cid, 0.0)
        segment = assign_customer_segment(total_revenue, order_count)

        profiles.append({
            "customer_id": cid,
            "name": c.get("name", ""),
            "email": c.get("email", ""),
            "city": c.get("city", ""),
            "signup_date": c.get("signup_date", ""),
            "order_count": order_count,
            "total_revenue": total_revenue,
            "segment": segment,
        })

    return profiles


def summarize_segments(customer_profiles):
    """
    Summarize customer counts by segment.

    Args:
        customer_profiles: List of profile dicts from build_customer_profiles().

    Returns:
        Dict mapping segment -> count, sorted by priority.
    """
    summary = {VIP: 0, LOYAL: 0, ACTIVE: 0, NEW: 0}
    for p in customer_profiles:
        seg = p.get("segment", NEW)
        if seg in summary:
            summary[seg] += 1
    return summary


def find_top_customers(customer_profiles, limit=5):
    """
    Find the top customers by total revenue.

    Args:
        customer_profiles: List of profile dicts.
        limit: Number of top customers to return.

    Returns:
        List of profile dicts sorted by total_revenue descending.
    """
    sorted_profiles = sorted(
        customer_profiles, key=lambda x: x.get("total_revenue", 0), reverse=True
    )
    return sorted_profiles[:limit]


def build_customer_summary(customers, orders):
    """
    Build a comprehensive customer summary dict.

    Args:
        customers: List of customer dicts.
        orders: List of order dicts.

    Returns:
        Dict containing:
        - total_customers
        - total_orders
        - total_revenue
        - average_revenue_per_customer
        - segment_summary
        - top_customers
    """
    profiles = build_customer_profiles(customers, orders)
    total_customers = len(profiles)
    total_orders = sum(p["order_count"] for p in profiles)
    total_revenue = sum(p["total_revenue"] for p in profiles)
    avg_revenue = total_revenue / total_customers if total_customers > 0 else 0.0
    segment_summary = summarize_segments(profiles)
    top_customers = find_top_customers(profiles)

    return {
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "average_revenue_per_customer": avg_revenue,
        "segment_summary": segment_summary,
        "top_customers": top_customers,
        "profiles": profiles,
    }


def print_customer_summary(summary):
    """
    Print a formatted customer summary to stdout.

    Args:
        summary: Dict from build_customer_summary().
    """
    print("=" * 60)
    print("CUSTOMER ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Customers:              {summary['total_customers']}")
    print(f"Total Orders:                 {summary['total_orders']}")
    print(f"Total Revenue:                ${summary['total_revenue']:,.2f}")
    print(f"Avg Revenue per Customer:     ${summary['average_revenue_per_customer']:,.2f}")
    print()

    print("--- Customer Segments ---")
    seg = summary["segment_summary"]
    for s in [VIP, LOYAL, ACTIVE, NEW]:
        print(f"  {s}: {seg[s]}")
    print()

    print("--- Top 5 Customers by Revenue ---")
    for i, p in enumerate(summary["top_customers"], 1):
        print(f"  {i}. {p['name']} (ID: {p['customer_id']})")
        print(f"     Orders: {p['order_count']}, Revenue: ${p['total_revenue']:,.2f}, "
              f"Segment: {p['segment']}")
    print("=" * 60)


def main():
    """Main entry point when run as a script."""
    examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
    customers_path = os.path.abspath(os.path.join(examples_dir, "customers.csv"))
    orders_path = os.path.abspath(os.path.join(examples_dir, "orders.csv"))

    try:
        print(f"Loading customers from: {customers_path}")
        customers = load_customers_data(customers_path)
        print(f"Loading orders from: {orders_path}")
        orders = load_orders(orders_path)
        print(f"Loaded {len(customers)} customers and {len(orders)} orders.")
        print()

        summary = build_customer_summary(customers, orders)
        print_customer_summary(summary)
    except (FileLoadError, DataValidationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
