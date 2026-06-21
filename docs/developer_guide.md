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

---

## 2. Setting Up the Development Environment

### 2.1 Python Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Requirements:

```text
pyinstaller
```

### 2.2 C Compiler

Install MinGW GCC or Microsoft Visual C++ Build Tools.

Verify:

```bash
gcc --version
```

### 2.3 R Setup

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

### 3.2 C

- Use ANSI C89/C99 compatible syntax.
- Use `fgets()` for safe line reading.
- Use `strtol()` and `strtod()` for numeric parsing.
- Always check `NULL` and `EOF` conditions.

### 3.3 R

- Use only base R packages.
- Use `read.csv()` for data loading.
- Use `cat()` for output.
- Use `stop()` or `warning()` for error conditions.

### 3.4 PowerShell

- Use `-ExecutionPolicy Bypass` when running scripts.
- Use `$LASTEXITCODE` to check command success.
- Use `Write-Host` or `Write-Output` for output.

---

## 4. Testing

### 4.1 Python Tests

```bash
python -m unittest discover tests
```

Test files are in `tests/` and use the standard `unittest` framework.

### 4.2 R Tests

```bash
Rscript tests/test_r_scripts.R
```

### 4.3 C Tests

```powershell
powershell -ExecutionPolicy Bypass -File tests/test_c_tools.ps1
```

### 4.4 Full Test Suite

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1
```

---

## 5. Building

### 5.1 Build Python Executable

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

This creates `dist/retailops.exe` using PyInstaller.

### 5.2 Build C Tools

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_c_tools.ps1
```

This compiles all C tools into `dist/c_tools/`.

---

## 6. Release Packaging

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_release.ps1
```

This creates `release/retailops-cli-suite-v1.0.0.zip`.

---

## 7. Extending the Application

### 7.1 Adding a New Analytics Module

1. Create `retailops/<module>.py` with the required functions.
2. Add a command handler in `retailops/cli.py`.
3. Add tests in `tests/`.
4. Update the report builder if needed.
5. Update documentation.

### 7.2 Adding a New C Tool

1. Create `c_tools/<tool>.c`.
2. Compile with GCC.
3. Add tests in `tests/test_c_tools.ps1`.
4. Update build scripts.

### 7.3 Adding a New R Script

1. Create `r_scripts/<script>.R`.
2. Use only base R functions.
3. Add assertions in `tests/test_r_scripts.R`.

---

## 8. Contribution Workflow

1. Create an Issue describing the feature or fix.
2. Create a branch from `main`.
3. Make changes with a single commit.
4. Open a Pull Request linked to the Issue.
5. Ensure all tests pass.
6. Merge the PR.

---

## 9. Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-06-21 | Initial release |