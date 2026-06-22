<#
.SYNOPSIS
    Build all C tools for RetailOps CLI Suite.
.DESCRIPTION
    This script compiles the four C tools from c_tools/ into dist/c_tools/
    and runs smoke tests on each executable.
.NOTES
    Run with: powershell -ExecutionPolicy Bypass -File scripts/build_c_tools.ps1
    Requires: gcc (MinGW or similar)
#>

#Requires -Version 5.0

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RetailOps CLI Suite - Build C Tools" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check prerequisites
Write-Host "[Step 1] Checking prerequisites..." -ForegroundColor Yellow

$gccVersion = gcc --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: gcc is not available. Install MinGW or similar." -ForegroundColor Red
    exit 1
}
$firstLine = ($gccVersion -split "`n")[0]
Write-Host "  gcc: $firstLine" -ForegroundColor Green

# Step 2: Create output directory
Write-Host ""
Write-Host "[Step 2] Creating output directory..." -ForegroundColor Yellow

$outputDir = "dist/c_tools"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "  Created: $outputDir" -ForegroundColor Gray
} else {
    Write-Host "  Directory exists: $outputDir" -ForegroundColor Gray
}

# Step 3: Define tools to build
$tools = @(
    @{ Name = "csv_validate"; Source = "c_tools/csv_validate.c"; Description = "CSV field validator" },
    @{ Name = "inventory_check"; Source = "c_tools/inventory_check.c"; Description = "Inventory stock checker" },
    @{ Name = "revenue_trend"; Source = "c_tools/revenue_trend.c"; Description = "Revenue trend analyzer" },
    @{ Name = "customer_score"; Source = "c_tools/customer_score.c"; Description = "Customer scoring engine" }
)

$buildResults = @()

Write-Host ""
Write-Host "[Step 3] Compiling C tools..." -ForegroundColor Yellow

foreach ($tool in $tools) {
    $sourceFile = $tool.Source
    $outputExe = "$outputDir/$($tool.Name).exe"

    Write-Host "  Building: $($tool.Name) ($($tool.Description))" -ForegroundColor Gray
    Write-Host "    Source: $sourceFile" -ForegroundColor Gray
    Write-Host "    Output: $outputExe" -ForegroundColor Gray

    if (-not (Test-Path $sourceFile)) {
        Write-Host "    ERROR: Source file $sourceFile not found!" -ForegroundColor Red
        $buildResults += @{ Name = $tool.Name; Status = "FAIL"; Reason = "Source file missing" }
        continue
    }

    $compileOutput = gcc $sourceFile -o $outputExe 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    FAIL: Compilation error" -ForegroundColor Red
        Write-Host "    $compileOutput" -ForegroundColor Red
        $buildResults += @{ Name = $tool.Name; Status = "FAIL"; Reason = "Compilation error" }
        continue
    }

    if (-not (Test-Path $outputExe)) {
        Write-Host "    FAIL: Output exe not created" -ForegroundColor Red
        $buildResults += @{ Name = $tool.Name; Status = "FAIL"; Reason = "Output not found" }
        continue
    }

    $exeInfo = Get-Item $outputExe
    $exeSize = "{0:N0}" -f $exeInfo.Length
    Write-Host "    OK: Compiled successfully ($exeSize bytes)" -ForegroundColor Green
    $buildResults += @{ Name = $tool.Name; Status = "OK" }
}

# Step 4: Summary
Write-Host ""
Write-Host "[Step 4] Build summary..." -ForegroundColor Yellow

$allOk = $true
foreach ($result in $buildResults) {
    if ($result.Status -eq "OK") {
        Write-Host "  $($result.Name): OK" -ForegroundColor Green
    } else {
        Write-Host "  $($result.Name): FAIL - $($result.Reason)" -ForegroundColor Red
        $allOk = $false
    }
}

if (-not $allOk) {
    Write-Host "ERROR: One or more tools failed to build." -ForegroundColor Red
    exit 1
}

# Step 5: Smoke tests
Write-Host ""
Write-Host "[Step 5] Running smoke tests..." -ForegroundColor Yellow

$smokeTests = @(
    @{ Exe = "csv_validate.exe"; Args = @("examples/sales.csv", "10"); Desc = "CSV validate with sales.csv" },
    @{ Exe = "inventory_check.exe"; Args = @("examples/inventory.csv"); Desc = "Inventory check" },
    @{ Exe = "revenue_trend.exe"; Args = @("examples/monthly_revenue.csv"); Desc = "Revenue trend" },
    @{ Exe = "customer_score.exe"; Args = @("examples/customers.csv", "examples/orders.csv"); Desc = "Customer score" }
)

$smokeAllOk = $true
foreach ($test in $smokeTests) {
    $exePath = "$outputDir/$($test.Exe)"
    Write-Host "  Test: $($test.Desc)" -ForegroundColor Gray

    if (-not (Test-Path $exePath)) {
        Write-Host "    FAIL: Executable $exePath not found" -ForegroundColor Red
        $smokeAllOk = $false
        continue
    }

    # Resolve full paths for arguments
    $resolvedArgs = @()
    foreach ($arg in $test.Args) {
        if ($arg -like "examples/*") {
            $resolvedArgs += "$ProjectRoot/$arg"
        } else {
            $resolvedArgs += $arg
        }
    }

    $testOutput = & $exePath $resolvedArgs 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    PASS (exit code 0)" -ForegroundColor Green
    } else {
        Write-Host "    FAIL (exit code $LASTEXITCODE)" -ForegroundColor Red
        Write-Host "    Output: $testOutput" -ForegroundColor Red
        $smokeAllOk = $false
    }
}

if (-not $smokeAllOk) {
    Write-Host ""
    Write-Host "ERROR: Some smoke tests failed." -ForegroundColor Red
    exit 1
}

# Step 6: Final summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BUILD SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Output directory: $outputDir" -ForegroundColor White
Get-ChildItem $outputDir -Filter "*.exe" | ForEach-Object {
    $size = "{0:N0}" -f $_.Length
    Write-Host "    $($_.Name) ($size bytes)" -ForegroundColor White
}
Write-Host "  Smoke Tests: All passed" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "NOTE: C executables are not committed to git." -ForegroundColor Yellow
Write-Host "      They are ignored by .gitignore." -ForegroundColor Yellow
Write-Host ""

Write-Host "C tools build completed successfully!" -ForegroundColor Green