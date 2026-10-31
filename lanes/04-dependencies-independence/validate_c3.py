#!/usr/bin/env python3
"""Acceptance checks for the C3 independent stdlib scanner."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

from c3_stdlib_scanner import scan_pdf


HERE = Path(__file__).resolve().parent
FIXTURE_DIR = HERE.parent / "03-fixtures-oracles" / "fixtures"
MANIFEST_PATH = HERE.parent / "03-fixtures-oracles" / "FIXTURE-MANIFEST.json"
SCANNER_PATH = HERE / "c3_stdlib_scanner.py"
OUTPUT_PATH = HERE / "C3-VALIDATION.json"


def main() -> int:
    source = SCANNER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    nonstdlib = sorted(name for name in imported if name not in sys.stdlib_module_names and name != "__future__")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["fixtures"]
    scans = {entry["id"]: scan_pdf(FIXTURE_DIR / entry["filename"]) for entry in manifest}
    checks = []

    def check(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail})

    check("C3-IMPORT-AUDIT", not nonstdlib, f"imports={sorted(imported)}; nonstdlib={nonstdlib}")
    check("C3-ALL-FILES", len(scans) == 14, f"scanned={len(scans)}")
    check("C3-PDF-SHAPE", all(s["header_is_pdf"] and s["eof_marker_present"] and s["indirect_object_count"] > 0 for s in scans.values()), "all fixtures have header, EOF marker, and indirect objects")
    check("C3-R01-ENCRYPT", scans["R01"]["refusal_detection"]["encrypted"], "R01 raw /Encrypt marker")
    check("C3-R02-SIGNATURE", scans["R02"]["refusal_detection"]["signed_or_certified"], "R02 raw signature/ByteRange marker")
    check("C3-R03-XFA", scans["R03"]["refusal_detection"]["xfa_or_hybrid_xfa"], "R03 raw /XFA marker")
    check("C3-R04-ACTIVE", scans["R04"]["refusal_detection"]["active_content"], "R04 raw JavaScript/active marker")
    clean_ids = [f"F{i:02d}" for i in range(1, 9)] + ["B01", "B02"]
    check(
        "C3-CLEAN-NO-REFUSAL-MARKERS",
        all(not any(scans[fixture_id]["refusal_detection"].values()) for fixture_id in clean_ids),
        f"clean_ids={clean_ids}",
    )
    check(
        "C3-MANIFEST-HASH-DIFF",
        all(scans[e["id"]]["sha256"] == e["sha256"] for e in manifest),
        "scanner hashes match all authoritative manifest hashes",
    )
    check(
        "C3-NAVIGATION-INVENTORY",
        scans["B02"]["navigation_inventory"]["link_annotation_count"] > 0,
        f"B02 navigation={scans['B02']['navigation_inventory']}",
    )

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    output = {
        "artifact": "C3-VALIDATION.json",
        "check": "C3 verifier-owned stdlib scanner acceptance",
        "status": status,
        "scope": "read-only raw-byte inventory and marker cross-check; never a sole semantic proof",
        "independence": {
            "builder_lineages": ["REPORTLAB", "PYPDF"],
            "scanner_lineage": "CPYTHON_STDLIB_RAW_BYTES",
            "nonstdlib_imports": nonstdlib,
            "decisive_use_limit": "May independently corroborate G1/G6/G8 observations; cannot render, decrypt, execute, or repair.",
        },
        "checks": checks,
        "scans": scans,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"C3 {status}; wrote {OUTPUT_PATH}")
    for item in checks:
        print(f"{item['status']}: {item['check_id']} — {item['detail']}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
