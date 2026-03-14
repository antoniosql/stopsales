from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage


@dataclass
class ServiceBusQueue:
    namespace: str
    queue_name: str

    def _client(self) -> ServiceBusClient:
        # Endpoint for AAD auth
        fqdn = f"{self.namespace}.servicebus.windows.net"
        return ServiceBusClient(fqdn=fqdn, credential=DefaultAzureCredential())

    def send(self, payload: Dict[str, Any]) -> None:
        client = self._client()
        with client:
            sender = client.get_queue_sender(queue_name=self.queue_name)
            with sender:
                msg = ServiceBusMessage(json.dumps(payload))
                sender.send_messages(msg)
