<#
.SYNOPSIS
Assign required RBAC roles to the Function App managed identity.

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
Require-EnvVar -Name 'STORAGE_ACCOUNT_NAME'
Require-EnvVar -Name 'SERVICEBUS_NAMESPACE'
Require-EnvVar -Name 'FOUNDRY_RESOURCE_NAME'
Require-EnvVar -Name 'FOUNDRY_PROJECT_NAME'

Write-Host "==> Get principalId of Function App managed identity"
$PRINCIPAL_ID = az functionapp identity show -g "$RESOURCE_GROUP" -n "$FUNCTIONAPP_NAME" --query principalId -o tsv
Write-Host "principalId: $PRINCIPAL_ID"

Write-Host "==> Assign Storage Blob Data Contributor on storage account"
$STORAGE_SCOPE = az storage account show -g "$RESOURCE_GROUP" -n "$STORAGE_ACCOUNT_NAME" --query id -o tsv
az role assignment create --assignee "$PRINCIPAL_ID" --role "Storage Blob Data Contributor" --scope "$STORAGE_SCOPE" -o none | Out-Null

Write-Host "==> Assign Service Bus sender/receiver roles on namespace"
$SB_SCOPE = az servicebus namespace show -g "$RESOURCE_GROUP" -n "$SERVICEBUS_NAMESPACE" --query id -o tsv
az role assignment create --assignee "$PRINCIPAL_ID" --role "Azure Service Bus Data Sender" --scope "$SB_SCOPE" -o none | Out-Null
az role assignment create --assignee "$PRINCIPAL_ID" --role "Azure Service Bus Data Receiver" --scope "$SB_SCOPE" -o none | Out-Null

Write-Host "==> Assign Azure AI User on Foundry project"
$PROJECT_ID = az cognitiveservices account project show `
  --name "$FOUNDRY_RESOURCE_NAME" `
  --resource-group "$RESOURCE_GROUP" `
  --project-name "$FOUNDRY_PROJECT_NAME" `
  --query id -o tsv

az role assignment create --assignee "$PRINCIPAL_ID" --role "Azure AI User" --scope "$PROJECT_ID" -o none | Out-Null

Write-Host "==> Done"
