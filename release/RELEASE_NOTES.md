# RetailOps CLI Suite v1.0.0 Release Notes

## Overview

RetailOps CLI Suite is a multi-language command-line retail operations analysis toolkit. It provides analytics for sales, inventory, customers, returns, stores, and monthly revenue data. This release includes a Python CLI application, C language utility tools, R analysis scripts, sample datasets, and comprehensive documentation.

## Features

### Python CLI Application (retailops.exe)

- **Sales Analysis**: Calculate total revenue, quantity sold, top products, top categories, top stores
- **Inventory Analysis**: Calculate inventory value, reorder quantities, stock status (OUT_OF_STOCK, LOW_STOCK, OK)
- **Customer Analysis**: Segment customers into VIP, LOYAL, ACTIVE, NEW tiers based on purchase history
- **Returns Analysis**: Calculate return rates, group by reason and product, identify top return reasons
- **Store Analysis**: Group and compare store performance, identify top and lowest performing stores
- **Revenue Trend Analysis**: Monthly revenue totals, averages, growth rates, moving averages
- **Markdown Report Generation**: Generate comprehensive retail analysis reports in Markdown format
- **Data Validation**: Validate CSV data files with detailed error reporting

### C Utility Tools (4 executables)

| Tool | Description |
|------|-------------|
| `csv_validate.exe` | Validate CSV field counts and report line statistics |
| `inventory_check.exe` | Analyze inventory CSV: item count, total stock, low/out-of-stock counts |
| `revenue_trend.exe` | Analyze monthly revenue CSV: totals, averages, best/worst months |
| `customer_score.exe` | Score customers based on order count and revenue, output top 5 |

### R Analysis Scripts

| Script | Description |
|--------|-------------|
| `sales_summary.R` | Sales total revenue, product revenue breakdown, category analysis |
| `inventory_summary.R` | Inventory valuation, low stock alerts, reorder suggestions |
| `customer_segments.R` | Customer segmentation and profile analysis |
| `revenue_forecast.R` | Revenue trends and moving average calculations |

### Sample Datasets

7 CSV datasets with realistic retail data:

- `sales.csv` - 80+ sales transactions
- `inventory.csv` - 40+ inventory items
- `customers.csv` - 50+ customer records
- `orders.csv` - 100+ order records
- `returns.csv` - 25+ return records
- `stores.csv` - 12 store locations
- `monthly_revenue.csv` - 36 months of revenue data

## CLI Commands

```bash
# Sales analysis
retailops.exe sales examples/sales.csv

# Inventory analysis
retailops.exe inventory examples/inventory.csv

# Customer analysis
retailops.exe customers examples/customers.csv examples/orders.csv

# Returns analysis
retailops.exe returns examples/returns.csv examples/orders.csv

# Store analysis
retailops.exe stores examples/stores.csv examples/sales.csv

# Revenue trend analysis
retailops.exe revenue examples/monthly_revenue.csv

# Generate full Markdown report
retailops.exe report --output reports/retail_report.md

# Validate a CSV file
retailops.exe validate examples/sales.csv
```

## Included Executables

1. `retailops.exe` - Main Python CLI application (standalone, no Python required)
2. `c_tools/csv_validate.exe` - CSV field validation tool
3. `c_tools/inventory_check.exe` - Inventory analysis tool
4. `c_tools/revenue_trend.exe` - Revenue trend analysis tool
5. `c_tools/customer_score.exe` - Customer scoring tool

## Test Instructions

### Run All Tests

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1
```

### Run Individual Test Suites

```bash
# Python unit tests
python -m unittest discover tests

# R script tests
Rscript tests/test_r_scripts.R

# C tool tests (compiles and tests all C tools)
powershell -ExecutionPolicy Bypass -File tests/test_c_tools.ps1
```

### Manual Verification

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

## Build Instructions

### Build Python Executable

```powershell
python -m PyInstaller --onefile --name retailops retailops/cli.py
```

### Build C Tools

```powershell
gcc c_tools/csv_validate.c -o c_tools/csv_validate.exe
gcc c_tools/inventory_check.c -o c_tools/inventory_check.exe
gcc c_tools/revenue_trend.c -o c_tools/revenue_trend.exe
gcc c_tools/customer_score.c -o c_tools/customer_score.exe
```

Or use the automated scripts:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
powershell -ExecutionPolicy Bypass -File scripts/build_c_tools.ps1
```

### Package Release

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_release.ps1
```

## Known Limitations

1. **Windows Only**: The executables (retailops.exe and C tools) are compiled for Windows x64. Linux/macOS users can run the Python source directly.
2. **Python Required for Source Usage**: Running from source requires Python 3.8+ installed.
3. **R Required for R Scripts**: R scripts require R 4.0+ installed.
4. **C Compiler Required for C Tool Building**: GCC (MinGW) is required to compile C tools from source.
5. **Data Format Dependent**: All CSV files must follow the expected column headers as defined in the data dictionary.
6. **Single-threaded**: All analysis is single-threaded; not optimized for very large datasets (millions of rows).
7. **No Database Support**: Currently reads from CSV files only; no direct database connectivity.
8. **No Visualization**: Reports are Markdown/text only; no charts or graphs are generated.

## File Structure (Release Zip)

```
retailops-cli-suite-v1.0.0/
  retailops.exe          # Python CLI executable
  README.md              # Project documentation
  LICENSE                # MIT license
  RELEASE_NOTES.md       # This file
  c_tools/
    csv_validate.exe     # CSV validation tool
    inventory_check.exe  # Inventory check tool
    revenue_trend.exe    # Revenue trend tool
    customer_score.exe   # Customer score tool
  examples/
    sales.csv            # Sample sales data
    inventory.csv        # Sample inventory data
    customers.csv        # Sample customer data
    orders.csv           # Sample orders data
    returns.csv          # Sample returns data
    stores.csv           # Sample stores data
    monthly_revenue.csv  # Sample monthly revenue data
  docs/
    data_dictionary.md   # Data dictionary
    user_guide.md        # User guide
    developer_guide.md   # Developer guide
    release_checklist.md # Release checklist
```

## Requirements

- **Windows 10/11** (for executables)
- **Python 3.8+** (for source execution)
- **R 4.0+** (for R analysis scripts)
- **GCC/MinGW** (for C tool compilation from source)
- **PyInstaller** (for Python EXE building from source)

## License

MIT License - See LICENSE file for details.