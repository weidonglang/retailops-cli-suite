RetailOps CLI Suite v1.0.1 Release Notes

## Overview

RetailOps CLI Suite v1.0.1 is a maintenance release that addresses several issues identified in the v1.0.0 release. This release improves data validation, error handling, schema consistency, and build/packaging reliability. It also reframes the line counting script as a project file inventory tool.

## Changes from v1.0.0

### Fix #53: data_loader validation pipeline

- Added `require_columns()` to enforce required column headers in all CSV loaders
- All 8 loader functions now validate required columns before processing
- Added error messages that list the missing column names when validation fails
- Consistent validation across sales, inventory, customers, orders, returns, stores, and revenue

### Fix #54: data_loader error handling

- All 8 loader functions now wrap their return in the `load_*()` pattern consistently
- Fixed `load_orders()` and `load_returns()` which previously returned raw data
- All loaders now properly return parsed and validated data
- Ensured consistent error handling throughout the module

### Fix #55: sales/orders schema

- Added proper `ProductName` field to `sales.csv` example data
- Added `StoreID` field to `orders.csv` to enable store-level order analysis
- Updated `load_sales()`, `load_orders()`, and `load_customers()` to validate the new columns
- Data dictionary updated to reflect schema changes

### Fix #56: C tool bounds checks

- Added `is_valid_positive_int()` and `is_valid_non_negative_int()` in `csv_validate.c`
- Added `parse_inventory_item()` with bounds checking in `inventory_check.c`
- Added `parse_revenue_entry()` with validation in `revenue_trend.c`
- Added `validate_customer_id()` and `parse_customer_record()` in `customer_score.c`
- All tools now exit with error code 1 on invalid input

### Fix #57: R script schema boundaries

- Added early-exit checks for empty data in all 4 R scripts
- Added `stopifnot()` column existence checks before column access
- Added `sprintf()` warnings for boundary conditions
- Scripts now exit gracefully with meaningful messages on malformed input

### Fix #58: Python packaging

- Removed `MANIFEST.in` (unnecessary for CLI tool)
- Added `pyproject.toml` with explicit `[tool.setuptools.packages.find]` configuration
- Properly excludes `c_tools`, `examples`, `tests`, `scripts`, `r_scripts`, `docs`, `reports`, `release` directories
- Cleaner package structure and more reliable `pip install`

### Fix #59: Line count script refactor

- Reframed `count_lines.ps1` from a mandatory 5000-line threshold check to a `Project File Inventory` tool
- Removed exit code 1 enforcement on low line counts
- Added per-file detail output sorted by type
- Added structured markdown report generation
- Added `Project Scope Indicators` section for context

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

## Build Instructions

### Build Python Executable

```powershell
python -m PyInstaller --onefile --name retailops retailops/cli.py
```

### Build C Tools

Use the automated scripts:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
powershell -ExecutionPolicy Bypass -File scripts/build_c_tools.ps1
```

### Package Release

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_release.ps1
```

## Known Limitations

1. **Windows Only**: The executables (retailops.exe and C tools) are compiled for Windows x64.
2. **Python Required for Source Usage**: Running from source requires Python 3.8+ installed.
3. **R Required for R Scripts**: R scripts require R 4.0+ installed.
4. **C Compiler Required for C Tool Building**: GCC (MinGW) is required to compile C tools from source.
5. **Data Format Dependent**: All CSV files must follow the expected column headers.
6. **Single-threaded**: Not optimized for very large datasets (millions of rows).
7. **No Database Support**: Currently reads from CSV files only.
8. **No Visualization**: Reports are Markdown/text only.

## File Structure (Release Zip)

```
retailops-cli-suite-v1.0.1/
  retailops.exe          # Python CLI executable
  README.md              # Project documentation
  LICENSE                # MIT license
  RELEASE_NOTES.md       # Release notes
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

## License

MIT License - See LICENSE file for details.