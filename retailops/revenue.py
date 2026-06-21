"""
RetailOps monthly revenue trend analytics module.

Provides functions for analyzing monthly revenue data, including totals,
averages, growth rates, moving averages, best/worst months, and summaries.
"""

import csv
import os
import sys


def aggregate_monthly_revenue(rows):
    """
    Aggregate revenue data across stores by year-month.

    Args:
        rows: List of dicts with 'year', 'month', 'total_revenue', 'total_orders'.

    Returns:
        List of dicts sorted by (year, month) with:
        - year, month, total_revenue, total_orders
    """
    monthly = {}
    for row in rows:
        year = int(row.get("year", 0))
        month = int(row.get("month", 0))
        key = (year, month)
        if key not in monthly:
            monthly[key] = {"year": year, "month": month, "total_revenue": 0.0, "total_orders": 0}
        try:
            monthly[key]["total_revenue"] += float(row.get("total_revenue", 0))
        except (ValueError, TypeError):
            pass
        try:
            monthly[key]["total_orders"] += int(row.get("total_orders", 0))
        except (ValueError, TypeError):
            pass
    result = sorted(monthly.values(), key=lambda x: (x["year"], x["month"]))
    return result


def calculate_total_monthly_revenue(rows):
    """
    Calculate the total revenue across all months.

    Args:
        rows: List of revenue row dicts.

    Returns:
        Total revenue as float.
    """
    total = 0.0
    for r in rows:
        try:
            total += float(r.get("total_revenue", 0))
        except (ValueError, TypeError):
            pass
    return total


def calculate_average_monthly_revenue(rows):
    """
    Calculate the average monthly revenue.

    Args:
        rows: List of revenue row dicts.

    Returns:
        Average monthly revenue as float.
    """
    if not rows:
        return 0.0
    return calculate_total_monthly_revenue(rows) / len(rows)


def calculate_growth_rates(rows):
    """
    Calculate month-over-month revenue growth rates.

    Args:
        rows: List of revenue row dicts (aggregated by month).

    Returns:
        List of dicts with 'year', 'month', 'revenue', 'growth_rate'.
        First month has growth_rate = 0.0.
    """
    monthly = aggregate_monthly_revenue(rows)
    result = []
    prev_revenue = None
    for m in monthly:
        revenue = m["total_revenue"]
        if prev_revenue is None or prev_revenue == 0:
            growth_rate = 0.0
        else:
            growth_rate = ((revenue - prev_revenue) / prev_revenue) * 100.0
        result.append({
            "year": m["year"],
            "month": m["month"],
            "revenue": revenue,
            "growth_rate": growth_rate,
        })
        prev_revenue = revenue
    return result


def calculate_moving_average(rows, window=3):
    """
    Calculate moving average of revenue over a sliding window.

    Args:
        rows: List of revenue row dicts.
        window: Number of periods for the moving average (default 3).

    Returns:
        List of dicts with 'year', 'month', 'revenue', 'moving_average'.
        First (window-1) months have moving_average = None.
    """
    monthly = aggregate_monthly_revenue(rows)
    result = []
    revenues = [m["total_revenue"] for m in monthly]

    for i, m in enumerate(monthly):
        if i < window - 1:
            ma = None
        else:
            ma = sum(revenues[i - window + 1 : i + 1]) / window
        result.append({
            "year": m["year"],
            "month": m["month"],
            "revenue": m["total_revenue"],
            "moving_average": ma,
        })
    return result


def find_best_month(rows):
    """
    Find the month with the highest total revenue.

    Args:
        rows: List of revenue row dicts.

    Returns:
        Tuple of (year, month, revenue) or (0, 0, 0.0).
    """
    if not rows:
        return (0, 0, 0.0)
    best = max(rows, key=lambda r: float(r.get("total_revenue", 0)))
    return (int(best.get("year", 0)), int(best.get("month", 0)), float(best.get("total_revenue", 0)))


def find_worst_month(rows):
    """
    Find the month with the lowest total revenue.

    Args:
        rows: List of revenue row dicts.

    Returns:
        Tuple of (year, month, revenue) or (0, 0, 0.0).
    """
    if not rows:
        return (0, 0, 0.0)
    worst = min(rows, key=lambda r: float(r.get("total_revenue", 0)))
    return (int(worst.get("year", 0)), int(worst.get("month", 0)), float(worst.get("total_revenue", 0)))


def build_revenue_summary(rows):
    """
    Build a comprehensive revenue trend summary.

    Args:
        rows: List of revenue row dicts.

    Returns:
        Dict containing:
        - month_count
        - total_revenue
        - average_monthly_revenue
        - best_month
        - worst_month
        - monthly_summary (aggregated by year-month)
        - growth_rates
        - moving_average_3
        - moving_average_6
    """
    monthly = aggregate_monthly_revenue(rows)
    month_count = len(monthly)
    total_revenue = calculate_total_monthly_revenue(rows)
    avg_revenue = calculate_average_monthly_revenue(rows)
    best = find_best_month(monthly)
    worst = find_worst_month(monthly)
    growth = calculate_growth_rates(rows)
    ma3 = calculate_moving_average(rows, window=3)
    ma6 = calculate_moving_average(rows, window=6)

    return {
        "month_count": month_count,
        "total_revenue": total_revenue,
        "average_monthly_revenue": avg_revenue,
        "best_month": best,
        "worst_month": worst,
        "monthly_summary": monthly,
        "growth_rates": growth,
        "moving_average_3": ma3,
        "moving_average_6": ma6,
    }


def print_revenue_summary(summary):
    """
    Print a formatted revenue trend summary to stdout.

    Args:
        summary: Dict from build_revenue_summary().
    """
    print("=" * 60)
    print("REVENUE TREND SUMMARY")
    print("=" * 60)
    print(f"Total Months:                 {summary['month_count']}")
    print(f"Total Revenue:                ${summary['total_revenue']:,.2f}")
    print(f"Average Monthly Revenue:      ${summary['average_monthly_revenue']:,.2f}")
    print()

    by, bm, brev = summary["best_month"]
    wy, wm, wrev = summary["worst_month"]
    print(f"Best Month:                   {by}-{bm:02d} (${brev:,.2f})")
    print(f"Worst Month:                  {wy}-{wm:02d} (${wrev:,.2f})")
    print()

    print("--- Monthly Revenue Breakdown ---")
    header = f"{'Year-Month':<12} {'Revenue':<15} {'Orders':<10}"
    print(header)
    print("-" * len(header))
    for m in summary["monthly_summary"]:
        ym = f"{m['year']}-{m['month']:02d}"
        rev = f"${m['total_revenue']:,.2f}"
        print(f"{ym:<12} {rev:<15} {m['total_orders']:<10}")
    print()

    print("--- Growth Rates ---")
    for g in summary["growth_rates"]:
        ym = f"{g['year']}-{g['month']:02d}"
        print(f"  {ym}: {g['growth_rate']:+.2f}%")
    print()

    print("--- Moving Average (3-month) ---")
    for ma in summary["moving_average_3"]:
        ym = f"{ma['year']}-{ma['month']:02d}"
        if ma["moving_average"] is not None:
            print(f"  {ym}: ${ma['moving_average']:,.2f}")
        else:
            print(f"  {ym}: N/A")
    print()

    print("--- Moving Average (6-month) ---")
    for ma in summary["moving_average_6"]:
        ym = f"{ma['year']}-{ma['month']:02d}"
        if ma["moving_average"] is not None:
            print(f"  {ym}: ${ma['moving_average']:,.2f}")
        else:
            print(f"  {ym}: N/A")
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
    revenue_path = os.path.abspath(os.path.join(examples_dir, "monthly_revenue.csv"))

    print(f"Loading revenue data from: {revenue_path}")
    rows = load_csv(revenue_path)
    print(f"Loaded {len(rows)} revenue records.")
    print()

    summary = build_revenue_summary(rows)
    print_revenue_summary(summary)


if __name__ == "__main__":
    main()