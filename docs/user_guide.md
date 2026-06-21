# User Guide

This guide explains how to install, configure, and use the RetailOps CLI Suite to analyze retail operations data.

---

## 1. Overview

RetailOps CLI Suite is a command-line tool that provides analytics for:

- Sales performance
- Inventory management
- Customer segmentation
- Returns analysis
- Store performance
- Revenue trends

It supports multiple output formats and can generate comprehensive Markdown reports.

---

## 2. System Requirements

- **Operating System:** Windows 10/11
- **Python:** 3.10 or later
- **R:** 4.0 or later (for R analysis scripts)
- **C Compiler:** GCC or MSVC (for C tools)
- **Disk Space:** 50 MB minimum

---

## 3. Installation

### 3.1 Download the Release Package

Download `retailops-cli-suite-v1.0.0.zip` from the GitHub Releases page and extract it to a folder of your choice.

### 3.2 Directory Structure After Extraction

```
retailops-cli-suite-v1.0.0/
  retailops.exe         - Main CLI executable
  c_tools/              - C compiled tools
    csv_validate.exe
    inventory_check.exe
    revenue_trend.exe
    customer_score.exe
  examples/             - Sample CSV datasets
  docs/                 - Documentation
  README.md
  LICENSE
  RELEASE_NOTES.md
```

---

## 4. Running from Source

If you have Python installed, you can run the tool directly from the source code:

```bash
python -m retailops.cli sales examples/sales.csv
python -m retailops.cli inventory examples/inventory.csv
python -m retailops.cli customers examples/customers.csv examples/orders.csv
python -m retailops.cli returns examples/returns.csv examples/orders.csv
python -m retailops.cli stores examples/stores.csv examples/sales.csv
python -m retailops.cli revenue examples/monthly_revenue.csv
python -m retailops.cli report --output reports/generated_report.md
python -m retailops.cli validate examples/sales.csv
```

---

## 5. Using the Windows Executable

Run `retailops.exe` directly from the command prompt or PowerShell:

```powershell
.\dist\retailops.exe --help
.\dist\retailops.exe sales examples/sales.csv
.\dist\retailops.exe inventory examples/inventory.csv
```

---

## 6. CLI Commands Reference

### 6.1 `sales`

Analyze sales data from a CSV file.

```bash
retailops.exe sales <file>
```

Outputs total revenue, total quantity, top products, top categories, and top stores.

### 6.2 `inventory`

Analyze inventory levels and stock status.

```bash
retailops.exe inventory <file>
```

Outputs total value, stock status distribution, and reorder recommendations.

### 6.3 `customers`

Segment customers based on their purchase history.

```bash
retailops.exe customers <customers_file> <orders_file>
```

Outputs segment counts and top customers.

### 6.4 `returns`

Analyze product returns.

```bash
retailops.exe returns <returns_file> <orders_file>
```

Outputs return rate, top reasons, and top returned products.

### 6.5 `stores`

Analyze store performance.

```bash
retailops.exe stores <stores_file> <sales_file>
```

Outputs per-store revenue, average revenue, and top/lowest stores.

### 6.6 `revenue`

Analyze monthly revenue trends.

```bash
retailops.exe revenue <file>
```

Outputs total revenue, growth rates, moving averages, and best/worst months.

### 6.7 `report`

Generate a comprehensive Markdown report.

```bash
retailops.exe report --output <output_file>
```

### 6.8 `validate`

Validate a CSV file's structure.

```bash
retailops.exe validate <file>
```

---

## 7. C Tools

The C tools are standalone executables located in the `c_tools/` directory:

- `csv_validate.exe` - Validate CSV field counts
- `inventory_check.exe` - Summarize inventory metrics
- `revenue_trend.exe` - Compute revenue trends
- `customer_score.exe` - Score and rank customers

---

## 8. R Scripts

R scripts are provided for advanced statistical analysis:

- `r_scripts/sales_summary.R` - Sales aggregation
- `r_scripts/inventory_summary.R` - Inventory valuation
- `r_scripts/customer_segments.R` - Customer segmentation
- `r_scripts/revenue_forecast.R` - Revenue trend analysis

---

## 9. Troubleshooting

| Problem | Solution |
|---------|----------|
| File not found | Verify the file path and try again |
| Missing columns | Ensure the CSV has the required headers |
| exe not recognized | Add the folder to PATH or use full path |
| R scripts fail | Verify R is installed and in PATH |

---

## 10. Support

For issues and feature requests, please open an issue on GitHub.