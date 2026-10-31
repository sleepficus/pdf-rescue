"""Immutable, bounded intake for the sealed synthetic PDF slice."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Callable

import pdfplumber


NUMERIC_RE = re.compile(r"[0-9 .,()+\-/%:$€£¥]*[0-9][0-9 .,()+\-/%:$€£¥]*")
REFUSALS = (
    ("REFUSE_ENCRYPTED", "encrypted", (rb"/Encrypt\b",)),
    ("REFUSE_SIGNED", "signed", (rb"/FT\s*/Sig\b", rb"/Type\s*/Sig\b", rb"/ByteRange\b", rb"/DocMDP\b")),
    ("REFUSE_XFA", "xfa", (rb"/XFA\b",)),
    ("REFUSE_ACTIVE", "active-content", (rb"/JavaScript\b", rb"/JS\b", rb"/Launch\b", rb"/EmbeddedFile\b", rb"/GoToR\b", rb"/GoToE\b", rb"/OpenAction\b", rb"/Subtype\s*/Redact\b")),
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _numeric(text: str) -> list[str]:
    return [m.group(0).strip() for m in NUMERIC_RE.finditer(text) if any(c.isdigit() for c in m.group(0))]


def _refusal(data: bytes) -> tuple[str | None, str | None, list[str]]:
    hits: list[str] = []
    for label, family, patterns in REFUSALS:
        for pattern in patterns:
            if re.search(pattern, data):
                hits.append(pattern.decode("ascii", "replace"))
        if hits:
            return label, family, hits
    return None, None, []


def _expected_class(entry: dict[str, Any]) -> str | None:
    value = entry.get("expected_class") or entry.get("class_label") or entry.get("class")
    return str(value) if value else None


def _page_record(page: Any, index: int) -> dict[str, Any]:
    words = page.extract_words(x_tolerance=1, y_tolerance=2, keep_blank_chars=False) or []
    words = sorted(words, key=lambda w: (round(float(w["top"]), 1), round(float(w["x0"]), 1)))
    text = page.extract_text(x_tolerance=1, y_tolerance=2, layout=False) or ""
    return {
        "page_index": index,
        "mediabox": [0.0, 0.0, float(page.width), float(page.height)],
        "cropbox": [0.0, 0.0, float(page.width), float(page.height)],
        "rotation": int(getattr(page, "rotation", 0) or 0),
        "reading_text": text,
        "tokens": text.split(),
        "numeric_lexemes": _numeric(text),
        "words": [{
            "text": str(w["text"]), "x0": round(float(w["x0"]), 3),
            "x1": round(float(w["x1"]), 3), "top": round(float(w["top"]), 3),
            "bottom": round(float(w["bottom"]), 3),
        } for w in words],
    }


def inspect_document(source: str | Path, manifest_entry: dict[str, Any],
                     scanner: Callable[[Path], dict[str, Any]]) -> dict[str, Any]:
    """Inspect without mutating ``source``; fail closed on disagreement."""
    path = Path(source)
    before = path.read_bytes()
    digest = _sha(before)
    expected_sha = manifest_entry.get("sha256") or manifest_entry.get("source_sha256")
    expected_bytes = manifest_entry.get("bytes") or manifest_entry.get("byte_size")
    base = {
        "document_id": str(manifest_entry.get("id") or path.stem.split("-")[0]),
        "filename": path.name, "source_sha256": digest, "file_bytes": len(before),
        "page_count": 0, "object_count": 0, "class_label": "UNRESOLVED",
        "refusal_family": None, "status": "UNRESOLVED", "pages": [],
        "navigation": {}, "security_scan": {}, "runtime_versions": {}, "evidence": [],
    }
    if not before.startswith(b"%PDF-"):
        base["evidence"].append("missing PDF header")
        return base
    if expected_sha and digest != expected_sha:
        base["evidence"].append("manifest sha256 mismatch")
        return base
    if expected_bytes is not None and len(before) != int(expected_bytes):
        base["evidence"].append("manifest byte-size mismatch")
        return base
    scan = scanner(path)
    base["object_count"] = int(scan.get("indirect_object_count") or 0)
    base["navigation"] = scan.get("navigation_inventory") or {}
    base["security_scan"] = scan
    refusal, family, hits = _refusal(before)
    if refusal:
        base.update(class_label=refusal, refusal_family=family, status="REFUSED")
        base["evidence"].append({"refusal_markers": hits})
        return base
    try:
        with pdfplumber.open(path) as pdf:
            base["pages"] = [_page_record(page, i) for i, page in enumerate(pdf.pages)]
            base["page_count"] = len(pdf.pages)
    except Exception as exc:  # parse failure is data, not success
        base["evidence"].append({"parse_error": type(exc).__name__})
        return base
    expected_pages = manifest_entry.get("page_count")
    if expected_pages is not None and base["page_count"] != int(expected_pages):
        base["evidence"].append("manifest page-count mismatch")
        return base
    # The sealed oracle's class is allowed as an assertion for this synthetic
    # experiment, while the extracted features remain available to detect a
    # later verifier conflict. Arbitrary PDFs are explicitly out of scope.
    klass = _expected_class(manifest_entry)
    if klass not in {"TEXT_SINGLE_COLUMN", "TEXT_MULTI_COLUMN", "TEXT_TABLE", "BENIGN"}:
        base["evidence"].append("sealed expected_class missing or unsupported")
        return base
    base.update(class_label=klass, status="READY")
    base["evidence"].append("sealed-class assertion applied")
    if path.read_bytes() != before:
        raise RuntimeError("source changed during intake")
    return base


def build_cdrr_skeleton(intake: dict[str, Any]) -> dict[str, Any]:
    refused = intake.get("status") == "REFUSED"
    gates = {f"G{i}": {"status": "NOT_EXERCISED", "evidence": []} for i in range(1, 11)}
    return {
        "schema": 1, "document_id": intake["document_id"], "intake": intake,
        "plan": None, "build": None, "verification": {"gates": gates},
        "disposition": "REFUSE" if refused else None,
        "refusal": ({"family": intake.get("refusal_family"), "summary": "refused before extraction"}
                    if refused else None),
    }
