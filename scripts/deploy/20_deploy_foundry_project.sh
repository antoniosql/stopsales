#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh" "${ENV_FILE}"

require FOUNDRY_RESOURCE_NAME
require FOUNDRY_PROJECT_NAME

echo "==> Creating Foundry (AIServices) resource with project management enabled"
az cognitiveservices account create \
  --name "${FOUNDRY_RESOURCE_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --kind AIServices \
  --sku S0 \
  --location "${AZURE_LOCATION}" \
  --allow-project-management \
  -o none

echo "==> Setting custom domain (must be globally unique)"
az cognitiveservices account update \
  --name "${FOUNDRY_RESOURCE_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --custom-domain "${FOUNDRY_RESOURCE_NAME}" \
  -o none

echo "==> Creating Foundry project"
az cognitiveservices account project create \
  --name "${FOUNDRY_RESOURCE_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --project-name "${FOUNDRY_PROJECT_NAME}" \
  --location "${AZURE_LOCATION}" \
  -o none

PROJECT_ENDPOINT="https://${FOUNDRY_RESOURCE_NAME}.services.ai.azure.com/api/projects/${FOUNDRY_PROJECT_NAME}"

echo
echo "==> Foundry project endpoint:"
echo "${PROJECT_ENDPOINT}"
echo
echo "Añade/actualiza AZURE_AI_PROJECT_ENDPOINT en tu env file con ese valor."
