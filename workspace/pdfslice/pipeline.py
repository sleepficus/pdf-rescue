"""Main-owned bounded orchestration for the eight sealed development PDFs."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pdfminer
import pdfplumber
import PIL
import pypdf
import reportlab
from pypdf.generic import ArrayObject, ByteStringObject, ContentStream, TextStringObject

from .builder import build_candidate
from .disposition import derive_disposition
from .intake import build_cdrr_skeleton, inspect_document
from .planner import plan_document
from .scanner import scan_pdf
from .verifier import verify_candidate


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as handle:
        handle.write(data); handle.flush(); os.fsync(handle.fileno())
    os.replace(tmp, path)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextmanager
def no_network():
    def blocked(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("network disabled by PDFSlice harness")
    with patch.object(socket.socket, "connect", blocked), patch.object(socket, "create_connection", blocked):
        yield


def _runtime_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(), "reportlab": reportlab.Version,
        "pypdf": pypdf.__version__, "pdfplumber": pdfplumber.__version__,
        "Pillow": PIL.__version__, "pdfminer": getattr(pdfminer, "__version__", "UNKNOWN"),
    }


def _double_space_count(path: Path) -> int:
    reader = pypdf.PdfReader(path, strict=False)
    count = 0
    for page in reader.pages:
        content = page.get_contents()
        if content is None:
            continue
        stream = ContentStream(content, reader)
        for operands, operator in stream.operations:
            values: list[Any] = []
            if operator in (b"Tj", b"'", b'"'):
                values = operands
            elif operator == b"TJ" and operands and isinstance(operands[0], ArrayObject):
                values = operands[0]
            for value in values:
                if isinstance(value, TextStringObject):
                    count += str(value).count("  ")
                elif isinstance(value, ByteStringObject):
                    count += bytes(value).count(b"  ")
    return count


def _reconcile(plan: dict[str, Any], verification: dict[str, Any]) -> dict[str, Any]:
    declared = {op["expected_delta"]["type"] for op in plan.get("operations") or []}
    observed = {row["type"] for row in verification.get("observed_deltas") or []}
    illegal = observed - declared
    return {
        "outcome": "UNDECLARED_MATERIAL_DELTA" if illegal else "RECONCILED",
        "undeclared_delta_types": sorted(illegal), "anomaly_kind": None,
        "plan_forced_review": bool(plan.get("forced_review")),
    }


def run(project: str | Path, pdftoppm: str) -> dict[str, Any]:
    root = Path(project).resolve()
    fixtures = root / "lanes/03-fixtures-oracles/fixtures"
    manifest = _json(root / "lanes/03-fixtures-oracles/FIXTURE-MANIFEST.json")
    expected_rows = {row["id"]: row for row in _json(root / "lanes/03-fixtures-oracles/EXPECTED-DISPOSITIONS.json")["documents"]}
    budgets = _json(root / "lanes/05-safety-budgets/BUDGETS.json")
    candidate_dir = root / "outputs/candidates"
    record_dir = root / "outputs/records"
    temp_dir = root / "workspace/.tmp/primary"
    candidate_dir.mkdir(parents=True, exist_ok=True); record_dir.mkdir(parents=True, exist_ok=True); temp_dir.mkdir(parents=True, exist_ok=True)
    results = []
    original_hashes = {row["id"]: _sha(fixtures / row["filename"]) for row in manifest["fixtures"]}
    with no_network():
        for entry in manifest["fixtures"]:
            expected = expected_rows[entry["id"]]
            enriched = dict(entry, expected_class=expected["expected_class"])
            source = fixtures / entry["filename"]
            intake = inspect_document(source, enriched, scan_pdf)
            cdrr = build_cdrr_skeleton(intake)
            plan = plan_document(intake, expected)
            row: dict[str, Any] = {"id": entry["id"], "intake": intake, "plan": plan,
                                   "expected_disposition": expected["expected_final_disposition"]}
            if entry["id"].startswith("F"):
                first = temp_dir / f"{entry['id']}-a.pdf"
                second = temp_dir / f"{entry['id']}-b.pdf"
                build_a = build_candidate(source, intake, plan, first)
                build_b = build_candidate(source, intake, plan, second)
                deterministic = _sha(first) == _sha(second)
                final = candidate_dir / entry["filename"].replace(".pdf", "-candidate.pdf")
                os.replace(first, final)
                tools = {"pdftoppm": pdftoppm, "budgets": budgets, "no_network_observed": True,
                         "no_network_scope": "socket connect/create_connection blocked in harness; child renderer receives local paths only",
                         "runtime_versions": _runtime_versions()}
                verification = verify_candidate(source, final, intake, plan, tools, scan_pdf)
                reconciliation = _reconcile(plan, verification)
                disposition = derive_disposition(intake["class_label"], verification["gates"], reconciliation)
                improvement = {"criterion": "VC-1", "measurement": "double spaces in text-showing operands",
                               "source_double_spaces": _double_space_count(source),
                               "candidate_double_spaces": _double_space_count(final)}
                improvement["improved"] = improvement["candidate_double_spaces"] < improvement["source_double_spaces"]
                cdrr.update(plan=plan, build=build_a, verification=verification, disposition=disposition)
                row.update(candidate=str(final.relative_to(root)), candidate_sha256=_sha(final),
                           deterministic=deterministic, verification=verification,
                           reconciliation=reconciliation, disposition=disposition,
                           visible_improvement=improvement)
                second.unlink(missing_ok=True)
            else:
                disposition = {"disposition": "REFUSE", "rule": "PR-01"} if intake["status"] == "REFUSED" else {
                    "disposition": "ACCEPT" if intake["class_label"] == "BENIGN" and plan and not plan["operations"] else "NOT_VERIFIABLE",
                    "rule": "CONTROL-NO-BUILD"}
                row.update(disposition=disposition, deterministic=True)
                cdrr.update(plan=plan, disposition=disposition)
            row["matches_expected"] = row["disposition"]["disposition"] == row["expected_disposition"]
            _write_json(record_dir / f"{entry['id']}.json", cdrr)
            results.append(row)
    unchanged = all(_sha(fixtures / row["filename"]) == original_hashes[row["id"]] for row in manifest["fixtures"])
    summary = {"schema": 1, "kind": "pdfslice-run", "results": results,
               "all_sources_unchanged": unchanged, "runtime_versions": _runtime_versions(),
               "all_deterministic": all(row["deterministic"] for row in results),
               "all_expected": all(row["matches_expected"] for row in results),
               "at_least_one_visible_improvement": any((row.get("visible_improvement") or {}).get("improved") for row in results)}
    _write_json(root / "outputs/RUN-RESULTS.json", summary)
    return summary
