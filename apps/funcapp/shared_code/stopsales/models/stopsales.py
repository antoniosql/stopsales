from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class StopSaleAction(str, Enum):
    STOP = "STOP"
    OPEN = "OPEN"


class ExtractedStopSaleEvent(BaseModel):
    """Evento extraído *sin* normalizar (tal cual viene en el correo)."""
    hotel_raw: str
    room_raw: Optional[str] = None
    market_raw: Optional[str] = None
    operator_raw: Optional[str] = None

    action: StopSaleAction
    start_date: date
    end_date: date

    notes: Optional[str] = None
    extraction_confidence: float = Field(default=0.7, ge=0.0, le=1.0)


class NormalizedStopSaleEvent(BaseModel):
    """Evento normalizado, listo para validación y publicación."""
    hotel_code: str
    hotel_name: str

    room_code: Optional[str] = None
    room_name: Optional[str] = None

    market_code: Optional[str] = None
    operator_code: Optional[str] = None

    action: StopSaleAction
    start_date: date
    end_date: date

    # Auditoría
    source_email_id: str
    source_provider: Optional[str] = None
    normalized_at_utc: datetime = Field(default_factory=lambda: datetime.utcnow())
