# Release Checklist

This document outlines the steps required to create a new release of the RetailOps CLI Suite. It covers all verification, building, packaging, and publishing steps.

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
- [ ] No duplicate or inconsistent data in CSV files

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
- [ ] All documentation files are at least 50 lines

### 6. Code Statistics

- [ ] Total source code lines >= 5000
- [ ] Line count report is generated (`scripts/count_lines.ps1`)
- [ ] Line count report documents per-file and per-type statistics

### 7. Git State

- [ ] All changes committed to main branch
- [ ] All PRs merged
- [ ] All issues closed
- [ ] Working tree is clean (`git status` shows no modifications)

---

## Release Process

### Step 1: Run Final Tests

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1
```

Expected output: "All tests passed"

If any test fails, fix it before proceeding.

### Step 2: Verify Line Count

```powershell
powershell -ExecutionPolicy Bypass -File scripts/count_lines.ps1
```

Expected output: Total lines >= 5000, exit code 0.

If less than 5000, add more content before proceeding.

### Step 3: Build Executables

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

Expected output: `dist/retailops.exe` created successfully. Smoke test passes.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_c_tools.ps1
```

Expected output: All 4 C tools compiled into `dist/c_tools/`. Smoke test passes.

### Step 4: Package Release

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_release.ps1
```

Expected output: `release/retailops-cli-suite-v1.0.0.zip` created successfully.

### Step 5: Create GitHub Release

```bash
gh release create v1.0.0 release/retailops-cli-suite-v1.0.0.zip --title "RetailOps CLI Suite v1.0.0" --notes-file release/RELEASE_NOTES.md
```

Expected output: Release v1.0.0 created on GitHub.

### Step 6: Verify Release

```bash
gh release view v1.0.0
```

Expected output: Release details with asset `retailops-cli-suite-v1.0.0.zip`.

---

## Verification After Release

### Verify the Release Archive

Anyone who downloads the zip can verify it by:

1. Extracting the archive.
2. Running the commands below.

**Python executable verification:**

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

**C tool verification:**

```powershell
.\c_tools\csv_validate.exe examples/sales.csv 8
.\c_tools\inventory_check.exe examples\inventory.csv
.\c_tools\revenue_trend.exe examples\monthly_revenue.csv
.\c_tools\customer_score.exe examples\customers.csv examples\orders.csv
```

**Documentation check:**

```powershell
Get-ChildItem docs
Get-Content docs/user_guide.md | Measure-Object -Line
```

---

## Post-Release Checklist

- [ ] Release zip is uploaded as GitHub Release asset
- [ ] Release notes are visible on GitHub
- [ ] Executables are not committed to the git repository
- [ ] Zip file is not committed to the git repository
- [ ] All issues for this milestone are closed
- [ ] Milestone is closed (if applicable)
- [ ] Release URL is documented
- [ ] Anyone can download and verify the release

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tests fail | Check error output, fix the failing test, re-run |
| Build fails | Check compiler/PyInstaller errors, ensure dependencies installed |
| Line count < 5000 | Add more code, data, or documentation |
| `gh release create` fails | Check GitHub CLI authentication: `gh auth status` |
| Release asset missing | Re-run `package_release.ps1` and retry |
| Zip extraction fails | Download the zip again, check file integrity |
| Python not found | Install Python 3.10+ and add to PATH |
| R not found | Install R 4.0+ and add to PATH |
| GCC not found | Install MinGW GCC or Visual C++ Build Tools |

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
- Each PR must have exactly one commit and link to exactly one issue.
- If a PR needs changes after creation, use `git commit --amend --no-edit` and force push.
- Do not use `git add .` unless explicitly allowed by the task.

---

## Files Excluded from Git

The following files are listed in `.gitignore` and must never be committed:

- `build/` — PyInstaller build artifacts
- `dist/` — Compiled executables
- `release/*.zip` — Release archives
- `__pycache__/` — Python bytecode cache
- `*.exe` — Executable binaries
- `*.pyc` — Compiled Python files
- `venv/` — Virtual environment