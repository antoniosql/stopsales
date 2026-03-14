from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

# MVP: stub in-memory.
# En industrial: Azure SQL para casos + Blob para evidencias + Service Bus para re-proceso.

app = FastAPI(title="StopSales Review API", version="0.1")

_CASES: Dict[str, Dict[str, Any]] = {}


class ReviewDecision(BaseModel):
    corrected_payload: Dict[str, Any]
    action: str  # APPROVE | REJECT


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/cases")
def list_cases() -> List[Dict[str, Any]]:
    return list(_CASES.values())


@app.get("/cases/{case_id}")
def get_case(case_id: str) -> Dict[str, Any]:
    if case_id not in _CASES:
        raise HTTPException(status_code=404, detail="Case not found")
    return _CASES[case_id]


@app.post("/cases/{case_id}/decision")
def decide(case_id: str, decision: ReviewDecision) -> Dict[str, Any]:
    if case_id not in _CASES:
        raise HTTPException(status_code=404, detail="Case not found")

    # TODO: persistir decisión, re-enqueue si APPROVE, etc.
    _CASES[case_id]["status"] = decision.action
    _CASES[case_id]["corrected_payload"] = decision.corrected_payload
    return {"ok": True, "case_id": case_id}
