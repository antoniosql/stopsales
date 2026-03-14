#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-}"
if [[ -z "${ENV_FILE}" ]]; then
  echo "Usage: $0 <path-to-envfile>"
  exit 1
fi
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Env file not found: ${ENV_FILE}"
  exit 1
fi

# shellcheck disable=SC1090
source "${ENV_FILE}"

require() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "Missing env var: ${name}"
    exit 1
  fi
}

require AZURE_SUBSCRIPTION_ID
require AZURE_LOCATION
require RESOURCE_GROUP
require PREFIX

az account set --subscription "${AZURE_SUBSCRIPTION_ID}" >/dev/null
