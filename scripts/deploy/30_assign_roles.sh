#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh" "${ENV_FILE}"

require FUNCTIONAPP_NAME
require STORAGE_ACCOUNT_NAME
require SERVICEBUS_NAMESPACE
require FOUNDRY_RESOURCE_NAME
require FOUNDRY_PROJECT_NAME

echo "==> Get principalId of Function App managed identity"
PRINCIPAL_ID=$(az functionapp identity show -g "${RESOURCE_GROUP}" -n "${FUNCTIONAPP_NAME}" --query principalId -o tsv)
echo "principalId: ${PRINCIPAL_ID}"

echo "==> Assign Storage Blob Data Contributor on storage account"
STORAGE_SCOPE=$(az storage account show -g "${RESOURCE_GROUP}" -n "${STORAGE_ACCOUNT_NAME}" --query id -o tsv)
az role assignment create --assignee "${PRINCIPAL_ID}" --role "Storage Blob Data Contributor" --scope "${STORAGE_SCOPE}" -o none || true

echo "==> Assign Service Bus sender/receiver roles on namespace"
SB_SCOPE=$(az servicebus namespace show -g "${RESOURCE_GROUP}" -n "${SERVICEBUS_NAMESPACE}" --query id -o tsv)
az role assignment create --assignee "${PRINCIPAL_ID}" --role "Azure Service Bus Data Sender" --scope "${SB_SCOPE}" -o none || true
az role assignment create --assignee "${PRINCIPAL_ID}" --role "Azure Service Bus Data Receiver" --scope "${SB_SCOPE}" -o none || true

echo "==> Assign Azure AI User on Foundry project"
PROJECT_ID=$(az cognitiveservices account project show \
  --name "${FOUNDRY_RESOURCE_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --project-name "${FOUNDRY_PROJECT_NAME}" \
  --query id -o tsv)

az role assignment create --assignee "${PRINCIPAL_ID}" --role "Azure AI User" --scope "${PROJECT_ID}" -o none || true

echo "==> Done"
