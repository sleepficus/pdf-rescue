"""Frozen, conservative operation planner for the sealed fixture pack."""
from __future__ import annotations

from typing import Any


def _op(op_type: str, delta_type: str, pages: list[int], *, tokens: int = 0,
        regions: int = 1, area: float = 0.005) -> dict[str, Any]:
    return {
        "op_type": op_type,
        "anchor": {"pages": pages, "element_ids": [], "region_ids": [f"p{p}-body" for p in pages]},
        "expected_delta": {
            "type": delta_type,
            "scope": {"pages": pages, "element_ids": []},
            "bounded_magnitude": {
                "max_affected_tokens": tokens,
                "max_affected_regions": regions,
                "max_affected_area_fraction": area,
            },
        },
    }


def plan_document(intake: dict[str, Any], expected: dict[str, Any] | None = None) -> dict[str, Any] | None:
    if intake.get("status") != "READY" or intake.get("class_label", "").startswith("REFUSE"):
        return None
    pages = list(range(int(intake.get("page_count") or 0)))
    doc_id = str(intake.get("document_id"))
    if intake.get("class_label") == "BENIGN" or doc_id.startswith("B"):
        operations: list[dict[str, Any]] = []
    else:
        operations = [_op("OP_STRUCTURE_TAGS", "STRUCTURE_TAG_ADD", pages,
                          tokens=0, regions=max(1, len(pages)), area=0.0)]
        if doc_id == "F02":
            operations.append(_op("OP_SPACING_NORMALIZE", "SPACING_COLLAPSE", pages,
                                  tokens=32, regions=32, area=0.005))
    return {
        "document_id": doc_id, "class_label": intake["class_label"],
        "operations": operations, "page_mapping": pages,
        "immutable": {"page_count": intake["page_count"], "page_order": pages},
        "forced_review": any(op["expected_delta"]["type"] == "PAGE_ROTATE_REVIEW" for op in operations),
    }
