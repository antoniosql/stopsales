<#
.SYNOPSIS
Deploy a Foundry (Azure AI Services) resource and create a project.

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

Require-EnvVar -Name 'FOUNDRY_RESOURCE_NAME'
Require-EnvVar -Name 'FOUNDRY_PROJECT_NAME'

Write-Host "==> Creating Foundry (AIServices) resource with project management enabled"
az cognitiveservices account create `
  --name "$FOUNDRY_RESOURCE_NAME" `
  --resource-group "$RESOURCE_GROUP" `
  --kind AIServices `
  --sku S0 `
  --location "$AZURE_LOCATION" `
  --allow-project-management `
  -o none

Write-Host "==> Setting custom domain (must be globally unique)"
az cognitiveservices account update `
  --name "$FOUNDRY_RESOURCE_NAME" `
  --resource-group "$RESOURCE_GROUP" `
  --custom-domain "$FOUNDRY_RESOURCE_NAME" `
  -o none

Write-Host "==> Creating Foundry project"
az cognitiveservices account project create `
  --name "$FOUNDRY_RESOURCE_NAME" `
  --resource-group "$RESOURCE_GROUP" `
  --project-name "$FOUNDRY_PROJECT_NAME" `
  --location "$AZURE_LOCATION" `
  -o none

$PROJECT_ENDPOINT = "https://$FOUNDRY_RESOURCE_NAME.services.ai.azure.com/api/projects/$FOUNDRY_PROJECT_NAME"

Write-Host "`n==> Foundry project endpoint:"
Write-Host $PROJECT_ENDPOINT
Write-Host "`nAñade/actualiza AZURE_AI_PROJECT_ENDPOINT en tu env file con ese valor."
