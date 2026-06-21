# Developer Guide

This guide provides instructions for developers who want to contribute to or extend the RetailOps CLI Suite.

---

## 1. Project Architecture

RetailOps CLI Suite is organized into four language layers:

- **Python** — Core CLI application and analytics engine
- **C** — Standalone performance tools for validation and checking
- **R** — Statistical analysis scripts for segmentation and forecasting
- **PowerShell** — Build, test, and release automation

### 1.1 Directory Layout

```
retailops-cli-suite/
  retailops/       - Python package (CLI + analytics modules)
  c_tools/         - C source files
  r_scripts/       - R analysis scripts
  examples/        - Sample CSV data
  tests/           - Test scripts for all languages
  scripts/         - Build/release automation
  docs/            - Documentation
  reports/         - Generated Markdown reports
  dist/            - Compiled executables (not committed)
  release/         - Release packages (not committed)
```

### 1.2 Python Module Map

```
retailops/
  cli.py           - CLI entrypoint using argparse
  data_loader.py   - CSV file reading and validation
  validators.py    - Field-level data validation
  sales.py         - Sales analytics
  inventory.py     - Inventory analytics
  customers.py     - Customer segmentation
  returns.py       - Returns analytics
  stores.py        - Store performance analytics
  revenue.py       - Revenue trend analytics
  report_builder.py - Markdown report generation
  formatting.py    - Output formatting utilities
  errors.py        - Custom exception classes
  __init__.py      - Package init
```

---

## 2. Setting Up the Development Environment

### 2.1 Prerequisites

Before starting, verify the following tools are installed:

```bash
python --version     # Python 3.10+
gcc --version        # GCC compiler
Rscript --version    # R 4.0+
gh --version         # GitHub CLI
git --version        # Git
```

If any tool is missing, install it before proceeding.

### 2.2 Python Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Requirements (`requirements.txt`):

```text
pyinstaller
```

The entire Python codebase uses only standard library modules except PyInstaller (used only for packaging).

### 2.3 C Compiler

Install MinGW GCC or Microsoft Visual C++ Build Tools.

Verify:

```bash
gcc --version
```

Compile a single C file:

```bash
gcc c_tools/csv_validate.c -o csv_validate.exe
```

### 2.4 R Setup

Install R from https://cran.r-project.org/.

Verify:

```bash
Rscript --version
```

---

## 3. Coding Standards

### 3.1 Python

- Follow PEP 8.
- Use type hints for function signatures.
- Use docstrings for all public functions.
- Use only standard library modules (except PyInstaller for packaging).
- Import order: standard library, third-party, local.
- Maximum line length: 100 characters.
- Use descriptive variable names.

### 3.2 C

- Use ANSI C89/C99 compatible syntax.
- Use `fgets()` for safe line reading.
- Use `strtol()` and `strtod()` for numeric parsing.
- Always check `NULL` and `EOF` conditions.
- Use structs for data grouping.
- Free allocated memory before exit.

### 3.3 R

- Use only base R packages.
- Use `read.csv()` for data loading.
- Use `cat()` for output.
- Use `stop()` or `warning()` for error conditions.
- Use `data.frame` operations for aggregation.
- Use `sprintf()` for formatted output.

### 3.4 PowerShell

- Use `-ExecutionPolicy Bypass` when running scripts.
- Use `$LASTEXITCODE` to check command success.
- Use `Write-Host` or `Write-Output` for output.
- Use `$ErrorActionPreference = "Stop"` to fail on errors.
- Use `param()` blocks for script parameters.

---

## 4. Testing

### 4.1 Python Tests

```bash
python -m unittest discover tests
```

Test files are in `tests/` and use the standard `unittest` framework.

Available test files:
- `tests/test_python_sales.py` - Tests for sales analytics
- `tests/test_python_inventory.py` - Tests for inventory analytics
- `tests/test_python_customers.py` - Tests for customer analytics
- `tests/test_python_cli.py` - Tests for CLI entrypoint

### 4.2 R Tests

```bash
Rscript tests/test_r_scripts.R
```

This runs assertions against all four R analysis scripts.

### 4.3 C Tests

```powershell
powershell -ExecutionPolicy Bypass -File tests/test_c_tools.ps1
```

This compiles and tests all four C tools against example data.

### 4.4 Full Test Suite

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1
```

This runs all tests and CLI commands. Exits with code 1 if any test fails.

### 4.5 Adding New Tests

**Python test example:**

```python
import unittest
from retailops.sales import calculate_total_revenue

class TestSales(unittest.TestCase):
    def test_total_revenue(self):
        orders = [{"total": "100.00"}, {"total": "200.00"}]
        self.assertEqual(calculate_total_revenue(orders), 300.00)
```

**R test example:**

```r
assert_equal <- function(actual, expected, msg) {
    if (actual != expected) {
        stop(paste("FAIL:", msg, "- expected:", expected, "got:", actual))
    }
    cat("PASS:", msg, "\n")
}
```

---

## 5. Building

### 5.1 Build Python Executable

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

This creates `dist/retailops.exe` using PyInstaller with `--onefile` flag.

Build verification:

```powershell
dist/retailops.exe --help
dist/retailops.exe sales examples/sales.csv
```

### 5.2 Build C Tools

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_c_tools.ps1
```

This compiles all C tools into `dist/c_tools/`.

Build verification:

```powershell
dist/c_tools/csv_validate.exe examples/sales.csv 8
dist/c_tools/inventory_check.exe examples/inventory.csv
dist/c_tools/revenue_trend.exe examples/monthly_revenue.csv
dist/c_tools/customer_score.exe examples/customers.csv examples/orders.csv
```

---

## 6. Release Packaging

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_release.ps1
```

This creates `release/retailops-cli-suite-v1.0.0.zip` containing:
- `retailops.exe`
- All C tool executables
- Example CSV data
- Documentation
- License and release notes

### 6.1 Creating a GitHub Release

```bash
gh release create v1.0.0 release/retailops-cli-suite-v1.0.0.zip --title "RetailOps CLI Suite v1.0.0" --notes-file release/RELEASE_NOTES.md
```

---

## 7. Extending the Application

### 7.1 Adding a New Analytics Module

1. Create `retailops/<module>.py` with the required functions.
2. Add a command handler in `retailops/cli.py`.
3. Add tests in `tests/`.
4. Update the report builder if needed.
5. Update documentation.

**Example pattern for a new module:**

```python
from retailops.data_loader import read_csv_rows, require_columns
from retailops.formatting import format_money, format_table

def build_<module>_summary(rows):
    """Build summary from raw data rows."""
    # ... analytics logic ...
    return summary

def print_<module>_summary(summary):
    """Print formatted summary to stdout."""
    # ... printing logic ...

if __name__ == "__main__":
    rows = read_csv_rows("examples/<data>.csv")
    require_columns(rows, ["col1", "col2"])
    summary = build_<module>_summary(rows)
    print_<module>_summary(summary)
```

### 7.2 Adding a New C Tool

1. Create `c_tools/<tool>.c`.
2. Use `fgets()` for file reading and `strtol()/strtod()` for parsing.
3. Use structs to organize data.
4. Add tests in `tests/test_c_tools.ps1`.
5. Update build scripts.

**Example C tool skeleton:**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 1024

typedef struct {
    char name[100];
    double value;
} Record;

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return 1;
    }
    FILE *file = fopen(argv[1], "r");
    if (!file) {
        fprintf(stderr, "Error: Cannot open %s\n", argv[1]);
        return 1;
    }
    char line[MAX_LINE];
    fgets(line, MAX_LINE, file); // skip header
    while (fgets(line, MAX_LINE, file)) {
        // process line
    }
    fclose(file);
    return 0;
}
```

### 7.3 Adding a New R Script

1. Create `r_scripts/<script>.R`.
2. Use only base R functions.
3. Use `read.csv()` for input.
4. Use `cat()` with `sprintf()` for formatted output.
5. Add assertions in `tests/test_r_scripts.R`.

**Example R script skeleton:**

```r
args <- commandArgs(trailingOnly = TRUE)
input_file <- if (length(args) > 0) args[1] else "examples/data.csv"
data <- read.csv(input_file, stringsAsFactors = FALSE)

if (nrow(data) == 0) {
    stop("Empty input file")
}

cat("=== Analysis Summary ===\n")
cat(sprintf("Total: %.2f\n", sum(data$value)))
```

---

## 8. Contribution Workflow

1. Create an Issue describing the feature or fix.
2. Create a branch from `main`: `git checkout -b task/your-task-name`
3. Make changes using a single commit: `git add <files> && git commit -m "Your message"`
4. Open a Pull Request linked to the Issue: `gh pr create --base main --head task/your-task-name --title "..." --body "Closes #N"`
5. Ensure all tests pass.
6. Merge the PR using squash merge: `gh pr merge N --squash --delete-branch`
7. Switch back to main: `git checkout main && git pull origin main`

### 8.1 Commit Rules

- Each PR must contain exactly one commit.
- If changes are needed after PR creation, use `--amend` and force push:
  ```bash
  git add <files>
  git commit --amend --no-edit
  git push --force-with-lease
  ```
- Do NOT use `git add .` unless explicitly allowed.

### 8.2 PR Template

```markdown
## Summary

This PR implements the current RetailOps CLI Suite task.

## Changes

- Added or updated the files required by this task.
- Implemented the requested functionality.
- Added validation, tests, documentation, or build support as required.

## Test

- <list of verification commands>

## Linked Issue

Closes #ISSUE_NUMBER
```

---

## 9. Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-06-21 | Initial release |