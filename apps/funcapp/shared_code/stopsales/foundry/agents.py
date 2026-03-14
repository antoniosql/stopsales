from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from azure.ai.projects import AIProjectClient
from jsonschema import validate as jsonschema_validate, ValidationError as JsonSchemaValidationError

logger = logging.getLogger(__name__)


class AgentCallError(RuntimeError):
    pass


@dataclass
class AgentRunner:
    """Ejecutor de agentes *Prompt* (Agent Service) usando el protocolo compatible con OpenAI Responses.

    Patrón recomendado (SDK `azure-ai-projects`):
    - Crear conversación
    - Invocar `responses.create()` con `agent_reference`
    - Obtener `response.output_text`
    - Parsear JSON y validar schema (si aplica)
    """

    project_client: AIProjectClient
    openai_client: Any  # OpenAI client (from openai package)

    def _load_schema(self, schema_path: Optional[str]) -> Optional[dict]:
        if not schema_path:
            return None
        p = Path(schema_path)
        return json.loads(p.read_text(encoding="utf-8"))

    def run_json(
        self,
        *,
        agent_name: str,
        user_input: str,
        schema_path: Optional[str] = None,
        temperature: float = 0.0,
        max_output_tokens: int = 1200,
    ) -> Dict[str, Any]:
        """Ejecuta un agente y fuerza una salida JSON (validada por schema si se proporciona)."""
        # Nota: mantenemos el prompt simple para no acoplar a un SDK concreto de 'structured output'.
        # Si quieres 'strict schema', añade response_format cuando tu modelo lo soporte.
        schema = self._load_schema(schema_path)
        system_hint = (
            "Devuelve SOLO un objeto JSON válido. "
            "No incluyas markdown, ni backticks, ni texto adicional."
        )
        prompt = f"{system_hint}\n\nINPUT:\n{user_input}"

        conversation = self.openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": prompt}],
        )
        try:
            response = self.openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            text = response.output_text.strip()
            data = json.loads(text)

            if schema:
                try:
                    jsonschema_validate(instance=data, schema=schema)
                except JsonSchemaValidationError as e:
                    raise AgentCallError(f"JSON schema validation failed: {e.message}") from e

            return data
        except Exception as e:
            raise AgentCallError(f"Agent '{agent_name}' failed: {e}") from e
        finally:
            # Limpieza best-effort para no dejar conversaciones huérfanas
            try:
                self.openai_client.conversations.delete(conversation_id=conversation.id)
            except Exception:
                logger.debug("Failed to delete conversation %s", conversation.id, exc_info=True)
