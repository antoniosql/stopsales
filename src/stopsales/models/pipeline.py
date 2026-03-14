from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field

from .classification import EmailClassification
from .stopsales import ExtractedStopSaleEvent, NormalizedStopSaleEvent


class ValidationIssue(BaseModel):
    code: str
    message: str
    field: Optional[str] = None
    severity: str = Field(default="error", description="error|warning|info")


class PipelineOutcome(BaseModel):
    email_id: str
    classification: EmailClassification
    extracted_events: List[ExtractedStopSaleEvent] = Field(default_factory=list)
    normalized_events: List[NormalizedStopSaleEvent] = Field(default_factory=list)

    validation_issues: List[ValidationIssue] = Field(default_factory=list)

    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    decision: str = Field(default="REVIEW", description="PUBLISH|REVIEW|DROP")

    published: bool = False
    destination_response: Optional[str] = None
    review_case_id: Optional[str] = None
