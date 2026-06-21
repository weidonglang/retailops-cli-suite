<#
.SYNOPSIS
    Build Windows executable for RetailOps CLI Suite using PyInstaller.
.DESCRIPTION
    This script builds retailops.exe from the Python CLI entry point.
    It cleans old build artifacts, runs PyInstaller, and performs smoke tests.
.NOTES
    Run with: powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
    Requires: PyInstaller (pip install pyinstaller)
#>

#Requires -Version 5.0

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RetailOps CLI Suite - Build Windows Executable" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check prerequisites
Write-Host "[Step 1] Checking prerequisites..." -ForegroundColor Yellow

$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not available." -ForegroundColor Red
    exit 1
}
Write-Host "  Python: $pythonVersion" -ForegroundColor Green

$pyinstallerCheck = python -m PyInstaller --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install PyInstaller." -ForegroundColor Red
        exit 1
    }
    Write-Host "  PyInstaller installed successfully." -ForegroundColor Green
} else {
    Write-Host "  PyInstaller: $pyinstallerCheck" -ForegroundColor Green
}

# Step 2: Clean old build artifacts
Write-Host ""
Write-Host "[Step 2] Cleaning old build artifacts..." -ForegroundColor Yellow

if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "  Removed: build/" -ForegroundColor Gray
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "  Removed: dist/" -ForegroundColor Gray
}
if (Test-Path "retailops.spec") {
    Remove-Item -Force "retailops.spec"
    Write-Host "  Removed: retailops.spec" -ForegroundColor Gray
}
Write-Host "  Cleanup complete." -ForegroundColor Green

# Step 3: Build executable with PyInstaller
Write-Host ""
Write-Host "[Step 3] Building retailops.exe with PyInstaller..." -ForegroundColor Yellow

$buildOutput = python -m PyInstaller --onefile --name retailops retailops/cli.py 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller build failed." -ForegroundColor Red
    Write-Host "  $buildOutput" -ForegroundColor Red
    exit 1
}
Write-Host "  PyInstaller build completed." -ForegroundColor Green

# Step 4: Verify executable exists
Write-Host ""
Write-Host "[Step 4] Verifying executable..." -ForegroundColor Yellow

$exePath = "dist/retailops.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "ERROR: $exePath was not created." -ForegroundColor Red
    exit 1
}

$exeInfo = Get-Item $exePath
$exeSize = "{0:N0}" -f $exeInfo.Length
Write-Host "  Executable: $exePath" -ForegroundColor Green
Write-Host "  Size: $exeSize bytes" -ForegroundColor Green
Write-Host "  Created: $($exeInfo.CreationTime)" -ForegroundColor Gray

# Step 5: Smoke test - help
Write-Host ""
Write-Host "[Step 5] Running smoke tests..." -ForegroundColor Yellow

Write-Host "  Test 1: --help" -ForegroundColor Gray
$helpOutput = & "$ProjectRoot/$exePath" --help 2>&1
if ($LASTEXITCODE -eq 0 -and ($helpOutput -match "usage:" -or $helpOutput -match "positional arguments")) {
    Write-Host "    PASS: --help works" -ForegroundColor Green
} else {
    Write-Host "    FAIL: --help did not produce expected output" -ForegroundColor Red
    Write-Host "    Output: $helpOutput" -ForegroundColor Red
    exit 1
}

# Step 6: Smoke test - command execution
Write-Host "  Test 2: sales examples/sales.csv" -ForegroundColor Gray
$salesOutput = & "$ProjectRoot/$exePath" sales "$ProjectRoot/examples/sales.csv" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    PASS: sales command works" -ForegroundColor Green
} else {
    Write-Host "    FAIL: sales command failed" -ForegroundColor Red
    Write-Host "    Output: $salesOutput" -ForegroundColor Red
    exit 1
}

Write-Host "  Test 3: inventory examples/inventory.csv" -ForegroundColor Gray
$inventoryOutput = & "$ProjectRoot/$exePath" inventory "$ProjectRoot/examples/inventory.csv" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    PASS: inventory command works" -ForegroundColor Green
} else {
    Write-Host "    FAIL: inventory command failed" -ForegroundColor Red
    Write-Host "    Output: $inventoryOutput" -ForegroundColor Red
    exit 1
}

Write-Host "  Test 4: customers with orders" -ForegroundColor Gray
$customersOutput = & "$ProjectRoot/$exePath" customers "$ProjectRoot/examples/customers.csv" "$ProjectRoot/examples/orders.csv" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    PASS: customers command works" -ForegroundColor Green
} else {
    Write-Host "    FAIL: customers command failed" -ForegroundColor Red
    Write-Host "    Output: $customersOutput" -ForegroundColor Red
    exit 1
}

Write-Host "  Test 5: validate command" -ForegroundColor Gray
$validateOutput = & "$ProjectRoot/$exePath" validate "$ProjectRoot/examples/sales.csv" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    PASS: validate command works" -ForegroundColor Green
} else {
    Write-Host "    FAIL: validate command failed" -ForegroundColor Red
    Write-Host "    Output: $validateOutput" -ForegroundColor Red
    exit 1
}

# Step 7: Build summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BUILD SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Executable: dist/retailops.exe" -ForegroundColor White
Write-Host "  Size: $exeSize bytes" -ForegroundColor White
Write-Host "  Smoke Tests: All passed" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "NOTE: retailops.exe and build/ directory are not committed to git." -ForegroundColor Yellow
Write-Host "      They are ignored by .gitignore." -ForegroundColor Yellow
Write-Host ""

Write-Host "Build completed successfully!" -ForegroundColor Green