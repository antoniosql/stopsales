from __future__ import annotations

from dataclasses import dataclass
from typing import List

from stopsales.models.pipeline import ValidationIssue
from stopsales.models.stopsales import ExtractedStopSaleEvent, NormalizedStopSaleEvent


@dataclass
class ConfidenceBreakdown:
    extraction_avg: float
    validation_penalty: float
    final_confidence: float


def compute_confidence(
    extracted: List[ExtractedStopSaleEvent],
    normalized: List[NormalizedStopSaleEvent],
    issues: List[ValidationIssue],
) -> ConfidenceBreakdown:
    """Heurística MVP de confianza.

    En industrial:
    - calibración con dataset y métricas (precision/recall por campo)
    - penalizaciones por mappings desconocidos
    - señales del proveedor/formato
    - tracking de drift
    """
    if not extracted:
        return ConfidenceBreakdown(0.0, 1.0, 0.0)

    extraction_avg = sum(e.extraction_confidence for e in extracted) / len(extracted)
    validation_penalty = 0.0
    for issue in issues:
        if issue.severity == "error":
            validation_penalty += 0.15
        elif issue.severity == "warning":
            validation_penalty += 0.05

    # penaliza eventos sin hotel_code real (UNK)
    unk = sum(1 for e in normalized if e.hotel_code.startswith("UNK:"))
    if normalized:
        validation_penalty += (unk / len(normalized)) * 0.2

    final = max(0.0, min(1.0, extraction_avg - validation_penalty))
    return ConfidenceBreakdown(extraction_avg, validation_penalty, final)
