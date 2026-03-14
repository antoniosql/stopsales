from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Catalogs:
    """Catálogos maestros (MVP: in-memory). En industrial: Azure SQL + (opcional) AI Search."""
    hotels_by_alias: Dict[str, Tuple[str, str]]  # alias_lower -> (hotel_code, hotel_name)
    rooms_by_alias: Dict[str, Tuple[str, str]]   # alias_lower -> (room_code, room_name)
    markets_by_alias: Dict[str, str]             # alias_lower -> market_code
    operators_by_alias: Dict[str, str]           # alias_lower -> operator_code


def _norm_key(x: Optional[str]) -> Optional[str]:
    return x.strip().lower() if x else None


def resolve_hotel(catalogs: Catalogs, hotel_raw: str) -> Tuple[str, str]:
    key = _norm_key(hotel_raw) or ""
    if key in catalogs.hotels_by_alias:
        return catalogs.hotels_by_alias[key]
    # fallback naive: usar raw como name/code temporal
    logger.warning("Hotel alias not found: %s", hotel_raw)
    return (f"UNK:{hotel_raw[:20]}", hotel_raw)


def resolve_room(catalogs: Catalogs, room_raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not room_raw:
        return (None, None)
    key = _norm_key(room_raw) or ""
    if key in catalogs.rooms_by_alias:
        return catalogs.rooms_by_alias[key]
    logger.info("Room alias not found: %s", room_raw)
    return (None, room_raw)


def resolve_market(catalogs: Catalogs, market_raw: Optional[str]) -> Optional[str]:
    if not market_raw:
        return None
    key = _norm_key(market_raw) or ""
    return catalogs.markets_by_alias.get(key)


def resolve_operator(catalogs: Catalogs, operator_raw: Optional[str]) -> Optional[str]:
    if not operator_raw:
        return None
    key = _norm_key(operator_raw) or ""
    return catalogs.operators_by_alias.get(key)
