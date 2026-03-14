#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from stopsales.config import Settings
from stopsales.logging import configure_logging
from stopsales.catalogs_loader import load_catalogs
from stopsales.foundry.client import FoundryClients
from stopsales.foundry.agents import AgentRunner
from stopsales.integrations.destination_api import DestinationApiClient
from stopsales.integrations.sql_repo import SqlAuditRepository
from stopsales.models.email import EmailEnvelope, EmailAttachment
from stopsales.pipeline.processor import StopSalesProcessor


def read_msg_as_envelope(path: str) -> EmailEnvelope:
    try:
        import extract_msg
    except ImportError as e:
        raise RuntimeError("Instala 'extract-msg' para procesar .msg en local") from e

    msg = extract_msg.Message(path)
    msg.process()

    email_id = Path(path).stem
    sender = msg.sender or "unknown"
    subject = msg.subject or "(no subject)"
    body = msg.body or ""

    attachments = []
    for att in msg.attachments:
        # extract-msg deja el fichero en disco; aquí solo guardamos el nombre
        attachments.append(EmailAttachment(filename=att.longFilename or att.shortFilename or "attachment"))

    return EmailEnvelope(
        email_id=email_id,
        subject=subject,
        sender=sender,
        received_utc=datetime.now(timezone.utc),
        body_text=body,
        attachments=attachments,
        provider_hint=None,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, help="Ruta al fichero .env")
    parser.add_argument("--samples", required=True, help="Carpeta con .msg")
    parser.add_argument("--catalogs", default=None, help="Ruta a catalogs.json")
    args = parser.parse_args()

    configure_logging()
    settings = Settings.from_env(args.env)

    catalogs = load_catalogs(args.catalogs)

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

    files = sorted(glob.glob(os.path.join(args.samples, "*.msg")))
    if not files:
        print("No .msg files found in", args.samples)
        return

    for f in files:
        print("\n---\nProcessing", f)
        env = read_msg_as_envelope(f)
        outcome = processor.process_email(env)
        print(outcome.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
