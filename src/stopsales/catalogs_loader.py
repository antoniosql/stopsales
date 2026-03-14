from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stopsales.rules.normalization import Catalogs


def load_catalogs(path: Optional[str] = None) -> Catalogs:
    """Carga catálogos desde JSON (MVP). En industrial: Azure SQL (+AI Search opcional)."""
    if not path:
        # default: data/catalogs/catalogs.json
        path = str(Path(__file__).resolve().parents[2] / "data" / "catalogs" / "catalogs.json")

    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))

    return Catalogs(
        hotels_by_alias={k.lower(): tuple(v) for k, v in data.get("hotels_by_alias", {}).items()},
        rooms_by_alias={k.lower(): tuple(v) for k, v in data.get("rooms_by_alias", {}).items()},
        markets_by_alias={k.lower(): v for k, v in data.get("markets_by_alias", {}).items()},
        operators_by_alias={k.lower(): v for k, v in data.get("operators_by_alias", {}).items()},
    )
