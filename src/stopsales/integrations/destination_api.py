from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class DestinationApiClient:
    base_url: str
    api_key: Optional[str] = None
    timeout_s: int = 20

    def publish_stop_sales(self, payload: Dict[str, Any]) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = requests.post(
            self.base_url.rstrip("/"),
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False),
            timeout=self.timeout_s,
        )
        resp.raise_for_status()
        return resp.text
