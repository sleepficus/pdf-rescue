"""Mechanical PR-00..PR-14 disposition precedence."""
from __future__ import annotations
from typing import Any

REQUIRED = {
    "TEXT_SINGLE_COLUMN": {"G1","G2","G3","G4","G5","G6","G8","G9","G10"},
    "TEXT_MULTI_COLUMN": {"G1","G2","G3","G4","G5","G6","G8","G9","G10"},
    "TEXT_TABLE": {"G1","G2","G3","G4","G5","G6","G7","G8","G9","G10"},
    "BENIGN": {"G1","G2","G3","G4","G5","G6","G8","G9","G10"},
}

def derive_disposition(class_label: str, gates: dict[str, Any], reconciliation: dict[str, Any], disposition_spec: dict[str, Any] | None = None) -> dict[str, str]:
    status = lambda g: (gates.get(g) or {}).get("status")
    outcome = reconciliation.get("outcome")
    anomaly = reconciliation.get("anomaly_kind")
    forced = bool(reconciliation.get("plan_forced_review")) and not bool(reconciliation.get("forced_review_confirmed"))
    if class_label == "UNRESOLVED": return {"disposition":"NOT_VERIFIABLE","rule":"PR-00"}
    if class_label.startswith("REFUSE_"): return {"disposition":"REFUSE","rule":"PR-01"}
    if status("G1") in {"FAIL","ERROR"}: return {"disposition":"NOT_VERIFIABLE","rule":"PR-02"}
    if outcome == "CLASSIFIER_CONFLICT": return {"disposition":"NOT_VERIFIABLE","rule":"PR-03"}
    if status("G8") == "FAIL": return {"disposition":"REFUSE","rule":"PR-04"}
    if status("G2") == "FAIL": return {"disposition":"REFUSE","rule":"PR-05"}
    if status("G4") == "FAIL" and anomaly == "DIVERGENT": return {"disposition":"REFUSE","rule":"PR-06"}
    if outcome in {"UNDECLARED_MATERIAL_DELTA","OUT_OF_BOUNDS","PLAN_ILLEGAL"}: return {"disposition":"REFUSE","rule":"PR-07"}
    req = REQUIRED.get(class_label, set())
    if any(status(g) in {"NOT_EXERCISED","ERROR"} for g in req): return {"disposition":"NOT_VERIFIABLE","rule":"PR-08"}
    if status("G5") == "FAIL": return {"disposition":"REVIEW","rule":"PR-09"}
    if status("G4") == "FAIL": return {"disposition":"REVIEW","rule":"PR-10"}
    if any(status(g) == "FAIL" for g in ("G3","G6","G7","G10")): return {"disposition":"REFUSE","rule":"PR-11"}
    if forced: return {"disposition":"REVIEW","rule":"PR-12"}
    if all(status(g) == "PASS" for g in req) and outcome == "RECONCILED": return {"disposition":"ACCEPT","rule":"PR-13"}
    return {"disposition":"NOT_VERIFIABLE","rule":"PR-14"}

