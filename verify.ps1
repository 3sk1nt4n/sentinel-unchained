[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$BundlePath,
    [switch]$Strict
)

$ErrorActionPreference = "Stop"
$python = Join-Path $env:LOCALAPPDATA "venvs\sentinel-unchained-py311\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Validated Python 3.11 environment was not found. Run .\setup.ps1 first."
}

$bundle = (Resolve-Path -LiteralPath $BundlePath -ErrorAction Stop).Path
if ($Strict) {
    & $python -m unchained verify-run $bundle --require-complete --require-live-gpt56
} else {
    & $python -m unchained verify-run $bundle
}
exit $LASTEXITCODE
