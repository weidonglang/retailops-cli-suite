# retailops-cli-suite

A multi-language retail operations CLI toolkit with analytics, tests, Windows executables, and release packaging.

RetailOps CLI Suite is a command-line retail operations analysis tool for analyzing sales, inventory, customers, returns, stores, and monthly revenue data.

---

## Features

- **Sales Analysis** — Total revenue, quantity, top products, categories, and stores
- **Inventory Management** — Stock valuation, reorder points, stock status (OK, LOW, OUT)
- **Customer Segmentation** — VIP, Loyal, Active, New customer tiers
- **Returns Analysis** — Return rates, top reasons, top returned products
- **Store Performance** — Per-store revenue, averages, top/lowest performers
- **Revenue Trends** — Growth rates, moving averages, best/worst months
- **Markdown Reporting** — Comprehensive report generation
- **CSV Validation** — Data structure and field validation

## Supported Languages

- **Python** — Core CLI application (PyInstaller packaged as `retailops.exe`)
- **C** — Standalone tools: `csv_validate.exe`, `inventory_check.exe`, `revenue_trend.exe`, `customer_score.exe`
- **R** — Analysis scripts: `sales_summary.R`, `inventory_summary.R`, `customer_segments.R`, `revenue_forecast.R`

---

## Quick Start

### Option 1: Download the Release

Download `retailops-cli-suite-v1.0.0.zip` from the Releases page and extract it. Then run:

```powershell
.\retailops.exe --help
.\retailops.exe sales examples/sales.csv
.\retailops.exe inventory examples/inventory.csv
```

### Option 2: Run from Source

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

## Installation

```bash
# Clone the repository
git clone https://github.com/weidonglang/retailops-cli-suite.git
cd retailops-cli-suite

# Install Python dependencies
pip install -r requirements.txt
```

---

## Running Tests

```powershell
# Full test suite
powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1

# Python unit tests only
python -m unittest discover tests

# R tests only
Rscript tests/test_r_scripts.R

# C tool tests only
powershell -ExecutionPolicy Bypass -File tests/test_c_tools.ps1
```

---

## Building

### Build Python Executable

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

Creates `dist/retailops.exe`.

### Build C Tools

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_c_tools.ps1
```

Creates executables in `dist/c_tools/`.

### Package Release

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_release.ps1
```

Creates `release/retailops-cli-suite-v1.0.0.zip`.

---

## Project Structure

```
retailops-cli-suite/
  retailops/       - Python package (CLI + analytics modules)
  c_tools/         - C source files
  r_scripts/       - R analysis scripts
  examples/        - Sample CSV data
  tests/           - Test scripts
  scripts/         - Build/release automation
  docs/            - Documentation
```

---

## Documentation

- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)
- [Data Dictionary](docs/data_dictionary.md)
- [Release Checklist](docs/release_checklist.md)

---

## License

[MIT](LICENSE)

---

## Version

v1.0.0