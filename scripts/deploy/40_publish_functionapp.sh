#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh" "${ENV_FILE}"

require FUNCTIONAPP_NAME

echo "==> Setting Function App settings from env file"
# En MVP: volcamos variables de entorno a App Settings.
# En prod: usa Key Vault references para secretos.

SETTINGS_ARGS=()
while IFS= read -r line; do
  # strip CR
  line="${line%$''}"
  [[ -z "${line}" ]] && continue
  [[ "${line}" =~ ^# ]] && continue
  SETTINGS_ARGS+=("${line}")
done < "${ENV_FILE}"

az functionapp config appsettings set \
  --name "${FUNCTIONAPP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --settings "${SETTINGS_ARGS[@]}" \
  -o none

echo "==> Publish function app (requires Azure Functions Core Tools)"
FUNCAPP_DIR="$(cd "${SCRIPT_DIR}/../../apps/funcapp" && pwd)"
cd "${FUNCAPP_DIR}"

if ! command -v func >/dev/null 2>&1; then
  echo "ERROR: Azure Functions Core Tools (func) no está instalado."
  echo "Instálalo y vuelve a ejecutar."
  exit 1
fi

func azure functionapp publish "${FUNCTIONAPP_NAME}" --python

echo "==> Done"
