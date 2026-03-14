from __future__ import annotations

# MVP: interface / placeholder.
# En industrial: usa pyodbc / sqlalchemy + Azure SQL con Managed Identity.

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class SqlAuditRepository:
    server: str
    database: str

    def upsert_case(self, case_id: str, data: Dict[str, Any]) -> None:
        """Inserta/actualiza el estado del caso (correo) y su trazabilidad."""
        # TODO: Implementar con Azure SQL
        return

    def save_events(self, case_id: str, events: list[Dict[str, Any]]) -> None:
        """Guarda eventos normalizados para auditoría y reporting."""
        # TODO
        return

    def create_review_case(self, email_id: str, payload: Dict[str, Any]) -> str:
        """Crea un caso pendiente de revisión humana y devuelve su id."""
        # TODO: generar id y persistir
        return f"review:{email_id}"
