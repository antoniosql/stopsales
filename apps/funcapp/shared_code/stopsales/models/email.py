from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class EmailAttachment(BaseModel):
    filename: str
    content_type: Optional[str] = None

    # En cloud se guarda en Blob y aquí se referencia por URL.
    blob_url: Optional[str] = None

    # Para local/testing (no recomendado en prod)
    content_bytes_b64: Optional[str] = None


class EmailEnvelope(BaseModel):
    """Representación canónica del correo para la pipeline.

    Idea clave: toda la trazabilidad cuelga de `email_id`.
    """
    email_id: str = Field(..., description="Id interno (Graph id / Message-Id / hash)")
    subject: str
    sender: str
    received_utc: datetime
    body_text: str
    attachments: List[EmailAttachment] = Field(default_factory=list)

    # Metadatos útiles
    provider_hint: Optional[str] = None  # Iberostar, Bahia, Barcelo, LIVVO...
    raw_blob_url: Optional[str] = None   # ubicación del .eml/.msg raw en Blob
