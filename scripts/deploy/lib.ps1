<#
.SYNOPSIS
Common helper functions for deploy scripts.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$EnvFile
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not (Test-Path -Path $EnvFile -PathType Leaf)) {
    Write-Error "Env file not found: $EnvFile"
    exit 1
}

function Load-EnvFile {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )

    Get-Content -Path $Path -ErrorAction Stop | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq '' -or $line.StartsWith('#')) {
            return
        }

        $parts = $line -split '=', 2
        if ($parts.Count -ne 2) {
            return
        }

        $name = $parts[0].Trim()
        $value = $parts[1].Trim()

        if ($value -match '^"(.*)"$') {
            $value = $Matches[1]
        }
        elseif ($value -match "^'(.*)'$") {
            $value = $Matches[1]
        }

        Set-Variable -Name $name -Value $value -Scope Global
        $env:$name = $value
    }
}

function Require-EnvVar {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name
    )

    if ([string]::IsNullOrEmpty($env:$Name)) {
        Write-Error "Missing env var: $Name"
        exit 1
    }
}

Load-EnvFile -Path $EnvFile

Require-EnvVar -Name 'AZURE_SUBSCRIPTION_ID'
Require-EnvVar -Name 'AZURE_LOCATION'
Require-EnvVar -Name 'RESOURCE_GROUP'
Require-EnvVar -Name 'PREFIX'

# Ensure the right Azure subscription is selected
az account set --subscription $env:AZURE_SUBSCRIPTION_ID | Out-Null
