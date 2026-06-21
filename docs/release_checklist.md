# Release Checklist

This document outlines the steps required to create a new release of the RetailOps CLI Suite.

---

## Pre-Release Checklist

### 1. Code Quality

- [ ] All Python modules compile without errors (`python -m compileall retailops`)
- [ ] All Python unit tests pass (`python -m unittest discover tests`)
- [ ] All R tests pass (`Rscript tests/test_r_scripts.R`)
- [ ] All C tool tests pass (`powershell -ExecutionPolicy Bypass -File tests/test_c_tools.ps1`)
- [ ] Full test suite passes (`powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1`)

### 2. Data Validation

- [ ] All example CSV files are present and non-empty
- [ ] Example CSV files have correct headers and data types
- [ ] CLI commands produce expected output with example data

### 3. Build Verification

- [ ] Python executable builds successfully (`scripts/build_exe.ps1`)
- [ ] C tools compile successfully (`scripts/build_c_tools.ps1`)
- [ ] `retailops.exe --help` displays help text
- [ ] `retailops.exe sales examples/sales.csv` runs without error
- [ ] `retailops.exe inventory examples/inventory.csv` runs without error
- [ ] `retailops.exe customers examples/customers.csv examples/orders.csv` runs without error
- [ ] `retailops.exe returns examples/returns.csv examples/orders.csv` runs without error
- [ ] `retailops.exe stores examples/stores.csv examples/sales.csv` runs without error
- [ ] `retailops.exe revenue examples/monthly_revenue.csv` runs without error
- [ ] `retailops.exe report --output reports/test_report.md` runs without error
- [ ] `retailops.exe validate examples/sales.csv` runs without error

### 4. C Tool Verification

- [ ] `csv_validate.exe examples/sales.csv 8` runs without error
- [ ] `inventory_check.exe examples/inventory.csv` runs without error
- [ ] `revenue_trend.exe examples/monthly_revenue.csv` runs without error
- [ ] `customer_score.exe examples/customers.csv examples/orders.csv` runs without error

### 5. Documentation

- [ ] README.md is up to date
- [ ] User guide is complete and accurate
- [ ] Developer guide is complete and accurate
- [ ] Data dictionary reflects current CSV schema
- [ ] Release notes are written

---

## Release Process

### Step 1: Run Final Tests

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1
```

### Step 2: Build Executables

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
powershell -ExecutionPolicy Bypass -File scripts/build_c_tools.ps1
```

### Step 3: Verify Line Count

```powershell
powershell -ExecutionPolicy Bypass -File scripts/count_lines.ps1
```

Ensure total lines >= 5000.

### Step 4: Package Release

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_release.ps1
```

### Step 5: Create GitHub Release

```bash
gh release create v1.0.0 release/retailops-cli-suite-v1.0.0.zip --title "RetailOps CLI Suite v1.0.0" --notes-file release/RELEASE_NOTES.md
```

### Step 6: Verify Release

```bash
gh release view v1.0.0
```

---

## Post-Release Checklist

- [ ] Release zip is uploaded as GitHub Release asset
- [ ] Release notes are visible on GitHub
- [ ] Executables are not committed to the git repository
- [ ] Zip file is not committed to the git repository
- [ ] All issues for this milestone are closed
- [ ] Milestone is closed (if applicable)

---

## Version History

| Version | Date | Summary |
|---------|------|---------|
| v1.0.0 | 2026-06-21 | Initial release |

---

## Notes

- Only commit script files and release notes; never commit `.exe` or `.zip` files.
- The release zip is uploaded as a GitHub Release asset, not stored in git.
- All PRs must be merged to `main` before creating a release.