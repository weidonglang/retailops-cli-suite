"""
RetailOps Markdown report builder module.

Generates comprehensive Markdown reports from all retail analytics modules.
Provides section builders for sales, inventory, customers, returns, stores,
and revenue, plus a full report assembler and file writer.
"""

import os
import sys
from datetime import datetime

from retailops.formatting import format_money, format_percent, format_int, format_table
from retailops.sales import (
    calculate_total_revenue, calculate_total_quantity, calculate_average_order_revenue,
    group_revenue_by_product, group_revenue_by_category, group_revenue_by_store,
    find_top_group, build_sales_summary,
)
from retailops.inventory import (
    enrich_inventory_items, summarize_inventory_by_category, find_top_reorder_item,
    find_top_inventory_category, build_inventory_summary,
)
from retailops.customers import (
    calculate_customer_order_counts, calculate_customer_revenue, assign_customer_segment,
    build_customer_profiles, summarize_segments, find_top_customers, build_customer_summary,
)
from retailops.returns import (
    calculate_return_count, calculate_return_amount, group_returns_by_reason,
    group_returns_by_product, calculate_return_rate, find_top_return_reason,
    find_top_return_product, build_returns_summary,
)
from retailops.stores import (
    group_revenue_by_store, join_store_metadata, calculate_average_revenue_per_store,
    find_top_store, find_lowest_store, build_store_summary,
)
from retailops.revenue import (
    aggregate_monthly_revenue, calculate_total_monthly_revenue,
    calculate_average_monthly_revenue, calculate_growth_rates,
    calculate_moving_average, find_best_month, find_worst_month, build_revenue_summary,
)
from retailops.data_loader import (
    load_sales, load_inventory, load_customers, load_orders,
    load_returns, load_stores, load_monthly_revenue,
)


def build_sales_section(summary):
    """
    Build a Markdown section for sales analytics.

    Args:
        summary: Dict from build_sales_summary(). Keys:
            - total_revenue, total_quantity, order_count, average_revenue
            - top_products, top_categories, top_stores

    Returns:
        Markdown string.
    """
    lines = []
    lines.append("## Sales Analytics")
    lines.append("")
    lines.append(f"- **Order Count:** {format_int(summary['order_count'])}")
    lines.append(f"- **Total Quantity:** {format_int(summary['total_quantity'])}")
    lines.append(f"- **Total Revenue:** {format_money(summary['total_revenue'])}")
    lines.append(f"- **Average Order Revenue:** {format_money(summary['average_revenue'])}")
    lines.append("")

    if summary.get("top_products"):
        lines.append("### Top 5 Products by Revenue")
        lines.append("")
        lines.append("| # | Product | Revenue |")
        lines.append("|---|---------|---------|")
        for i, (product, rev) in enumerate(summary["top_products"], 1):
            lines.append(f"| {i} | {product} | {format_money(rev)} |")
        lines.append("")

    if summary.get("top_categories"):
        lines.append("### Top 5 Categories by Revenue")
        lines.append("")
        lines.append("| # | Category | Revenue |")
        lines.append("|---|----------|---------|")
        for i, (cat, rev) in enumerate(summary["top_categories"], 1):
            lines.append(f"| {i} | {cat} | {format_money(rev)} |")
        lines.append("")

    if summary.get("top_stores"):
        lines.append("### Top 5 Stores by Revenue")
        lines.append("")
        lines.append("| # | Store | Revenue |")
        lines.append("|---|-------|---------|")
        for i, (sid, rev) in enumerate(summary["top_stores"], 1):
            lines.append(f"| {i} | {sid} | {format_money(rev)} |")
        lines.append("")

    return "\n".join(lines)


def build_inventory_section(summary):
    """
    Build a Markdown section for inventory analytics.

    Args:
        summary: Dict from build_inventory_summary(). Keys:
            - total_items, total_stock, total_value
            - low_stock_count, out_of_stock_count
            - average_stock_per_item, average_value_per_item
            - category_summary, top_reorder_item, top_category

    Returns:
        Markdown string.
    """
    lines = []
    lines.append("## Inventory Analytics")
    lines.append("")
    lines.append(f"- **Total Items:** {format_int(summary['total_items'])}")
    lines.append(f"- **Total Stock Units:** {format_int(summary['total_stock'])}")
    lines.append(f"- **Total Value:** {format_money(summary['total_value'])}")
    lines.append(f"- **Average Stock per Item:** {summary['average_stock_per_item']:.1f}")
    lines.append(f"- **Average Value per Item:** {format_money(summary['average_value_per_item'])}")
    ok_count = summary['total_items'] - summary['low_stock_count'] - summary['out_of_stock_count']
    lines.append(f"- **Stock Health:**")
    lines.append(f"  - OK: {format_int(ok_count)}")
    lines.append(f"  - Low Stock: {format_int(summary['low_stock_count'])}")
    lines.append(f"  - Out of Stock: {format_int(summary['out_of_stock_count'])}")
    lines.append("")

    if summary.get("category_summary"):
        lines.append("### Category Summary")
        lines.append("")
        lines.append("| Category | Items | Stock | Value | Low Stock | Out of Stock |")
        lines.append("|----------|-------|-------|-------|-----------|--------------|")
        for cat_name in sorted(summary["category_summary"].keys()):
            data = summary["category_summary"][cat_name]
            lines.append(
                f"| {cat_name} | {data['item_count']} | {data['total_stock']} | "
                f"{format_money(data['total_value'])} | {data['low_stock_count']} | "
                f"{data['out_of_stock_count']} |"
            )
        lines.append("")

    if summary.get("top_reorder_item"):
        top_item = summary["top_reorder_item"]
        item_name = top_item.get("product_name", "Unknown")
        reorder_qty = top_item.get("reorder_quantity", 0)
        lines.append(f"- **Top Reorder Item:** {item_name} (need {reorder_qty} units)")
        lines.append("")

    if summary.get("top_category"):
        cat_name, cat_info = summary["top_category"]
        lines.append(f"- **Top Category (by value):** {cat_name} ({format_money(cat_info['total_value'])})")
        lines.append("")

    return "\n".join(lines)


def build_customer_section(summary):
    """
    Build a Markdown section for customer analytics.

    Args:
        summary: Dict from build_customer_summary(). Keys:
            - total_customers, total_orders, total_revenue
            - average_revenue_per_customer
            - segment_summary, top_customers, profiles

    Returns:
        Markdown string.
    """
    lines = []
    lines.append("## Customer Analytics")
    lines.append("")
    lines.append(f"- **Total Customers:** {format_int(summary['total_customers'])}")
    lines.append(f"- **Total Orders:** {format_int(summary['total_orders'])}")
    lines.append(f"- **Total Revenue:** {format_money(summary['total_revenue'])}")
    lines.append(f"- **Avg Revenue per Customer:** {format_money(summary['average_revenue_per_customer'])}")
    lines.append("")

    if summary.get("segment_summary"):
        lines.append("### Customer Segments")
        lines.append("")
        lines.append("| Segment | Customers |")
        lines.append("|---------|-----------|")
        for seg in sorted(summary["segment_summary"].keys()):
            lines.append(f"| {seg} | {summary['segment_summary'][seg]} |")
        lines.append("")

    if summary.get("top_customers"):
        lines.append("### Top 5 Customers by Revenue")
        lines.append("")
        lines.append("| Name | Customer ID | Orders | Revenue | Segment |")
        lines.append("|------|-------------|--------|---------|---------|")
        for c in summary["top_customers"]:
            lines.append(
                f"| {c['name']} | {c['customer_id']} | {c['order_count']} | "
                f"{format_money(c['total_revenue'])} | {c['segment']} |"
            )
        lines.append("")

    return "\n".join(lines)


def build_returns_section(summary):
    """
    Build a Markdown section for returns analytics.

    Args:
        summary: Dict from build_returns_summary(). Keys:
            - total_returns, total_return_amount, return_rate
            - reason_summary, product_summary
            - top_return_reason, top_return_product

    Returns:
        Markdown string.
    """
    lines = []
    lines.append("## Returns Analytics")
    lines.append("")
    lines.append(f"- **Total Returns:** {format_int(summary['total_returns'])}")
    lines.append(f"- **Total Return Amount:** {format_money(summary['total_return_amount'])}")
    lines.append(f"- **Return Rate:** {format_percent(summary.get('return_rate', 0))}")
    lines.append("")

    if summary.get("top_return_reason"):
        reason, count = summary["top_return_reason"]
        lines.append(f"- **Most Common Return Reason:** {reason} ({format_int(count)} returns)")
    if summary.get("top_return_product"):
        pid, amount = summary["top_return_product"]
        lines.append(f"- **Most Returned Product:** {pid} ({format_money(amount)} returned)")
    lines.append("")

    if summary.get("reason_summary"):
        lines.append("### Returns by Reason")
        lines.append("")
        lines.append("| Reason | Count | Amount |")
        lines.append("|--------|-------|--------|")
        for reason in sorted(summary["reason_summary"].keys()):
            data = summary["reason_summary"][reason]
            lines.append(f"| {reason} | {data['count']} | {format_money(data['amount'])} |")
        lines.append("")

    return "\n".join(lines)


def build_stores_section(summary):
    """
    Build a Markdown section for store analytics.

    Args:
        summary: Dict from build_store_summary(). Keys:
            - total_stores, total_sales, total_revenue
            - average_revenue_per_store
            - top_store, lowest_store, store_details

    Returns:
        Markdown string.
    """
    lines = []
    lines.append("## Store Analytics")
    lines.append("")
    lines.append(f"- **Total Stores:** {format_int(summary['total_stores'])}")
    lines.append(f"- **Total Sales (Records):** {format_int(summary['total_sales'])}")
    lines.append(f"- **Total Revenue:** {format_money(summary['total_revenue'])}")
    lines.append(f"- **Average Revenue per Store:** {format_money(summary['average_revenue_per_store'])}")
    lines.append("")

    top_id, top_rev = summary["top_store"]
    low_id, low_rev = summary["lowest_store"]
    lines.append(f"- **Top Store:** Store {top_id} ({format_money(top_rev)})")
    lines.append(f"- **Lowest Store:** Store {low_id} ({format_money(low_rev)})")
    lines.append("")

    if summary.get("store_details"):
        lines.append("### Store Rankings")
        lines.append("")
        lines.append("| Rank | Store Name | City | Revenue | Sales |")
        lines.append("|------|------------|------|---------|-------|")
        for i, sd in enumerate(summary["store_details"], 1):
            lines.append(
                f"| {i} | {sd['store_name']} | {sd['city']} | "
                f"{format_money(sd['total_revenue'])} | {sd['sale_count']} |"
            )
        lines.append("")

    return "\n".join(lines)


def build_revenue_section(summary):
    """
    Build a Markdown section for revenue trend analytics.

    Args:
        summary: Dict from build_revenue_summary(). Keys:
            - month_count, total_revenue, average_monthly_revenue
            - best_month, worst_month
            - monthly_summary, growth_rates

    Returns:
        Markdown string.
    """
    lines = []
    lines.append("## Revenue Trend Analytics")
    lines.append("")
    lines.append(f"- **Total Months:** {format_int(summary['month_count'])}")
    lines.append(f"- **Total Revenue:** {format_money(summary['total_revenue'])}")
    lines.append(f"- **Average Monthly Revenue:** {format_money(summary['average_monthly_revenue'])}")
    lines.append("")

    by, bm, brev = summary["best_month"]
    wy, wm, wrev = summary["worst_month"]
    lines.append(f"- **Best Month:** {by}-{bm:02d} ({format_money(brev)})")
    lines.append(f"- **Worst Month:** {wy}-{wm:02d} ({format_money(wrev)})")
    lines.append("")

    if summary.get("monthly_summary"):
        lines.append("### Monthly Revenue Breakdown")
        lines.append("")
        lines.append("| Year-Month | Revenue |")
        lines.append("|------------|---------|")
        for m in summary["monthly_summary"]:
            ym = f"{m['year']}-{m['month']:02d}"
            lines.append(f"| {ym} | {format_money(m['total_revenue'])} |")
        lines.append("")

    if summary.get("growth_rates"):
        lines.append("### Month-over-Month Growth Rates")
        lines.append("")
        for g in summary["growth_rates"]:
            ym = f"{g['year']}-{g['month']:02d}"
            lines.append(f"- {ym}: {g['growth_rate']:+.2f}%")
        lines.append("")

    return "\n".join(lines)


def build_full_report(sections):
    """
    Combine report sections into a complete Markdown document.

    Args:
        sections: Dict mapping section names to Markdown strings.

    Returns:
        Complete Markdown report string.
    """
    lines = []
    lines.append("# RetailOps CLI Suite - Retail Analytics Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    section_order = [
        "sales", "inventory", "customers", "returns",
        "stores", "revenue",
    ]

    for sec in section_order:
        if sec in sections and sections[sec]:
            lines.append(sections[sec])
            lines.append("---")
            lines.append("")

    lines.append("## Summary")
    lines.append("")
    for sec in section_order:
        if sec in sections and sections[sec]:
            lines.append(f"- {sec.capitalize()} analytics included")
    lines.append("")
    lines.append("> Report generated by RetailOps CLI Suite.")
    lines.append("")

    return "\n".join(lines)


def write_report(report_text, output_path):
    """
    Write report text to a file.

    Args:
        report_text: Markdown report string.
        output_path: Path to write the report file.
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Report written to: {output_path}")


def main():
    """Main entry point: generate a sample report using example data."""
    examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Load all example data
    print("Loading example data...")
    sales_data = load_sales(os.path.join(examples_dir, "sales.csv"))
    inventory_data = load_inventory(os.path.join(examples_dir, "inventory.csv"))
    customers_data = load_customers(os.path.join(examples_dir, "customers.csv"))
    orders_data = load_orders(os.path.join(examples_dir, "orders.csv"))
    returns_data = load_returns(os.path.join(examples_dir, "returns.csv"))
    stores_data = load_stores(os.path.join(examples_dir, "stores.csv"))
    revenue_data = load_monthly_revenue(os.path.join(examples_dir, "monthly_revenue.csv"))

    # Build summaries
    print("Building analytics summaries...")
    sales_summary = build_sales_summary(orders_data)
    inventory_summary = build_inventory_summary(inventory_data)
    customer_summary = build_customer_summary(customers_data, orders_data)
    returns_summary = build_returns_summary(returns_data, orders_data)
    store_summary = build_store_summary(stores_data, sales_data)
    revenue_summary = build_revenue_summary(revenue_data)

    # Build sections
    sections = {
        "sales": build_sales_section(sales_summary),
        "inventory": build_inventory_section(inventory_summary),
        "customers": build_customer_section(customer_summary),
        "returns": build_returns_section(returns_summary),
        "stores": build_stores_section(store_summary),
        "revenue": build_revenue_section(revenue_summary),
    }

    # Generate full report
    print("Generating Markdown report...")
    report = build_full_report(sections)

    # Write sample report
    output_path = os.path.join(reports_dir, "sample_report.md")
    write_report(report, output_path)
    print("Sample report generated successfully.")


if __name__ == "__main__":
    main()