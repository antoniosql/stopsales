from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

logger = logging.getLogger(__name__)


@dataclass
class BlobStore:
    account_name: str
    container_raw_emails: str
    container_attachments: str

    def _client(self) -> BlobServiceClient:
        """Crea un BlobServiceClient con Managed Identity / DefaultAzureCredential.

        Requiere RBAC (Storage Blob Data Contributor) para la identidad.
        """
        url = f"https://{self.account_name}.blob.core.windows.net"
        return BlobServiceClient(account_url=url, credential=DefaultAzureCredential())

    def upload_raw_email(self, email_id: str, content: bytes, content_type: str = "message/rfc822") -> str:
        client = self._client()
        container = client.get_container_client(self.container_raw_emails)
        blob_name = f"emails/{email_id}.eml"
        container.upload_blob(
            name=blob_name,
            data=content,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return f"{container.url}/{blob_name}"

    def upload_attachment(self, email_id: str, filename: str, content: bytes, content_type: Optional[str] = None) -> str:
        client = self._client()
        container = client.get_container_client(self.container_attachments)
        safe = filename.replace("/", "_")
        blob_name = f"attachments/{email_id}/{safe}"
        container.upload_blob(
            name=blob_name,
            data=content,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type) if content_type else None,
        )
        return f"{container.url}/{blob_name}"
