"""
RetailOps formatting utilities.

Provides consistent formatting functions for monetary values,
percentages, integers, and table output used across the CLI.
"""


def format_money(value: float) -> str:
    """
    Format a numeric value as a US currency string.

    Args:
        value: The monetary value to format.

    Returns:
        A string like '$1,234.56'.
    """
    if value < 0:
        return f"-${abs(value):,.2f}"
    return f"${value:,.2f}"


def format_percent(value: float) -> str:
    """
    Format a decimal fraction as a percentage string.

    Args:
        value: A decimal between 0 and 1 (or beyond).

    Returns:
        A string like '85.23%'.
    """
    return f"{value * 100:.2f}%"


def format_int(value: float) -> str:
    """
    Format a number with thousands separators as an integer.

    Args:
        value: The numeric value.

    Returns:
        A string like '1,234'.
    """
    return f"{int(round(value)):,}"


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """
    Build a left-aligned text table from headers and row data.

    Each column width is determined by the longest entry in that
    column (including the header).  A separator line is printed
    between the header and the data rows.

    Args:
        headers: Column header labels.
        rows: List of rows, each a list of string cells.

    Returns:
        A multi-line formatted table string (no trailing newline).
    """
    if not headers:
        return ""

    col_count = len(headers)
    widths: list[int] = [len(h) for h in headers]

    for row in rows:
        for i in range(min(len(row), col_count)):
            widths[i] = max(widths[i], len(row[i]))

    def build_separator() -> str:
        return "-+-".join("-" * w for w in widths)

    def build_data_line(cells: list[str]) -> str:
        padded = []
        for i in range(col_count):
            val = cells[i] if i < len(cells) else ""
            padded.append(val.ljust(widths[i]))
        return " | ".join(padded)

    lines: list[str] = []
    lines.append(build_data_line(headers))
    lines.append(build_separator())
    for row in rows:
        lines.append(build_data_line(row))

    return "\n".join(lines)