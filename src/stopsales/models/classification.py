from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EmailPattern(str, Enum):
    BODY_STRUCTURED = "body_structured"
    PDF_OR_TEXT_ATTACHMENT = "pdf_or_text_attachment"
    VISUAL_OR_CALENDAR_ATTACHMENT = "visual_or_calendar_attachment"
    MULTI_EVENT_COMPLEX = "multi_event_complex"
    UNKNOWN = "unknown"


class EmailClassification(BaseModel):
    pattern: EmailPattern
    provider: Optional[str] = Field(default=None, description="Proveedor / cadena hotelera / formato detectado")
    language: Optional[str] = None

    # Señales para orquestación
    has_attachments: bool = False
    needs_document_intelligence: bool = False
    needs_vision: bool = False

    rationale: Optional[str] = Field(default=None, description="Breve explicación (para auditoría)")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
