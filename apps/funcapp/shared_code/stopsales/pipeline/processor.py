from __future__ import annotations

import logging
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional

from stopsales.config import Settings
from stopsales.foundry.agents import AgentRunner
from stopsales.models.classification import EmailClassification, EmailPattern
from stopsales.models.email import EmailEnvelope
from stopsales.models.pipeline import PipelineOutcome, ValidationIssue
from stopsales.models.stopsales import (
    ExtractedStopSaleEvent,
    NormalizedStopSaleEvent,
    StopSaleAction,
)
from stopsales.rules.cleaning import clean_email_body
from stopsales.rules.confidence import compute_confidence
from stopsales.rules.normalization import Catalogs, resolve_hotel, resolve_room, resolve_market, resolve_operator
from stopsales.rules.validation import validate_events
from stopsales.integrations.destination_api import DestinationApiClient
from stopsales.integrations.sql_repo import SqlAuditRepository

logger = logging.getLogger(__name__)

SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "foundry" / "schemas"


class StopSalesProcessor:
    def __init__(
        self,
        *,
        settings: Settings,
        agent_runner: AgentRunner,
        catalogs: Catalogs,
        destination: DestinationApiClient,
        audit_repo: SqlAuditRepository,
    ):
        self.settings = settings
        self.agent_runner = agent_runner
        self.catalogs = catalogs
        self.destination = destination
        self.audit_repo = audit_repo

    def process_email(self, envelope: EmailEnvelope) -> PipelineOutcome:
        """Procesa un correo y devuelve el outcome con decisión PUBLISH/REVIEW."""
        cleaned_body = clean_email_body(envelope.body_text)

        classification = self._classify(envelope, cleaned_body)
        extracted = self._extract(envelope, cleaned_body, classification)
        normalized = self._normalize(envelope, extracted, classification)
        issues = validate_events(normalized)
        conf = compute_confidence(extracted, normalized, issues)

        outcome = PipelineOutcome(
            email_id=envelope.email_id,
            classification=classification,
            extracted_events=extracted,
            normalized_events=normalized,
            validation_issues=issues,
            confidence=conf.final_confidence,
        )

        decision = self._decide(outcome)
        outcome.decision = decision

        # Auditoría (MVP)
        try:
            self.audit_repo.upsert_case(envelope.email_id, outcome.model_dump())
        except Exception:
            logger.exception("Audit upsert failed")

        if decision == "PUBLISH":
            payload = self._build_destination_payload(outcome)
            try:
                resp_text = self.destination.publish_stop_sales(payload)
                outcome.published = True
                outcome.destination_response = resp_text
            except Exception as e:
                # fallo del destino → reintento / DLQ en la capa de orquestación
                outcome.published = False
                outcome.destination_response = str(e)
                outcome.decision = "REVIEW"
                outcome.validation_issues.append(ValidationIssue(
                    code="DESTINATION_ERROR",
                    message=str(e),
                    severity="error",
                ))

        if outcome.decision == "REVIEW":
            try:
                review_id = self.audit_repo.create_review_case(envelope.email_id, outcome.model_dump())
                outcome.review_case_id = review_id
            except Exception:
                logger.exception("Failed creating review case")

        return outcome

    # ---------------------------
    # Steps
    # ---------------------------

    def _classify(self, envelope: EmailEnvelope, cleaned_body: str) -> EmailClassification:
        schema = str(SCHEMAS_DIR / "classify_email.schema.json")
        payload = {
            "subject": envelope.subject,
            "sender": envelope.sender,
            "body": cleaned_body[:8000],
            "attachments": [a.filename for a in envelope.attachments],
        }
        data = self.agent_runner.run_json(
            agent_name=self.settings.agent_classifier_name,
            user_input=json_dumps(payload),
            schema_path=schema,
            temperature=0.0,
        )
        return EmailClassification(**data)

    def _extract(
        self,
        envelope: EmailEnvelope,
        cleaned_body: str,
        classification: EmailClassification,
    ) -> List[ExtractedStopSaleEvent]:
        schema = str(SCHEMAS_DIR / "extract_events.schema.json")

        # MVP: solo body extractor.
        # Industrial: branch por pattern (PDF/visual), ejecutar Document Intelligence, etc.
        extractor_agent = self.settings.agent_body_extractor_name
        input_payload = {
            "subject": envelope.subject,
            "provider": classification.provider or envelope.provider_hint,
            "body": cleaned_body[:12000],
            "attachments": [a.filename for a in envelope.attachments],
            "instruction": "Extrae eventos STOP/OPEN sales y devuélvelos como lista 'events'."
        }
        data = self.agent_runner.run_json(
            agent_name=extractor_agent,
            user_input=json_dumps(input_payload),
            schema_path=schema,
            temperature=0.0,
            max_output_tokens=1800,
        )
        events = []
        for item in data.get("events", []):
            events.append(ExtractedStopSaleEvent(
                hotel_raw=item.get("hotel_raw"),
                room_raw=item.get("room_raw"),
                market_raw=item.get("market_raw"),
                operator_raw=item.get("operator_raw"),
                action=StopSaleAction(item.get("action")),
                start_date=date.fromisoformat(item.get("start_date")),
                end_date=date.fromisoformat(item.get("end_date")),
                notes=item.get("notes"),
                extraction_confidence=float(item.get("extraction_confidence", 0.7)),
            ))
        return events

    def _normalize(
        self,
        envelope: EmailEnvelope,
        extracted: List[ExtractedStopSaleEvent],
        classification: EmailClassification,
    ) -> List[NormalizedStopSaleEvent]:
        normalized: List[NormalizedStopSaleEvent] = []
        for ev in extracted:
            hotel_code, hotel_name = resolve_hotel(self.catalogs, ev.hotel_raw)
            room_code, room_name = resolve_room(self.catalogs, ev.room_raw)
            market_code = resolve_market(self.catalogs, ev.market_raw)
            operator_code = resolve_operator(self.catalogs, ev.operator_raw)

            normalized.append(NormalizedStopSaleEvent(
                hotel_code=hotel_code,
                hotel_name=hotel_name,
                room_code=room_code,
                room_name=room_name,
                market_code=market_code,
                operator_code=operator_code,
                action=ev.action,
                start_date=ev.start_date,
                end_date=ev.end_date,
                source_email_id=envelope.email_id,
                source_provider=classification.provider or envelope.provider_hint,
            ))
        return normalized

    def _decide(self, outcome: PipelineOutcome) -> str:
        has_errors = any(i.severity == "error" for i in outcome.validation_issues)
        if has_errors:
            return "REVIEW"
        if outcome.confidence >= self.settings.confidence_threshold:
            return "PUBLISH"
        return "REVIEW"

    def _build_destination_payload(self, outcome: PipelineOutcome) -> Dict[str, Any]:
        """Construye el JSON final para API destino.

        Ajusta este contrato con tu JSON objetivo real.
        """
        return {
            "email_id": outcome.email_id,
            "provider": outcome.classification.provider,
            "generated_at_utc": datetime.utcnow().isoformat() + "Z",
            "events": [e.model_dump() for e in outcome.normalized_events],
            "confidence": outcome.confidence,
        }


def json_dumps(obj: Any) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False, indent=2)
