<#
.SYNOPSIS
    PowerShell test script for C tools in RetailOps CLI Suite.
.DESCRIPTION
    This script compiles, tests, and cleans up C tools.
    Tests include success cases and error cases.
.NOTES
    Run with: powershell -ExecutionPolicy Bypass -File tests/test_c_tools.ps1
#>

#Requires -Version 5.0

$ErrorActionPreference = "Continue"
$Global:TestPassed = 0
$Global:TestFailed = 0
$Global:TestTotal = 0
$Global:AnyFailure = $false

function Write-TestHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "  TEST: $Title" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
}

function Write-SubHeader {
    param([string]$Title)
    Write-Host "  --- $Title" -ForegroundColor Yellow
}

function Assert-ExitCode {
    param(
        [scriptblock]$ScriptBlock,
        [int]$ExpectedExitCode = 0,
        [string]$Message
    )
    $Global:TestTotal++
    try {
        $null = & $ScriptBlock 2>&1
        $exitCode = $LASTEXITCODE
        if ($exitCode -eq $ExpectedExitCode) {
            Write-Host "  [PASS] $Message (exit=$exitCode)" -ForegroundColor Green
            $Global:TestPassed++
        } else {
            Write-Host "  [FAIL] $Message (expected exit=$ExpectedExitCode, actual exit=$exitCode)" -ForegroundColor Red
            $Global:AnyFailure = $true
            $Global:TestFailed++
        }
    } catch {
        Write-Host "  [FAIL] $Message - Exception: $_" -ForegroundColor Red
        $Global:AnyFailure = $true
        $Global:TestFailed++
    }
}

function Assert-OutputContains {
    param(
        [scriptblock]$ScriptBlock,
        [string]$ExpectedSubstring,
        [string]$Message
    )
    $Global:TestTotal++
    try {
        $output = & $ScriptBlock 2>&1 | Out-String
        if ($output -match [regex]::Escape($ExpectedSubstring)) {
            Write-Host "  [PASS] $Message" -ForegroundColor Green
            $Global:TestPassed++
        } else {
            Write-Host "  [FAIL] $Message" -ForegroundColor Red
            Write-Host "         Expected to contain: $ExpectedSubstring" -ForegroundColor Red
            $Global:AnyFailure = $true
            $Global:TestFailed++
        }
    } catch {
        Write-Host "  [FAIL] $Message - Exception: $_" -ForegroundColor Red
        $Global:AnyFailure = $true
        $Global:TestFailed++
    }
}

function Assert-FileExists {
    param(
        [string]$FilePath,
        [string]$Message
    )
    $Global:TestTotal++
    if (Test-Path $FilePath) {
        Write-Host "  [PASS] $Message" -ForegroundColor Green
        $Global:TestPassed++
    } else {
        Write-Host "  [FAIL] $Message (file not found: $FilePath)" -ForegroundColor Red
        $Global:AnyFailure = $true
        $Global:TestFailed++
    }
}

# === Step 1: Build all C tools ===
Write-TestHeader "Step 1: Compile All C Tools"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$CToolsDir = Join-Path $ProjectRoot "c_tools"
$TestDir = $ProjectRoot

Set-Location $ProjectRoot

Write-Host "  Project root: $ProjectRoot" -ForegroundColor Gray
Write-Host "  C tools dir:  $CToolsDir" -ForegroundColor Gray

Write-SubHeader "Compiling csv_validate.c"
gcc "$CToolsDir/csv_validate.c" -o "$TestDir/csv_validate.exe" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "    csv_validate.exe built successfully" -ForegroundColor Green }
else { Write-Host "    csv_validate.exe BUILD FAILED" -ForegroundColor Red; $Global:AnyFailure = $true }

Write-SubHeader "Compiling inventory_check.c"
gcc "$CToolsDir/inventory_check.c" -o "$TestDir/inventory_check.exe" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "    inventory_check.exe built successfully" -ForegroundColor Green }
else { Write-Host "    inventory_check.exe BUILD FAILED" -ForegroundColor Red; $Global:AnyFailure = $true }

Write-SubHeader "Compiling revenue_trend.c"
gcc "$CToolsDir/revenue_trend.c" -o "$TestDir/revenue_trend.exe" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "    revenue_trend.exe built successfully" -ForegroundColor Green }
else { Write-Host "    revenue_trend.exe BUILD FAILED" -ForegroundColor Red; $Global:AnyFailure = $true }

Write-SubHeader "Compiling customer_score.c"
gcc "$CToolsDir/customer_score.c" -o "$TestDir/customer_score.exe" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "    customer_score.exe built successfully" -ForegroundColor Green }
else { Write-Host "    customer_score.exe BUILD FAILED" -ForegroundColor Red; $Global:AnyFailure = $true }

# === Step 2: Verify executables exist ===
Write-TestHeader "Step 2: Verify Executables Exist"

Assert-FileExists -FilePath "$TestDir/csv_validate.exe" -Message "csv_validate.exe exists after compilation"
Assert-FileExists -FilePath "$TestDir/inventory_check.exe" -Message "inventory_check.exe exists after compilation"
Assert-FileExists -FilePath "$TestDir/revenue_trend.exe" -Message "revenue_trend.exe exists after compilation"
Assert-FileExists -FilePath "$TestDir/customer_score.exe" -Message "customer_score.exe exists after compilation"

# === Step 3: Test csv_validate success cases ===
Write-TestHeader "Step 3: Test csv_validate Success Cases"

$salesCsv = "$ProjectRoot/examples/sales.csv"
$inventoryCsv = "$ProjectRoot/examples/inventory.csv"
$customersCsv = "$ProjectRoot/examples/customers.csv"
$ordersCsv = "$ProjectRoot/examples/orders.csv"
$returnsCsv = "$ProjectRoot/examples/returns.csv"
$storesCsv = "$ProjectRoot/examples/stores.csv"
$monthlyRevenueCsv = "$ProjectRoot/examples/monthly_revenue.csv"

Assert-ExitCode -ScriptBlock { & "$TestDir/csv_validate.exe" $salesCsv 10 } -ExpectedExitCode 0 -Message "csv_validate: sales.csv with 10 fields"
Assert-ExitCode -ScriptBlock { & "$TestDir/csv_validate.exe" $inventoryCsv 7 } -ExpectedExitCode 0 -Message "csv_validate: inventory.csv with 7 fields"
Assert-ExitCode -ScriptBlock { & "$TestDir/csv_validate.exe" $customersCsv 5 } -ExpectedExitCode 0 -Message "csv_validate: customers.csv with 5 fields"
Assert-ExitCode -ScriptBlock { & "$TestDir/csv_validate.exe" $ordersCsv 7 } -ExpectedExitCode 0 -Message "csv_validate: orders.csv with 7 fields"
Assert-ExitCode -ScriptBlock { & "$TestDir/csv_validate.exe" $returnsCsv 7 } -ExpectedExitCode 0 -Message "csv_validate: returns.csv with 7 fields"
Assert-ExitCode -ScriptBlock { & "$TestDir/csv_validate.exe" $storesCsv 7 } -ExpectedExitCode 0 -Message "csv_validate: stores.csv with 7 fields"
Assert-ExitCode -ScriptBlock { & "$TestDir/csv_validate.exe" $monthlyRevenueCsv 5 } -ExpectedExitCode 0 -Message "csv_validate: monthly_revenue.csv with 5 fields"

Assert-OutputContains -ScriptBlock { & "$TestDir/csv_validate.exe" $salesCsv 10 } -ExpectedSubstring "Total Data Lines" -Message "csv_validate: output contains Total Data Lines"
Assert-OutputContains -ScriptBlock { & "$TestDir/csv_validate.exe" $inventoryCsv 7 } -ExpectedSubstring "Valid Lines" -Message "csv_validate: output contains Valid Lines"
Assert-OutputContains -ScriptBlock { & "$TestDir/csv_validate.exe" $returnsCsv 7 } -ExpectedSubstring "Invalid Lines" -Message "csv_validate: output contains Invalid Lines"

# === Step 4: Test csv_validate error cases ===
Write-TestHeader "Step 4: Test csv_validate Error Cases"

Assert-ExitCode -ScriptBlock { & "$TestDir/csv_validate.exe" "nonexistent.csv" 5 } -ExpectedExitCode 1 -Message "csv_validate: error on missing file"
Assert-ExitCode -ScriptBlock { & "$TestDir/csv_validate.exe" $salesCsv } -ExpectedExitCode 1 -Message "csv_validate: error on missing expected_fields argument"
Assert-OutputContains -ScriptBlock { & "$TestDir/csv_validate.exe" "nonexistent.csv" 5 } -ExpectedSubstring "ERROR" -Message "csv_validate: missing file shows ERROR"

# === Step 5: Test inventory_check success ===
Write-TestHeader "Step 5: Test inventory_check Success Cases"

Assert-ExitCode -ScriptBlock { & "$TestDir/inventory_check.exe" $inventoryCsv } -ExpectedExitCode 0 -Message "inventory_check: runs successfully"
Assert-OutputContains -ScriptBlock { & "$TestDir/inventory_check.exe" $inventoryCsv } -ExpectedSubstring "Inventory Check" -Message "inventory_check: output contains title"
Assert-OutputContains -ScriptBlock { & "$TestDir/inventory_check.exe" $inventoryCsv } -ExpectedSubstring "Total Items" -Message "inventory_check: output contains Total Items"

# === Step 6: Test inventory_check error ===
Write-TestHeader "Step 6: Test inventory_check Error Cases"

Assert-ExitCode -ScriptBlock { & "$TestDir/inventory_check.exe" "missing.csv" } -ExpectedExitCode 1 -Message "inventory_check: error on missing file"
Assert-ExitCode -ScriptBlock { & "$TestDir/inventory_check.exe" } -ExpectedExitCode 1 -Message "inventory_check: error on missing argument"
Assert-OutputContains -ScriptBlock { & "$TestDir/inventory_check.exe" "missing.csv" } -ExpectedSubstring "ERROR" -Message "inventory_check: missing file shows ERROR"

# === Step 7: Test revenue_trend success ===
Write-TestHeader "Step 7: Test revenue_trend Success Cases"

Assert-ExitCode -ScriptBlock { & "$TestDir/revenue_trend.exe" $monthlyRevenueCsv } -ExpectedExitCode 0 -Message "revenue_trend: runs successfully"
Assert-OutputContains -ScriptBlock { & "$TestDir/revenue_trend.exe" $monthlyRevenueCsv } -ExpectedSubstring "Revenue Trend" -Message "revenue_trend: output contains title"
Assert-OutputContains -ScriptBlock { & "$TestDir/revenue_trend.exe" $monthlyRevenueCsv } -ExpectedSubstring "Total Revenue" -Message "revenue_trend: output contains Total Revenue"

# === Step 8: Test revenue_trend error ===
Write-TestHeader "Step 8: Test revenue_trend Error Cases"

Assert-ExitCode -ScriptBlock { & "$TestDir/revenue_trend.exe" "missing.csv" } -ExpectedExitCode 1 -Message "revenue_trend: error on missing file"
Assert-ExitCode -ScriptBlock { & "$TestDir/revenue_trend.exe" } -ExpectedExitCode 1 -Message "revenue_trend: error on missing argument"

# === Step 9: Test customer_score success ===
Write-TestHeader "Step 9: Test customer_score Success Cases"

Assert-ExitCode -ScriptBlock { & "$TestDir/customer_score.exe" $customersCsv $ordersCsv } -ExpectedExitCode 0 -Message "customer_score: runs successfully"
Assert-OutputContains -ScriptBlock { & "$TestDir/customer_score.exe" $customersCsv $ordersCsv } -ExpectedSubstring "Customer Score" -Message "customer_score: output contains title"
Assert-OutputContains -ScriptBlock { & "$TestDir/customer_score.exe" $customersCsv $ordersCsv } -ExpectedSubstring "TOP 5" -Message "customer_score: output contains TOP 5"

# === Step 10: Test customer_score error ===
Write-TestHeader "Step 10: Test customer_score Error Cases"

Assert-ExitCode -ScriptBlock { & "$TestDir/customer_score.exe" "missing.csv" $ordersCsv } -ExpectedExitCode 1 -Message "customer_score: error on missing customers file"
Assert-ExitCode -ScriptBlock { & "$TestDir/customer_score.exe" $customersCsv "missing.csv" } -ExpectedExitCode 1 -Message "customer_score: error on missing orders file"
Assert-ExitCode -ScriptBlock { & "$TestDir/customer_score.exe" $customersCsv } -ExpectedExitCode 1 -Message "customer_score: error on missing second argument"
Assert-ExitCode -ScriptBlock { & "$TestDir/customer_score.exe" } -ExpectedExitCode 1 -Message "customer_score: error on missing both arguments"

# === Step 11: Print summary ===
Write-TestHeader "Test Summary"

Write-Host ""
Write-Host "  Total tests:  $Global:TestTotal" -ForegroundColor White
Write-Host "  Passed:       $Global:TestPassed" -ForegroundColor Green
Write-Host "  Failed:       $Global:TestFailed" -ForegroundColor Red

if ($Global:AnyFailure) {
    Write-Host ""
    Write-Host "  RESULT: SOME TESTS FAILED" -ForegroundColor Red
} else {
    Write-Host ""
    Write-Host "  RESULT: ALL TESTS PASSED" -ForegroundColor Green
}

# === Step 12: Clean up generated executables ===
Write-TestHeader "Step 12: Clean Up Generated Executables"

$exeFiles = @(
    "$TestDir/csv_validate.exe",
    "$TestDir/inventory_check.exe",
    "$TestDir/revenue_trend.exe",
    "$TestDir/customer_score.exe"
)

foreach ($exe in $exeFiles) {
    if (Test-Path $exe) {
        Remove-Item $exe -Force
        Write-Host "  Removed: $exe" -ForegroundColor Gray
    }
}

Write-Host "  Cleanup complete." -ForegroundColor Green

# === Exit with appropriate code ===
if ($Global:AnyFailure) {
    exit 1
} else {
    exit 0
}