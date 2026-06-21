<#
.SYNOPSIS
    Count lines of code/documentation/data in the project.
.DESCRIPTION
    Counts lines by file type, excluding generated/build files.
    Exits with 1 if total lines < 5000.
.NOTES
    Run with: powershell -ExecutionPolicy Bypass -File scripts/count_lines.ps1
#>

#Requires -Version 5.0

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$ExcludeDirs = @(".git", "build", "dist", "__pycache__", ".mypy_cache", ".pytest_cache", ".eggs", "*.egg-info")
$ExcludeExtensions = @(".exe", ".zip")

$FileTypes = @{
    ".py"  = "Python"
    ".c"   = "C Source"
    ".R"   = "R Script"
    ".ps1" = "PowerShell"
    ".md"  = "Markdown"
    ".csv" = "CSV Data"
    ".txt" = "Text"
}

function Should-Exclude($path) {
    $relative = $path.Substring($ProjectRoot.Length + 1)
    foreach ($dir in $ExcludeDirs) {
        if ($relative -like "$dir*" -or $relative -like "*\$dir*") {
            return $true
        }
    }
    foreach ($ext in $ExcludeExtensions) {
        if ($path -like "*$ext") {
            return $true
        }
    }
    return $false
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RetailOps CLI Suite - Line Count Report" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$allFiles = Get-ChildItem -Recurse -File | Where-Object { -not (Should-Exclude $_.FullName) }

$typeCounts = @{}
$typeLines = @{}
$fileDetails = @()

$totalFiles = 0
$totalLines = 0

foreach ($file in $allFiles) {
    $ext = $file.Extension.ToLower()
    if (-not $FileTypes.ContainsKey($ext)) {
        continue
    }
    $totalFiles++
    $lineCount = (Get-Content $file.FullName | Measure-Object -Line).Lines
    $totalLines += $lineCount

    $typeName = $FileTypes[$ext]
    $relativePath = $file.FullName.Substring($ProjectRoot.Length + 1)

    $fileDetails += [PSCustomObject]@{
        Type   = $typeName
        File   = $relativePath
        Lines  = $lineCount
    }

    if (-not $typeCounts.ContainsKey($typeName)) {
        $typeCounts[$typeName] = 0
        $typeLines[$typeName] = 0
    }
    $typeCounts[$typeName]++
    $typeLines[$typeName] += $lineCount
}

# Sort file details by type then by lines descending
$fileDetails = $fileDetails | Sort-Object Type, Lines -Descending

# Output per-file details
Write-Host "File Details:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$currentType = ""
foreach ($detail in $fileDetails) {
    if ($detail.Type -ne $currentType) {
        $currentType = $detail.Type
        Write-Host ""
        Write-Host "[$currentType]" -ForegroundColor Green
    }
    Write-Host ("  {0,-60} {1,6} lines" -f $detail.File, $detail.Lines)
}
Write-Host ""

# Output summary
Write-Host "Summary by Type:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host ("{0,-20} {1,8} {2,12}" -f "Type", "Files", "Lines")
Write-Host ("{0,-20} {1,8} {2,12}" -f "----", "-----", "-----")
$sortedTypes = $typeCounts.Keys | Sort-Object
foreach ($type in $sortedTypes) {
    Write-Host ("{0,-20} {1,8} {2,12}" -f $type, $typeCounts[$type], $typeLines[$type])
}
Write-Host ("{0,-20} {1,8} {2,12}" -f "--------", "-----", "-----")
Write-Host ("{0,-20} {1,8} {2,12}" -f "TOTAL", $totalFiles, $totalLines)
Write-Host ""

Write-Host "Total files: $totalFiles" -ForegroundColor White
Write-Host "Total lines: $totalLines" -ForegroundColor White

if ($totalLines -ge 5000) {
    Write-Host "Line count target (5000): PASSED" -ForegroundColor Green
} else {
    Write-Host "Line count target (5000): FAILED ($totalLines < 5000)" -ForegroundColor Red
}

# Write report to docs/line_count_report.md
$reportLines = @()
$reportLines += "# Line Count Report"
$reportLines += ""
$reportLines += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$reportLines += ""
$reportLines += "## File Details"
$reportLines += ""
$reportLines += "| Type | File | Lines |"
$reportLines += "|------|------|-------|"
foreach ($detail in $fileDetails) {
    $escapedFile = $detail.File -replace '\|', '\|'
    $reportLines += "| $($detail.Type) | $escapedFile | $($detail.Lines) |"
}
$reportLines += ""
$reportLines += "## Summary by Type"
$reportLines += ""
$reportLines += "| Type | Files | Lines |"
$reportLines += "|------|-------|-------|"
foreach ($type in $sortedTypes) {
    $reportLines += "| $type | $($typeCounts[$type]) | $($typeLines[$type]) |"
}
$reportLines += "| **TOTAL** | **$totalFiles** | **$totalLines** |"
$reportLines += ""
$reportLines += "## Results"
$reportLines += ""
$reportLines += "- **Total files**: $totalFiles"
$reportLines += "- **Total lines**: $totalLines"
if ($totalLines -ge 5000) {
    $reportLines += "- **Target (5000 lines)**: ✅ PASSED"
} else {
    $reportLines += "- **Target (5000 lines)**: ❌ FAILED"
}
$reportLines += ""

$reportPath = "$ProjectRoot\docs\line_count_report.md"
$reportLines -join "`n" | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host ""
Write-Host "Report written to: docs/line_count_report.md" -ForegroundColor Gray

if ($totalLines -lt 5000) {
    Write-Host "ERROR: Total lines ($totalLines) is less than 5000. Exiting with 1." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Line count check complete. Exit code: 0" -ForegroundColor Green
exit 0