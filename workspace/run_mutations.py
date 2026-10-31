#!/usr/bin/env python3
"""Run the six sealed hostile mutations against the integrated verifier."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from pdfslice.disposition import derive_disposition
from pdfslice.intake import inspect_document
from pdfslice.pipeline import (_reconcile, _runtime_versions, _write_json,
                               no_network)
from pdfslice.planner import plan_document
from pdfslice.scanner import scan_pdf
from pdfslice.verifier import verify_candidate


PDFTOPPM = "/Users/carrie/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm"
TARGETS = {"M01": "F01", "M02": "F02", "M03": "F05",
           "M04": "F08", "M05": "F07", "M06": "F04"}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_generator(path: Path):
    spec = importlib.util.spec_from_file_location("sealed_fixture_generator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load sealed fixture generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(root: Path) -> dict:
    fixture_root = root / "lanes/03-fixtures-oracles/fixtures"
    mutation_root = root / "workspace/.tmp/mutations"
    mutation_root.mkdir(parents=True, exist_ok=True)
    generator = _load_generator(root / "lanes/03-fixtures-oracles/generator/generate_all.py")
    manifest = {row["id"]: row for row in _json(root / "lanes/03-fixtures-oracles/FIXTURE-MANIFEST.json")["fixtures"]}
    expected = {row["id"]: row for row in _json(root / "lanes/03-fixtures-oracles/EXPECTED-DISPOSITIONS.json")["documents"]}
    specs = _json(root / "lanes/03-fixtures-oracles/MUTATION-SPECS.json")["mutations"]
    budgets = _json(root / "lanes/05-safety-budgets/BUDGETS.json")
    rows = []
    with no_network():
        generator.emit(str(mutation_root), list(TARGETS.values()),
                       mutated={doc: mid for mid, doc in TARGETS.items()},
                       report_name="build-report.json")
        for spec_row in specs:
            mutation_id = spec_row["id"]
            doc_id = TARGETS[mutation_id]
            entry = dict(manifest[doc_id], expected_class=expected[doc_id]["expected_class"])
            source = fixture_root / entry["filename"]
            mutant = mutation_root / f"{doc_id}-{mutation_id}-mutant.pdf"
            intake = inspect_document(source, entry, scan_pdf)
            plan = plan_document(intake, expected[doc_id])
            tools = {
                "pdftoppm": PDFTOPPM,
                "budgets": budgets,
                "no_network_observed": True,
                "no_network_scope": "socket connect/create_connection blocked in mutation harness",
                "runtime_versions": _runtime_versions(),
            }
            verification = verify_candidate(source, mutant, intake, plan, tools, scan_pdf)
            reconciliation = _reconcile(plan, verification)
            disposition = derive_disposition(intake["class_label"], verification["gates"], reconciliation)
            expected_gate = spec_row["expected_failing_gate"]
            target_status = verification["gates"][expected_gate]["status"]
            passed = target_status == "FAIL" and disposition["disposition"] != "ACCEPT"
            rows.append({
                "mutation_id": mutation_id,
                "document_id": doc_id,
                "expected_failing_gate": expected_gate,
                "target_gate_status": target_status,
                "disposition": disposition,
                "passed": passed,
                "gate_statuses": {key: value["status"] for key, value in verification["gates"].items()},
                "mutant": str(mutant.relative_to(root)),
            })
    result = {"schema": 1, "kind": "pdfslice-hostile-mutation-run",
              "all_detected": all(row["passed"] for row in rows), "mutations": rows}
    _write_json(root / "outputs/MUTATION-RESULTS.json", result)
    return result


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[1]
    print(json.dumps(run(project), indent=2, sort_keys=True))
