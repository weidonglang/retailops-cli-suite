# RetailOps CLI Suite v1.0.1 Release Notes

## Overview

RetailOps CLI Suite is a multi-language command-line retail operations analysis toolkit. It provides analytics for sales, inventory, customers, returns, stores, and monthly revenue data. This release includes a Python CLI application, C language utility tools, R analysis scripts, sample datasets, and comprehensive documentation.

v1.0.1 is a maintenance release that fixes critical bugs and improves robustness across all components.

## What's New in v1.0.1

### Bug Fixes

1. **Data Validation Pipeline (Issue #53)**: Fixed data_loader.py to properly call validators before analysis in all modules. Now `validate_sales_record`, `validate_inventory_record`, etc. are consistently applied before any calculations.

2. **Error Handling (Issue #54)**: Fixed silent error swallowing across the entire codebase. All modules now properly propagate `DataValidationError` and `FileLoadError` exceptions. Removed blanket try/except blocks that were hiding errors.

3. **Sales/Orders Schema (Issue #55)**: Fixed field name inconsistencies between orders.csv columns and the validators/sales modules. Updated CSV headers and validator field references to match: `customer_id`, `product`, `category`, `quantity`, `unit_price`, `total_price`.

4. **C Tool Bounds Checks (Issue #56)**: Added bounds checking to all 4 C tools to prevent buffer overflows on malformed input lines. Added `MAX_LINE` and `MAX_FIELDS` constants, input length validation, and proper error messaging.

5. **R Script Schema Boundaries (Issue #57)**: Fixed R scripts to handle edge cases (empty files, missing columns, single rows). Added defensive checks before field access with `nrow() > 0` and `%in%` column existence checks.

6. **Python Packaging (Issue #58)**: Fixed PyInstaller packaging. Updated package_release.ps1 with proper stderr handling, error checking, and post-build verification of executable existence.

7. **Line Count Script (Issue #59)**: Fixed the count_lines.ps1 script to properly handle encoding on Windows and correctly count `.ps1` and `.c` source files.

### Features

- **Python CLI Application (retailops.exe)**: Sales Analysis, Inventory Analysis, Customer Analysis, Returns Analysis, Store Analysis, Revenue Trend Analysis, Markdown Report Generation, Data Validation
- **C Utility Tools (4 executables)**: CSV validation, inventory check, revenue trend, customer scoring
- **R Analysis Scripts (4 scripts)**: Sales summary, inventory summary, customer segments, revenue forecast
- **Sample Datasets (7 CSV files)**: Realistic retail data for all analysis modules

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
gcc c_tools/csv_validate.c -o dist/c_tools/csv_validate.exe
gcc c_tools/inventory_check.c -o dist/c_tools/inventory_check.exe
gcc c_tools/revenue_trend.c -o dist/c_tools/revenue_trend.exe
gcc c_tools/customer_score.c -o dist/c_tools/customer_score.exe
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
retailops-cli-suite-v1.0.1/
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