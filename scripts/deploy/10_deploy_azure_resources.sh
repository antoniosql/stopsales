#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh" "${ENV_FILE}"

require STORAGE_ACCOUNT_NAME
require SERVICEBUS_NAMESPACE
require SERVICEBUS_QUEUE
require APP_INSIGHTS_NAME
require KEYVAULT_NAME
require FUNCTIONAPP_NAME
require FUNCTIONAPP_PLAN

echo "==> Creating resource group"
az group create --name "${RESOURCE_GROUP}" --location "${AZURE_LOCATION}" -o none

echo "==> Storage account"
az storage account create \
  --name "${STORAGE_ACCOUNT_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --location "${AZURE_LOCATION}" \
  --sku Standard_LRS \
  --kind StorageV2 \
  -o none

# Containers (requires account key; for RBAC-only environments, create via ARM/Bicep)
echo "==> Blob containers"
SA_KEY=$(az storage account keys list -g "${RESOURCE_GROUP}" -n "${STORAGE_ACCOUNT_NAME}" --query "[0].value" -o tsv)
az storage container create --name "${BLOB_CONTAINER_RAW_EMAILS:-raw-emails}" --account-name "${STORAGE_ACCOUNT_NAME}" --account-key "${SA_KEY}" -o none
az storage container create --name "${BLOB_CONTAINER_ATTACHMENTS:-attachments}" --account-name "${STORAGE_ACCOUNT_NAME}" --account-key "${SA_KEY}" -o none

echo "==> Service Bus"
az servicebus namespace create \
  --name "${SERVICEBUS_NAMESPACE}" \
  --resource-group "${RESOURCE_GROUP}" \
  --location "${AZURE_LOCATION}" \
  --sku Standard \
  -o none

az servicebus queue create \
  --name "${SERVICEBUS_QUEUE}" \
  --namespace-name "${SERVICEBUS_NAMESPACE}" \
  --resource-group "${RESOURCE_GROUP}" \
  --max-delivery-count "${SERVICEBUS_MAX_DELIVERY_COUNT:-10}" \
  -o none

echo "==> Application Insights"
# App Insights crea también un workspace por defecto si no pasas uno; simplificamos MVP
az monitor app-insights component create \
  --app "${APP_INSIGHTS_NAME}" \
  --location "${AZURE_LOCATION}" \
  --resource-group "${RESOURCE_GROUP}" \
  --application-type web \
  -o none

echo "==> Key Vault"
az keyvault create \
  --name "${KEYVAULT_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --location "${AZURE_LOCATION}" \
  -o none

echo "==> Function App plan + app (consumption)"
az functionapp plan create \
  --name "${FUNCTIONAPP_PLAN}" \
  --resource-group "${RESOURCE_GROUP}" \
  --location "${AZURE_LOCATION}" \
  --sku Y1 \
  --is-linux \
  -o none

az functionapp create \
  --name "${FUNCTIONAPP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --plan "${FUNCTIONAPP_PLAN}" \
  --storage-account "${STORAGE_ACCOUNT_NAME}" \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  -o none

echo "==> Enable managed identity for Function App"
az functionapp identity assign --name "${FUNCTIONAPP_NAME}" --resource-group "${RESOURCE_GROUP}" -o none


echo
echo "==> Service Bus connection string (para trigger de Azure Functions)"
SB_CONN=$(az servicebus namespace authorization-rule keys list \
  --resource-group "${RESOURCE_GROUP}" \
  --namespace-name "${SERVICEBUS_NAMESPACE}" \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString -o tsv)
echo "${SB_CONN}"
echo "Guárdala en Key Vault o en tu env como SERVICEBUS_CONNECTION."

echo "==> Done"
