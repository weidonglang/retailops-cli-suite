<#
.SYNOPSIS
    Package RetailOps CLI Suite for release.
.DESCRIPTION
    This script runs all tests, builds executables, and creates a release zip.
.NOTES
    Run with: powershell -ExecutionPolicy Bypass -File scripts/package_release.ps1
#>

#Requires -Version 5.0

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$Version = "v1.0.1"
$ReleaseDir = "$ProjectRoot\release"
$PackageDir = "$ReleaseDir\retailops-cli-suite-$Version"
$ZipPath = "$ReleaseDir\retailops-cli-suite-$Version.zip"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RetailOps CLI Suite - Release Packaging $Version" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Run all tests
Write-Host "Step 1: Running all tests..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$testResult = & "powershell" "-ExecutionPolicy", "Bypass", "-File", "scripts\run_all_tests.ps1" 2>&1
Write-Host $testResult
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Tests failed. Aborting release packaging." -ForegroundColor Red
    exit 1
}
Write-Host "All tests passed." -ForegroundColor Green
Write-Host ""

# Step 2: Build Python executable
Write-Host "Step 2: Building Python executable (retailops.exe)..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

# Clean old build artifacts
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "retailops.spec") { Remove-Item -Force "retailops.spec" }

# Run PyInstaller directly (temporarily disable ErrorActionPreference for stderr)
$originalErrorAction = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    $pyiOutput = python -m PyInstaller --onefile --name retailops retailops/cli.py 2>&1
    $pyiExitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $originalErrorAction
}
if ($pyiExitCode -ne 0) {
    Write-Host "ERROR: PyInstaller build failed with exit code $pyiExitCode" -ForegroundColor Red
    Write-Host $pyiOutput
    exit 1
}
Write-Host "  PyInstaller build completed successfully" -ForegroundColor Green
if (-not (Test-Path "$ProjectRoot\dist\retailops.exe")) {
    Write-Host "ERROR: dist\retailops.exe not found after build." -ForegroundColor Red
    exit 1
}
Write-Host "Python executable built successfully." -ForegroundColor Green
Write-Host ""

# Step 3: Build C tools
Write-Host "Step 3: Building C tools..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$buildCToolsResult = & "powershell" "-ExecutionPolicy", "Bypass", "-File", "scripts\build_c_tools.ps1" 2>&1
Write-Host $buildCToolsResult
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: C tools build failed. Aborting release packaging." -ForegroundColor Red
    exit 1
}
Write-Host "C tools built successfully." -ForegroundColor Green
Write-Host ""

# Step 4: Create package directory
Write-Host "Step 4: Creating package directory..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
if (Test-Path $PackageDir) {
    Remove-Item -Recurse -Force $PackageDir
}
New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null
Write-Host "Created: $PackageDir" -ForegroundColor Gray
Write-Host ""

# Step 5: Copy files to package
Write-Host "Step 5: Copying files to package..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

# Copy Python executable
if (Test-Path "$ProjectRoot\dist\retailops.exe") {
    Copy-Item "$ProjectRoot\dist\retailops.exe" "$PackageDir\retailops.exe"
    Write-Host "  Copied: retailops.exe" -ForegroundColor Gray
}

# Copy C tools
$cToolsDir = "$PackageDir\c_tools"
New-Item -ItemType Directory -Path $cToolsDir -Force | Out-Null
$cToolExes = @("csv_validate.exe", "inventory_check.exe", "revenue_trend.exe", "customer_score.exe")
foreach ($exe in $cToolExes) {
    $src = "$ProjectRoot\dist\c_tools\$exe"
    if (Test-Path $src) {
        Copy-Item $src "$cToolsDir\$exe"
        Write-Host "  Copied: c_tools\$exe" -ForegroundColor Gray
    }
}

# Copy examples
$examplesDir = "$PackageDir\examples"
if (Test-Path "$ProjectRoot\examples") {
    Copy-Item -Recurse "$ProjectRoot\examples" $examplesDir
    Write-Host "  Copied: examples/" -ForegroundColor Gray
}

# Copy docs
$docsDir = "$PackageDir\docs"
if (Test-Path "$ProjectRoot\docs") {
    Copy-Item -Recurse "$ProjectRoot\docs" $docsDir
    Write-Host "  Copied: docs/" -ForegroundColor Gray
}

# Copy README and LICENSE
if (Test-Path "$ProjectRoot\README.md") {
    Copy-Item "$ProjectRoot\README.md" "$PackageDir\README.md"
    Write-Host "  Copied: README.md" -ForegroundColor Gray
}
if (Test-Path "$ProjectRoot\LICENSE") {
    Copy-Item "$ProjectRoot\LICENSE" "$PackageDir\LICENSE"
    Write-Host "  Copied: LICENSE" -ForegroundColor Gray
}

# Copy RELEASE_NOTES.md
if (Test-Path "$ProjectRoot\release\RELEASE_NOTES.md") {
    Copy-Item "$ProjectRoot\release\RELEASE_NOTES.md" "$PackageDir\RELEASE_NOTES.md"
    Write-Host "  Copied: RELEASE_NOTES.md" -ForegroundColor Gray
}
Write-Host ""

# Step 6: Create zip
Write-Host "Step 6: Creating release zip..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
if (Test-Path $ZipPath) {
    Remove-Item -Force $ZipPath
}
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($PackageDir, $ZipPath)
Write-Host "Created: $ZipPath" -ForegroundColor Green
Write-Host ""

# Step 7: Verify package
Write-Host "Step 7: Verifying package..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$zipSize = (Get-Item $ZipPath).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 2)
Write-Host "  Zip size: $zipSizeMB MB" -ForegroundColor Gray

$zipContents = [System.IO.Compression.ZipFile]::OpenRead($ZipPath).Entries.Count
Write-Host "  Files in zip: $zipContents" -ForegroundColor Gray

$hasRetailopsExe = $false
$hasCTools = $false
$hasExamples = $false
$hasDocs = $false
$hasReadme = $false

$entries = [System.IO.Compression.ZipFile]::OpenRead($ZipPath).Entries
foreach ($entry in $entries) {
    $name = $entry.FullName
    if ($name -eq "retailops.exe") { $hasRetailopsExe = $true }
    if ($name -like "c_tools/*") { $hasCTools = $true }
    if ($name -like "examples/*") { $hasExamples = $true }
    if ($name -like "docs/*") { $hasDocs = $true }
    if ($name -eq "README.md") { $hasReadme = $true }
}
$entries.Dispose()

if (-not $hasRetailopsExe) { Write-Host "  WARNING: retailops.exe missing from zip!" -ForegroundColor Red }
if (-not $hasCTools) { Write-Host "  WARNING: c_tools missing from zip!" -ForegroundColor Red }
if (-not $hasExamples) { Write-Host "  WARNING: examples missing from zip!" -ForegroundColor Red }
if (-not $hasDocs) { Write-Host "  WARNING: docs missing from zip!" -ForegroundColor Red }
if (-not $hasReadme) { Write-Host "  WARNING: README.md missing from zip!" -ForegroundColor Red }

Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RELEASE PACKAGING COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Version: $Version" -ForegroundColor White
Write-Host "  Package: $PackageDir" -ForegroundColor White
Write-Host "  Zip: $ZipPath" -ForegroundColor White
Write-Host "  Size: $zipSizeMB MB" -ForegroundColor White
Write-Host ""
Write-Host "  Contents:" -ForegroundColor White
Write-Host "    - retailops.exe (Python CLI)" -ForegroundColor White
Write-Host "    - c_tools/*.exe (4 C utilities)" -ForegroundColor White
Write-Host "    - examples/ (7 CSV datasets)" -ForegroundColor White
Write-Host "    - docs/ (documentation)" -ForegroundColor White
Write-Host "    - README.md" -ForegroundColor White
Write-Host "    - LICENSE" -ForegroundColor White
Write-Host "    - RELEASE_NOTES.md" -ForegroundColor White
Write-Host ""
Write-Host "  To create GitHub release:" -ForegroundColor Yellow
Write-Host "    gh release create $Version $ZipPath --title ""RetailOps CLI Suite $Version"" --notes-file release/RELEASE_NOTES.md" -ForegroundColor Yellow
Write-Host ""

Write-Host "Release packaging complete! Exit code: 0" -ForegroundColor Green
exit 0