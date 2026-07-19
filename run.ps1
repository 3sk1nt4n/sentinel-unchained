[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$EvidencePath,
    [ValidateSet("default", "strict")]
    [string]$Caps = "default",
    [switch]$Live,
    [switch]$SkipSetup
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot ".")).Path
$venv = Join-Path $env:LOCALAPPDATA "venvs\sentinel-unchained-py311"
$python = Join-Path $venv "Scripts\python.exe"

Set-Location $root
if (-not (Test-Path $python)) {
    if ($SkipSetup) {
        throw "-SkipSetup was supplied, but the validated Python environment is missing: $python"
    }
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "setup.ps1") -SkipTests
}

$evidence = (Resolve-Path -LiteralPath $EvidencePath -ErrorAction Stop).Path
if (-not (Test-Path -LiteralPath $evidence)) {
    throw "EvidencePath must be an existing file or directory: $EvidencePath"
}

$env:UNCHAINED_MODEL = "gpt-5.6"
if ($Caps -eq "strict") {
    $env:MAX_TOOL_CALLS = "20"
    $env:MAX_TOTAL_TOKENS = "100000"
    $env:MAX_WALL_SECONDS = "600"
    $env:MAX_COST_USD = "2.50"
} else {
    $env:MAX_TOOL_CALLS = "60"
    $env:MAX_TOTAL_TOKENS = "400000"
    $env:MAX_WALL_SECONDS = "1800"
    $env:MAX_COST_USD = "10"
}

if ($Live) {
    if (-not $env:OPENAI_API_KEY) {
        & (Join-Path $root "scripts\set-openai-key.ps1")
    }
    if (-not $env:OPENAI_API_KEY) {
        throw "The hidden key prompt completed but OPENAI_API_KEY is absent."
    }
} else {
    throw "Live execution is explicit. Add -Live to run the funded GPT-5.6 investigator."
}

& $python -m unchained run $evidence --caps $Caps
exit $LASTEXITCODE
