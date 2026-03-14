import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

import azure.functions as func

from stopsales.config import Settings
from stopsales.catalogs_loader import load_catalogs
from stopsales.foundry.client import FoundryClients
from stopsales.foundry.agents import AgentRunner
from stopsales.integrations.destination_api import DestinationApiClient
from stopsales.integrations.sql_repo import SqlAuditRepository
from stopsales.models.email import EmailEnvelope, EmailAttachment
from stopsales.pipeline.processor import StopSalesProcessor


def _envelope_from_payload(payload: Dict[str, Any]) -> EmailEnvelope:
    attachments = [EmailAttachment(**a) for a in payload.get("attachments", [])]
    received = payload.get("received_utc")
    if received:
        received_dt = datetime.fromisoformat(received.replace("Z", "+00:00"))
    else:
        received_dt = datetime.now(timezone.utc)

    return EmailEnvelope(
        email_id=payload.get("email_id") or payload.get("id") or "unknown",
        subject=payload.get("subject") or "",
        sender=payload.get("sender") or "",
        received_utc=received_dt,
        body_text=payload.get("body_text") or payload.get("body") or "",
        attachments=attachments,
        provider_hint=payload.get("provider_hint"),
        raw_blob_url=payload.get("raw_blob_url"),
    )


def main(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Activity: procesa un correo completo (MVP)."""
    logging.info("ProcessStopSalesActivity started")

    settings = Settings.from_env(env_file=None)  # en Azure Functions vienen como app settings
    catalogs = load_catalogs(None)

    foundry = FoundryClients(project_endpoint=settings.azure_ai_project_endpoint, tenant_id=settings.azure_tenant_id)
    project_client = foundry.create_project_client()
    openai_client = project_client.get_openai_client()
    agent_runner = AgentRunner(project_client=project_client, openai_client=openai_client)

    destination = DestinationApiClient(base_url=settings.destination_api_url, api_key=settings.destination_api_key)
    audit = SqlAuditRepository(server=settings.sql_server_name, database=settings.sql_database_name)

    processor = StopSalesProcessor(
        settings=settings,
        agent_runner=agent_runner,
        catalogs=catalogs,
        destination=destination,
        audit_repo=audit,
    )

    envelope = _envelope_from_payload(payload)
    outcome = processor.process_email(envelope)

    return outcome.model_dump()
