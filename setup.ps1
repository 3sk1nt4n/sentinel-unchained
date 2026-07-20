[CmdletBinding()]
param(
    [switch]$SkipTests,
    [switch]$FullTest,
    [switch]$Check
)

Set-StrictMode -Version Latest
$ExpectedPythonVersion = "3.11.9"
$ErrorActionPreference = "Stop"
# Render the box-drawing banners correctly even on a legacy code page. Best-effort.
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
if ($env:OS -ne "Windows_NT") {
    throw "setup.ps1 supports Windows only. Use the documented container workflow elsewhere."
}
if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
    throw "LOCALAPPDATA is unavailable; refusing to guess where to create the isolated environment."
}
$root = (Resolve-Path (Join-Path $PSScriptRoot ".")).Path
$venv = Join-Path $env:LOCALAPPDATA "venvs\sentinel-unchained-py311"
$python = Join-Path $venv "Scripts\python.exe"
$env:PIP_REQUIRE_VIRTUALENV = "true"

function Write-SetupBanner {
    Write-Host ""
    Write-Host "+========================================================================+" -ForegroundColor Cyan
    Write-Host "|                               UNCHAINED                                |" -ForegroundColor White
    Write-Host "|       Autonomous Digital Forensics & Incident Response - GPT-5.6       |" -ForegroundColor Cyan
    Write-Host "|                                                                        |" -ForegroundColor Cyan
    Write-Host "|       Point me at one case. I will show you what is safe to run.       |" -ForegroundColor Gray
    Write-Host "+========================================================================+" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This installer creates one isolated Python environment outside the repo," -ForegroundColor Gray
    Write-Host "installs the pinned toolchain, and proves it is healthy before onboarding." -ForegroundColor Gray
    Write-Host "It does not read evidence, ask for an API key, or call OpenAI." -ForegroundColor Yellow
    Write-Host ""
}

function Assert-NativeSuccess {
    param([Parameter(Mandatory = $true)][string]$Step)

    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE. Fix that step before onboarding."
    }
}

function Test-DockerPresent {
    # Docker is OPTIONAL on Windows (the native venv path is primary) but it is
    # the reliable Linux/macOS route, so we report it either way - never install
    # it silently. Returns $true when a docker CLI is on PATH.
    return [bool](Get-Command docker -ErrorAction SilentlyContinue)
}

function Report-DockerStatus {
    if (Test-DockerPresent) {
        Write-Host "      Docker detected - the isolated container path is available too:" -ForegroundColor Green
        Write-Host "        docker compose run --rm offline        (no key, no evidence, offline)" -ForegroundColor DarkGray
    }
    else {
        Write-Host "      Docker not found - not required on Windows (the native path above is primary)." -ForegroundColor DarkGray
        Write-Host "        For Linux/macOS or full isolation, install Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor DarkGray
    }
}

Write-SetupBanner

if ($Check) {
    # Fast, non-mutating re-verify (mirrors the Qwen './setup.sh --check' habit):
    # confirm the isolated toolchain is healthy WITHOUT reinstalling or testing.
    Write-Host "[check] Verifying the existing isolated environment (no install, no tests)" -ForegroundColor Cyan
    $problems = @()
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        $problems += "Python Launcher 'py' is missing - install official CPython $ExpectedPythonVersion AMD64."
    }
    if (-not (Test-Path $python)) {
        $problems += "Isolated environment is missing at $venv - run setup.ps1 (no -Check) once."
    }
    else {
        & $python -m pip check 2>$null
        if ($LASTEXITCODE -ne 0) { $problems += "Dependency integrity check failed - run setup.ps1 to repair." }
        & $python -c "import unchained" 2>$null
        if ($LASTEXITCODE -ne 0) { $problems += "The 'unchained' package does not import - run setup.ps1 to repair." }
    }
    Report-DockerStatus
    if ($problems.Count -gt 0) {
        Write-Host ""
        Write-Host "NOT READY" -ForegroundColor Yellow
        foreach ($p in $problems) { Write-Host "  - $p" -ForegroundColor Yellow }
        exit 1
    }
    Write-Host ""
    Write-Host "READY - toolchain healthy. Start the whole case with one command:" -ForegroundColor Green
    Write-Host "  sentinel" -ForegroundColor White
    exit 0
}

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python Launcher was not found. Install official CPython 3.11 AMD64, then reopen PowerShell."
}
# Verify 3.11 specifically, not just that the launcher exists, so a missing 3.11
# fails here with a clear message instead of later at 'py -3.11 -m venv'.
& py -3.11 --version > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "CPython 3.11 was not found by the Python Launcher. Install official CPython $ExpectedPythonVersion AMD64 (tick 'Add to PATH'), reopen PowerShell, and rerun setup."
}

Set-Location $root
Write-Host "[1/5] Checking supported CPython $ExpectedPythonVersion AMD64" -ForegroundColor Cyan
if (-not (Test-Path $python)) {
    Write-Host "      Creating an isolated environment outside OneDrive: $venv" -ForegroundColor Gray
    & py -3.11 -m venv $venv
    Assert-NativeSuccess "Python virtual-environment creation"
}
# The probe runs from a file, not -c, because Windows PowerShell 5.1 mangles
# embedded double quotes when building native command lines.
$probeFile = Join-Path ([System.IO.Path]::GetTempPath()) "unchained-python-probe.py"
@'
import json, platform, struct
print(json.dumps({"implementation": platform.python_implementation(), "version": platform.python_version(), "machine": platform.machine(), "address_bits": struct.calcsize("P") * 8}, sort_keys=True))
'@ | Set-Content -Path $probeFile -Encoding ascii
$pythonInfoRaw = @(& $python -I -S $probeFile)
Assert-NativeSuccess "Python version check"
Remove-Item $probeFile -ErrorAction SilentlyContinue
try {
    $pythonInfo = ($pythonInfoRaw -join [Environment]::NewLine) |
        ConvertFrom-Json -ErrorAction Stop
}
catch {
    throw "Python runtime identity was not valid JSON; refusing to install dependencies."
}
$actualPythonVersion = [string]$pythonInfo.version
$supportedMachine = [string]$pythonInfo.machine -in @("AMD64", "x86_64")
if (
    $pythonInfo.implementation -ne "CPython" -or
    $actualPythonVersion -ne $ExpectedPythonVersion -or
    [int]$pythonInfo.address_bits -ne 64 -or
    -not $supportedMachine
) {
    throw "Expected CPython $ExpectedPythonVersion AMD64 (64-bit), but the isolated environment is $($pythonInfo.implementation) $actualPythonVersion $($pythonInfo.machine) $($pythonInfo.address_bits)-bit. Remove only '$venv', install official CPython $ExpectedPythonVersion AMD64, and rerun setup."
}
Write-Host "      PASS  CPython $actualPythonVersion AMD64 (64-bit)" -ForegroundColor Green

Write-Host "[2/5] Installing the pinned bootstrap tools" -ForegroundColor Cyan
& $python -m pip install -q -r requirements/bootstrap.txt
Assert-NativeSuccess "Bootstrap dependency installation"
Write-Host "      PASS  bootstrap tools ready" -ForegroundColor Green

Write-Host "[3/5] Installing Unchained and its constrained DFIR dependencies" -ForegroundColor Cyan
Write-Host "      (first run downloads a few packages - this is the only real wait)" -ForegroundColor Gray
# NON-editable install: the package is COPIED into the isolated venv, so
# `sentinel` keeps working no matter where this folder lives - or even if you
# move or delete it afterwards. An editable (-e) install would pin the clone
# path and break the moment the folder moves (e.g. a OneDrive-redirected
# Documents folder), which is not "install anywhere, works anywhere".
& $python -m pip install -q -c requirements/constraints.windows-amd64-cp311.txt ".[dev]"
Assert-NativeSuccess "Unchained dependency installation"
& $python -m pip check | Out-Null
Assert-NativeSuccess "Dependency integrity check"
Write-Host "      PASS  dependencies installed and consistent" -ForegroundColor Green

if ($SkipTests) {
    Write-Host "[4/5] Verification skipped (-SkipTests)" -ForegroundColor Yellow
}
elseif ($FullTest) {
    Write-Host "[4/5] Running the full developer gate (tests, lint, format, build)" -ForegroundColor Cyan
    & $python -m pytest
    Assert-NativeSuccess "Test suite"
    & $python -m ruff check .
    Assert-NativeSuccess "Ruff lint"
    & $python -m ruff format --check .
    Assert-NativeSuccess "Ruff format check"
    & $python -m build
    Assert-NativeSuccess "Package build"
}
else {
    # Fast, user-facing health check - NOT the developer test suite. Proves the
    # toolchain imports and the CLI responds, in a couple of seconds.
    Write-Host "[4/5] Verifying the toolchain is healthy (fast - not the dev suite)" -ForegroundColor Cyan
    & $python -c "import unchained, openai, volatility3"
    Assert-NativeSuccess "Import check"
    & $python -m unchained --help *> $null
    Assert-NativeSuccess "CLI smoke"
    Write-Host "      PASS  unchained + openai + volatility3 import; the CLI responds" -ForegroundColor Green
    Write-Host "      (want the full test/lint/build gate? run:  .\setup.ps1 -FullTest)" -ForegroundColor DarkGray
}

Write-Host "[5/5] Making 'sentinel' a one-word command in every terminal" -ForegroundColor Cyan
$shimDirectory = Join-Path $env:LOCALAPPDATA "sentinel-unchained\bin"
New-Item -ItemType Directory -Force $shimDirectory | Out-Null
$shim = Join-Path $shimDirectory "sentinel.cmd"
$sentinelExe = Join-Path $venv "Scripts\sentinel.exe"
Set-Content -Path $shim -Value "@echo off`r`n`"$sentinelExe`" %*" -Encoding ascii
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($null -eq $userPath) { $userPath = "" }
if (($userPath -split ";") -notcontains $shimDirectory) {
    [Environment]::SetEnvironmentVariable("Path", ($userPath.TrimEnd(";") + ";" + $shimDirectory), "User")
    Write-Host "      Added one shim folder to your user PATH: $shimDirectory" -ForegroundColor Gray
    Write-Host "      (Only a 2-line sentinel.cmd lives there - nothing else is shadowed.)" -ForegroundColor Gray
}
if (($env:Path -split ";") -notcontains $shimDirectory) {
    $env:Path = $env:Path.TrimEnd(";") + ";" + $shimDirectory
}

Write-Host ""
Report-DockerStatus
Write-Host ""
Write-Host "READY" -ForegroundColor Green
Write-Host ""
Write-Host "+-- ONE COMMAND. IT WALKS YOU THROUGH THE REST. -------------------------+" -ForegroundColor Cyan
Write-Host "| Just run the word below. It profiles one case locally (`$0, no key, no  |" -ForegroundColor White
Write-Host "| OpenAI) shows a verified card, asks the depth, and only then stops for |" -ForegroundColor White
Write-Host "| your explicit launch phrase. No flags, no environment variables.       |" -ForegroundColor White
Write-Host "+------------------------------------------------------------------------+" -ForegroundColor Cyan
Write-Host ""
Write-Host "  sentinel" -ForegroundColor White
Write-Host ""
Write-Host "Or, if you like typing a launcher:  .\unchained.ps1  (does the same thing)." -ForegroundColor Gray
Write-Host "Re-verify anytime without reinstalling:  .\setup.ps1 -Check" -ForegroundColor Gray
Write-Host "Every command is one word from any terminal:" -ForegroundColor Gray
Write-Host "  sentinel  -  sentinel key  -  sentinel doctor  -  sentinel view <bundle>" -ForegroundColor Gray
Write-Host "PATH-restricted environment? The full form always works:" -ForegroundColor DarkGray
Write-Host "  & `"$python`" -m unchained" -ForegroundColor DarkGray
Write-Host "Validated Python: $python" -ForegroundColor DarkGray
