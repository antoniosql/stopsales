<#
.SYNOPSIS
Publish the Azure Function App and push app settings from an env file.

.PARAMETER EnvFile
Path to an env file containing the needed values (KEY=VALUE).
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$EnvFile
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

. "$PSScriptRoot\lib.ps1" -EnvFile $EnvFile

Require-EnvVar -Name 'FUNCTIONAPP_NAME'

Write-Host "==> Setting Function App settings from env file"

$settingsArgs = @()
Get-Content -Path $EnvFile -ErrorAction Stop | ForEach-Object {
    $line = $_.Trim()
    if ($line -eq '' -or $line.StartsWith('#')) { return }
    $settingsArgs += $line
}

az functionapp config appsettings set `
  --name "$FUNCTIONAPP_NAME" `
  --resource-group "$RESOURCE_GROUP" `
  --settings $settingsArgs `
  -o none

Write-Host "==> Publish function app (requires Azure Functions Core Tools)"

$func = Get-Command func -ErrorAction SilentlyContinue
if (-not $func) {
    Write-Error "Azure Functions Core Tools (func) no está instalado. Instálalo y vuelve a ejecutar."
    exit 1
}

$FUNCAPP_DIR = Join-Path -Path $PSScriptRoot -ChildPath "..\..\apps\funcapp"
Set-Location -Path $FUNCAPP_DIR

func azure functionapp publish $FUNCTIONAPP_NAME --python

Write-Host "==> Done"
