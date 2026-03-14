from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)


@dataclass
class FoundryClients:
    """Wrapper para inicializar AIProjectClient + OpenAI client autenticado.

    El endpoint debe ser el de un *Foundry project*:
      https://<resource>.services.ai.azure.com/api/projects/<project>
    """
    project_endpoint: str
    allow_preview: bool = True
    tenant_id: Optional[str] = None

    def create_project_client(self) -> AIProjectClient:
        # DefaultAzureCredential funciona tanto local (az login) como en Azure (Managed Identity)
        credential = DefaultAzureCredential(
            interactive_browser_tenant_id=self.tenant_id
        ) if self.tenant_id else DefaultAzureCredential()

        client = AIProjectClient(
            endpoint=self.project_endpoint,
            credential=credential,
            allow_preview=self.allow_preview,
        )
        return client

    def create_openai_client(self):
        project_client = self.create_project_client()
        # El openai client soporta Responses + Conversations + Files + etc.
        return project_client.get_openai_client()
