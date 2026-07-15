[CmdletBinding()]
param(
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot ".")).Path
$venv = Join-Path $env:LOCALAPPDATA "venvs\sentinel-unchained-py311"
$python = Join-Path $venv "Scripts\python.exe"
$env:PIP_REQUIRE_VIRTUALENV = "true"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python Launcher was not found. Install official CPython 3.11 AMD64, then reopen PowerShell."
}

Set-Location $root
if (-not (Test-Path $python)) {
    Write-Host "Creating $venv"
    & py -3.11 -m venv $venv
}

& $python -m pip install --upgrade pip setuptools wheel
& $python -m pip install -r requirements/bootstrap.txt
& $python -m pip install -c requirements/constraints.windows-amd64-cp311.txt -e ".[dev]"
& $python -m pip check

if (-not $SkipTests) {
    & $python -m pytest
    & $python -m ruff check .
    & $python -m ruff format --check .
    & $python -m build
}

Write-Host "READY: $python"
