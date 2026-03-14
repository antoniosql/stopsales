from __future__ import annotations

from datetime import date
from typing import List

from stopsales.models.pipeline import ValidationIssue
from stopsales.models.stopsales import NormalizedStopSaleEvent


def validate_events(events: List[NormalizedStopSaleEvent]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    for i, ev in enumerate(events):
        if ev.start_date > ev.end_date:
            issues.append(ValidationIssue(
                code="DATE_RANGE_INVALID",
                message=f"Evento {i}: start_date > end_date",
                field="start_date",
                severity="error",
            ))
        # ejemplo de validación adicional:
        # - rangos excesivos
        # - coherencia STOP/OPEN
        # - mercados obligatorios por operador
        # - etc.

    return issues
