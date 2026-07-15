<#
.SYNOPSIS
    Prompt for an OpenAI project key without echoing it.

.DESCRIPTION
    The key is assigned only to the current PowerShell process and child
    processes launched from it. It is never written to this repository or
    printed. Close the terminal to remove the process-scoped value.
#>

$ErrorActionPreference = "Stop"
$secret = Read-Host "Paste the new OpenAI project key, then press Enter" -AsSecureString
$pointer = [IntPtr]::Zero

try {
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
    $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
}
finally {
    if ($pointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
    $secret.Dispose()
}

if ($env:OPENAI_API_KEY) {
    Write-Output "OPENAI_API_KEY is present for this PowerShell process."
} else {
    Write-Output "OPENAI_API_KEY is absent."
    exit 1
}
