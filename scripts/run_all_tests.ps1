<#
.SYNOPSIS
    Run all tests for RetailOps CLI Suite.
.DESCRIPTION
    This script runs Python unit tests, R script tests, C tool tests,
    and CLI command smoke tests. Any failure causes exit code 1.
.NOTES
    Run with: powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1
#>

#Requires -Version 5.0

$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RetailOps CLI Suite - All Tests" -ForegroundColor Cyan
Write-Host "  Started: $timestamp" -ForegroundColor Cyan
Write-Host "  Directory: $ProjectRoot" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$global:AnyFailed = $false
$global:TestResults = @()

function Run-Test {
    param (
        [string]$Name,
        [string]$Command,
        [int]$ExpectedExitCode = 0
    )

    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Host "  TEST: $Name" -ForegroundColor Yellow
    Write-Host "  Command: $Command" -ForegroundColor Gray
    Write-Host "----------------------------------------" -ForegroundColor Gray

    $output = Invoke-Expression $Command 2>&1
    $exitCode = $LASTEXITCODE

    Write-Host $output

    if ($exitCode -eq $ExpectedExitCode) {
        Write-Host ""
        Write-Host "  PASS: $Name (exit code $exitCode)" -ForegroundColor Green
        $global:TestResults += @{ Name = $Name; Status = "PASS" }
    } else {
        Write-Host ""
        Write-Host "  FAIL: $Name (expected exit $ExpectedExitCode, got $exitCode)" -ForegroundColor Red
        $global:TestResults += @{ Name = $Name; Status = "FAIL" }
        $global:AnyFailed = $true
    }
    Write-Host ""
}

# ============================================================
# Section 1: Python unit tests
# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SECTION 1: Python Unit Tests" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Run-Test -Name "Python unit tests (unittest discover)" -Command "python -m unittest discover tests"

# ============================================================
# Section 2: R script tests
# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SECTION 2: R Script Tests" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Run-Test -Name "R script tests" -Command "Rscript tests/test_r_scripts.R"

# ============================================================
# Section 3: C tool tests
# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SECTION 3: C Tool Tests" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# First build C tools for testing
Write-Host "Building C tools for testing..." -ForegroundColor Gray
$buildOutput = & "powershell" "-ExecutionPolicy", "Bypass", "-File", "tests/test_c_tools.ps1" 2>&1
$buildExitCode = $LASTEXITCODE
Write-Host $buildOutput

if ($buildExitCode -eq 0) {
    Write-Host "  PASS: C tool tests" -ForegroundColor Green
    $global:TestResults += @{ Name = "C tool tests"; Status = "PASS" }
} else {
    Write-Host "  FAIL: C tool tests (exit code $buildExitCode)" -ForegroundColor Red
    $global:TestResults += @{ Name = "C tool tests"; Status = "FAIL" }
    $global:AnyFailed = $true
}

# ============================================================
# Section 4: CLI smoke tests
# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SECTION 4: CLI Smoke Tests" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Run-Test -Name "CLI sales module" -Command "python -m retailops.cli sales examples/sales.csv"
Run-Test -Name "CLI inventory module" -Command "python -m retailops.cli inventory examples/inventory.csv"
Run-Test -Name "CLI report generation" -Command "python -m retailops.cli report --output reports/generated_report.md"

# ============================================================
# Summary
# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$passCount = ($global:TestResults | Where-Object { $_.Status -eq "PASS" }).Count
$failCount = ($global:TestResults | Where-Object { $_.Status -eq "FAIL" }).Count
$totalCount = $global:TestResults.Count

foreach ($result in $global:TestResults) {
    $symbol = if ($result.Status -eq "PASS") { "[PASS]" } else { "[FAIL]" }
    $color = if ($result.Status -eq "PASS") { "Green" } else { "Red" }
    Write-Host "  $symbol $($result.Name)" -ForegroundColor $color
}

Write-Host ""
Write-Host "  Total: $totalCount, Passed: $passCount, Failed: $failCount" -ForegroundColor White
Write-Host ""

if ($global:AnyFailed) {
    Write-Host "  Some tests FAILED." -ForegroundColor Red
    Write-Host "  Exit code: 1" -ForegroundColor Red
    exit 1
} else {
    Write-Host "  All tests passed!" -ForegroundColor Green
    Write-Host "  Exit code: 0" -ForegroundColor Green
    Write-Host "  All tests passed" > $null
    Write-Host "============================================================" -ForegroundColor Cyan
    exit 0
}