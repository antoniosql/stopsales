<#
.SYNOPSIS
Deploy Azure resources required for the StopSales sample.

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

Require-EnvVar -Name 'STORAGE_ACCOUNT_NAME'
Require-EnvVar -Name 'SERVICEBUS_NAMESPACE'
Require-EnvVar -Name 'SERVICEBUS_QUEUE'
Require-EnvVar -Name 'APP_INSIGHTS_NAME'
Require-EnvVar -Name 'KEYVAULT_NAME'
Require-EnvVar -Name 'FUNCTIONAPP_NAME'
Require-EnvVar -Name 'FUNCTIONAPP_PLAN'

Write-Host "==> Creating resource group"
az group create --name "$RESOURCE_GROUP" --location "$AZURE_LOCATION" -o none

Write-Host "==> Storage account"
az storage account create `
  --name "$STORAGE_ACCOUNT_NAME" `
  --resource-group "$RESOURCE_GROUP" `
  --location "$AZURE_LOCATION" `
  --sku Standard_LRS `
  --kind StorageV2 `
  -o none

Write-Host "==> Blob containers"
$SA_KEY = az storage account keys list -g "$RESOURCE_GROUP" -n "$STORAGE_ACCOUNT_NAME" --query "[0].value" -o tsv

$rawEmailsContainer = if ($env:BLOB_CONTAINER_RAW_EMAILS) { $env:BLOB_CONTAINER_RAW_EMAILS } else { "raw-emails" }
$attachmentsContainer = if ($env:BLOB_CONTAINER_ATTACHMENTS) { $env:BLOB_CONTAINER_ATTACHMENTS } else { "attachments" }

az storage container create --name $rawEmailsContainer --account-name "$STORAGE_ACCOUNT_NAME" --account-key "$SA_KEY" -o none
az storage container create --name $attachmentsContainer --account-name "$STORAGE_ACCOUNT_NAME" --account-key "$SA_KEY" -o none

Write-Host "==> Service Bus"
az servicebus namespace create `
  --name "$SERVICEBUS_NAMESPACE" `
  --resource-group "$RESOURCE_GROUP" `
  --location "$AZURE_LOCATION" `
  --sku Standard `
  -o none

$serviceBusMaxDeliveryCount = if ($env:SERVICEBUS_MAX_DELIVERY_COUNT) { $env:SERVICEBUS_MAX_DELIVERY_COUNT } else { 10 }
az servicebus queue create `
  --name "$SERVICEBUS_QUEUE" `
  --namespace-name "$SERVICEBUS_NAMESPACE" `
  --resource-group "$RESOURCE_GROUP" `
  --max-delivery-count $serviceBusMaxDeliveryCount `
  -o none

Write-Host "==> Application Insights"
az monitor app-insights component create `
  --app "$APP_INSIGHTS_NAME" `
  --location "$AZURE_LOCATION" `
  --resource-group "$RESOURCE_GROUP" `
  --application-type web `
  -o none

Write-Host "==> Key Vault"
az keyvault create `
  --name "$KEYVAULT_NAME" `
  --resource-group "$RESOURCE_GROUP" `
  --location "$AZURE_LOCATION" `
  -o none

Write-Host "==> Function App plan + app (consumption)"
az functionapp plan create `
  --name "$FUNCTIONAPP_PLAN" `
  --resource-group "$RESOURCE_GROUP" `
  --location "$AZURE_LOCATION" `
  --sku Y1 `
  --is-linux `
  -o none

az functionapp create `
  --name "$FUNCTIONAPP_NAME" `
  --resource-group "$RESOURCE_GROUP" `
  --plan "$FUNCTIONAPP_PLAN" `
  --storage-account "$STORAGE_ACCOUNT_NAME" `
  --runtime python `
  --runtime-version 3.11 `
  --functions-version 4 `
  -o none

Write-Host "==> Enable managed identity for Function App"
az functionapp identity assign --name "$FUNCTIONAPP_NAME" --resource-group "$RESOURCE_GROUP" -o none

Write-Host "`n==> Service Bus connection string (para trigger de Azure Functions)"
$SB_CONN = az servicebus namespace authorization-rule keys list `
  --resource-group "$RESOURCE_GROUP" `
  --namespace-name "$SERVICEBUS_NAMESPACE" `
  --name RootManageSharedAccessKey `
  --query primaryConnectionString -o tsv
Write-Host $SB_CONN
Write-Host "Guárdala en Key Vault o en tu env como SERVICEBUS_CONNECTION."

Write-Host "==> Done"
