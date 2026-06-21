# User Guide

This guide explains how to install, configure, and use the RetailOps CLI Suite to analyze retail operations data. It also includes a complete verification guide so anyone can reproduce the setup and testing steps.

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

### 4.1 Verifying Source Code Works

After cloning the repository, run these checks:

```bash
# Check Python compilation
python -m compileall retailops

# Run the CLI help
python -m retailops.cli --help

# Run a simple sales analysis
python -m retailops.cli sales examples/sales.csv

# Run the full test suite
powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1
```

---

## 5. Using the Windows Executable

Run `retailops.exe` directly from the command prompt or PowerShell:

```powershell
.\retailops.exe --help
.\retailops.exe sales examples/sales.csv
.\retailops.exe inventory examples/inventory.csv
```

### 5.1 Verifying the Executable

After building or downloading `retailops.exe`, verify it works:

```powershell
# Check help output
.\retailops.exe --help
# Output should list all available commands: sales, inventory, customers, returns, stores, revenue, report, validate

# Run sales analysis
.\retailops.exe sales examples/sales.csv
# Expected output: Total Revenue, Total Quantity, Top Product, Top Category, Top Store

# Run inventory analysis
.\retailops.exe inventory examples/inventory.csv
# Expected output: Total Value, Stock Status Summary, Reorder Recommendations

# Run validate
.\retailops.exe validate examples/sales.csv
# Expected output: Validation passed
```

---

## 6. CLI Commands Reference

### 6.1 `sales`

Analyze sales data from a CSV file.

```bash
retailops.exe sales <file>
```

Outputs total revenue, total quantity, top products, top categories, and top stores.

**Example output:**
```
=== Sales Summary ===
Total Revenue: $152,847.30
Total Quantity: 1,284 units
Top Product: Laptop Pro (25 orders, $37,473.00)
Top Category: Electronics (46 orders, $68,745.20)
Top Store: Downtown Store (55 orders, $53,496.55)
Average Order Revenue: $1,528.47
```

### 6.2 `inventory`

Analyze inventory levels and stock status.

```bash
retailops.exe inventory <file>
```

Outputs total value, stock status distribution, and reorder recommendations.

**Example output:**
```
=== Inventory Summary ===
Total Items: 40
Total Stock: 4,220 units
Total Value: $147,420.00
Out of Stock: 2 items
Low Stock: 8 items
OK: 30 items
Top Reorder Item: Wireless Mouse (0 units, $1,500.00)
Top Category by Value: Electronics ($89,520.00)
```

### 6.3 `customers`

Segment customers based on their purchase history.

```bash
retailops.exe customers <customers_file> <orders_file>
```

Outputs segment counts and top customers.

**Segment rules:**
- VIP: revenue >= 1000 or orders >= 10
- LOYAL: revenue >= 500 or orders >= 5
- ACTIVE: revenue > 0
- NEW: revenue == 0

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

This combines all analytics into a single report file.

### 6.8 `validate`

Validate a CSV file's structure.

```bash
retailops.exe validate <file>
```

Checks for correct column headers, non-empty data, and valid field types.

---

## 7. C Tools

The C tools are standalone executables located in the `c_tools/` directory during development:

- `csv_validate.exe` - Validate CSV field counts
- `inventory_check.exe` - Summarize inventory metrics
- `revenue_trend.exe` - Compute revenue trends
- `customer_score.exe` - Score and rank customers

### 7.1 Verifying C Tools

After building or downloading, verify each tool:

```powershell
# Verify csv_validate
.\c_tools\csv_validate.exe examples/sales.csv 8
# Expected: total=80+, valid=80+, invalid=0 (or similar)

# Verify inventory_check
.\c_tools\inventory_check.exe examples/inventory.csv
# Expected: item_count=40+, total_stock=4000+, low_stock and out_of_stock counts

# Verify revenue_trend
.\c_tools\revenue_trend.exe examples/monthly_revenue.csv
# Expected: months=36, total_revenue, average, best/worst month

# Verify customer_score
.\c_tools\customer_score.exe examples/customers.csv examples/orders.csv
# Expected: Top 5 customers with scores
```

---

## 8. R Scripts

R scripts are provided for advanced statistical analysis:

- `r_scripts/sales_summary.R` - Sales aggregation
- `r_scripts/inventory_summary.R` - Inventory valuation
- `r_scripts/customer_segments.R` - Customer segmentation
- `r_scripts/revenue_forecast.R` - Revenue trend analysis

### 8.1 Running R Scripts

```bash
Rscript r_scripts/sales_summary.R
Rscript r_scripts/inventory_summary.R
Rscript r_scripts/customer_segments.R
Rscript r_scripts/revenue_forecast.R
```

### 8.2 Verifying R Scripts

Run the R test suite:

```bash
Rscript tests/test_r_scripts.R
```

Expected output: "All R script tests passed."

---

## 9. Full Verification Guide

Follow these steps to completely verify the release package works:

### Step 1: Extract the ZIP

```powershell
# Extract the release package
# If using the downloaded zip:
Expand-Archive -Path retailops-cli-suite-v1.0.0.zip -DestinationPath retailops-test
cd retailops-test
```

### Step 2: Verify Python Executable

```powershell
.\retailops.exe --help
.\retailops.exe sales examples/sales.csv
.\retailops.exe inventory examples/inventory.csv
.\retailops.exe customers examples/customers.csv examples/orders.csv
.\retailops.exe returns examples/returns.csv examples/orders.csv
.\retailops.exe stores examples/stores.csv examples/sales.csv
.\retailops.exe revenue examples/monthly_revenue.csv
.\retailops.exe report --output reports\verify_report.md
.\retailops.exe validate examples/sales.csv
```

All commands should exit with code 0 and produce meaningful output.

### Step 3: Verify C Tools

```powershell
.\c_tools\csv_validate.exe examples/sales.csv 8
.\c_tools\inventory_check.exe examples\inventory.csv
.\c_tools\revenue_trend.exe examples\monthly_revenue.csv
.\c_tools\customer_score.exe examples\customers.csv examples\orders.csv
```

### Step 4: Verify Documentation

```powershell
# Check that all doc files exist
Get-ChildItem docs
# Should show: data_dictionary.md, developer_guide.md, release_checklist.md, user_guide.md, line_count_report.md
```

### Step 5: Verify Line Count

```powershell
# If running from source (not just the extracted zip):
powershell -ExecutionPolicy Bypass -File scripts/count_lines.ps1
# Should show total lines >= 5000 and exit with 0
```

---

## 10. Troubleshooting

| Problem | Solution |
|---------|----------|
| File not found | Verify the file path and try again |
| Missing columns | Ensure the CSV has the required headers |
| exe not recognized | Add the folder to PATH or use full path |
| R scripts fail | Verify R is installed and in PATH |
| Python module not found | Run `pip install -r requirements.txt` |
| "retailops.exe is not recognized" | Run from the directory containing retailops.exe, or use absolute path |
| CSV validation fails | Check for trailing commas, missing headers, or inconsistent row lengths |
| PowerShell execution blocked | Run with `-ExecutionPolicy Bypass` flag |
| C tool crashes | Verify the input file exists and has the expected format |

### Common Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| `FileLoadError: File not found` | Input CSV missing | Check file path |
| `DataValidationError: Missing column` | CSV lacks required header | Add the required column |
| `DataValidationError: Empty file` | CSV has no data rows | Populate the CSV |
| `ValueError: invalid literal` | Number parse failure | Check data format |
| `ModuleNotFoundError` | Missing Python package | Run `pip install` |

---

## 11. Support

For issues and feature requests, please open an issue on GitHub at:
https://github.com/weidonglang/retailops-cli-suite/issues