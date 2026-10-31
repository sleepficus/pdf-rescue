#!/usr/bin/env python3
"""Mechanical Gate-A checks. No network, installs, PDF mutation, or candidate build."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "GATE-A-MECHANICAL-CHECKS.json"


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


checks = []


def check(check_id: str, passed: bool, detail: str) -> None:
    checks.append({"check_id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail})


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


manifest = load("lanes/03-fixtures-oracles/FIXTURE-MANIFEST.json")["fixtures"]
expected = load("lanes/03-fixtures-oracles/EXPECTED-DISPOSITIONS.json")
prebuild = load("outputs/PREBUILD-GATE.json")
budgets = load("lanes/05-safety-budgets/BUDGETS.json")
trips = load("lanes/05-safety-budgets/TRIP-CASES.json")
receipt_schema = load("lanes/02-cdrr-receipts/RECEIPT-SCHEMA.json")
disposition = load("lanes/01-protocol-disposition/DISPOSITION-SPEC.json")
c3 = load("lanes/04-dependencies-independence/C3-VALIDATION.json")

fixture_dir = ROOT / "lanes/03-fixtures-oracles/fixtures"
hash_ok = True
for entry in manifest:
    path = fixture_dir / entry["filename"]
    hash_ok &= path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
check("GA-01-FIXTURE-HASHES", hash_ok and len(manifest) == 14, "14 fixture files equal authoritative manifest hashes")

sealed = (ROOT / "lanes/03-fixtures-oracles/SEALED.md").read_text(encoding="utf-8")
sealed_pairs = dict(re.findall(r"(?m)^([0-9a-f]{64})\s+fixtures/(\S+\.pdf)$", sealed))
sealed_by_file = {filename: digest for digest, filename in sealed_pairs.items()}
manifest_by_file = {entry["filename"]: entry["sha256"] for entry in manifest}
check("GA-02-SEALED-TABLE", sealed_by_file == manifest_by_file, f"sealed_rows={len(sealed_by_file)} manifest_rows={len(manifest_by_file)}")

expected_records = expected.get("documents", expected.get("fixtures", expected.get("expected_dispositions", expected)))
if isinstance(expected_records, dict):
    expected_ids = set(expected_records)
else:
    expected_ids = {entry.get("id", entry.get("fixture_id")) for entry in expected_records}
manifest_ids = {entry["id"] for entry in manifest}
check("GA-03-EXPECTED-ID-COVERAGE", expected_ids == manifest_ids, f"missing={sorted(manifest_ids-expected_ids)} extra={sorted(expected_ids-manifest_ids)}")

required_maps = ["gate_id_map", "class_map", "refusal_family_map", "operation_name_map", "delta_type_map"]
check("GA-04-MAPS", all(isinstance(prebuild.get(key), dict) and prebuild[key] for key in required_maps), f"required={required_maps}")
disambiguations = prebuild.get("disambiguations", {})
check("GA-05-DISAMBIGUATIONS", all(key in disambiguations for key in ("G6_REQUIRED", "G5_STRUCTURE_TREE", "BENIGN_ZERO_OPERATIONS")), "G6/G5/B01-B02 rules present")
check("GA-06-C3", c3.get("status") == "PASS", f"C3 status={c3.get('status')}")

budget_ids = {"PAGE_COUNT", "OBJECT_COUNT", "FILE_BYTES", "PIXELS", "CPU_SECONDS", "WALL_SECONDS", "TEMP_STORAGE_BYTES", "OUTPUT_BYTES"}
observed_budget_ids = {item["budget_id"] for item in budgets["budgets"]}
check("GA-07-BUDGET-ID-SET", observed_budget_ids == budget_ids, f"ids={sorted(observed_budget_ids)}")
shape_ok = all(item.get("comparison") == "<=" and item.get("limit") is not None and item.get("unit") and item.get("measured_on") for item in budgets["budgets"])
check("GA-08-BUDGET-SHAPE", shape_ok, "all budgets carry limit/unit/<=/measurement points")
headroom_ok = True
for item in budgets["budgets"]:
    baseline = item.get("baseline", {})
    observed = baseline.get("observed_max_in_packet")
    status = baseline.get("status")
    if status in {"MEASURED", "DERIVED", "DERIVED_FROM_COMPONENTS"}:
        headroom_ok &= observed is not None and item["limit"] > observed
    if status == "MEASURED":
        headroom_ok &= item["limit"] >= 2 * observed
check("GA-09-BUDGET-HEADROOM", headroom_ok, "all measured/derived limits exceed baselines; measured limits >=2x")
constants = budgets["frozen_constants"]
constants_ok = constants["render_pixel_size"][0] * constants["render_pixel_size"][1] == constants["pixels_per_page_at_render_dpi"] == 2103750 and constants["render_dpi"] == 150 and constants["page_box_pt"] == [612.0, 792.0]
check("GA-10-FROZEN-CONSTANTS", constants_ok, "1275x1650=2103750, 150 DPI, US Letter points")

candidate_states = {"NO_CANDIDATE_EVER_CREATED", "DISCARDED_AT_TEMP_NEVER_PUBLISHED"}
trip_shape_ok = all(
    case["expected"]["original_state"] == "UNCHANGED_HASH_REVERIFIED"
    and case["expected"]["receipt"]["present"] is True
    and case["expected"]["candidate_state"] in candidate_states
    for case in trips["trip_cases"]
)
check("GA-11-TRIP-SHAPE", trip_shape_ok, f"trip_cases={len(trips['trip_cases'])}")
allowed_e = {"E06", "E07", "E12", "E15"}
target_ok = all(
    case.get("target_budget_id") in budget_ids
    or (case.get("kind") in {"HST", "INVARIANT_AUDIT"} and bool(set(case.get("e_conditions", [])) & allowed_e))
    for case in trips["trip_cases"]
)
check("GA-12-TRIP-TARGETS", target_ok, "each trip targets a budget or allowed audit E-condition")

rule_ids = {item["id"] for item in disposition["precedence_rules"]}
receipt_strings = set(strings(receipt_schema))
mapping_text = json.dumps(trips["disposition_mapping"], sort_keys=True)
mapping_ok = all(rule in rule_ids and rule in mapping_text for rule in ("PR-08", "PR-14")) and "RESOURCE_BUDGET_EXCEEDED" in receipt_strings and "BUDGET_TRIP_BEFORE_GATE" in receipt_strings
check("GA-13-DISPOSITION-CITATIONS", mapping_ok, "PR-08/PR-14 and receipt enums resolve")

json_text = json.dumps([budgets, trips], sort_keys=True)
unsafe_tokens = [token for token in ("http://", "https://", "pip install", "brew install", "npm install") if token in json_text]
absolute_paths = re.findall(r'(?<![A-Za-z0-9_.-])/(?:Users|home|tmp|var|etc)/[^\"\s]*', json_text)
check("GA-14-NO-EXTERNAL-ACTION", not unsafe_tokens and not absolute_paths, f"unsafe_tokens={unsafe_tokens} absolute_paths={absolute_paths}")

check("GA-15-TC09-FAMILY", trips["trip_cases"][8]["case_id"] == "TC-09" and trips["trip_cases"][8]["expected"]["receipt"]["refusal_family"] == "OTHER_RECORDED", "network E06 is not mislabeled as a resource budget trip")

status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
result = {
    "artifact": "GATE-A-MECHANICAL-CHECKS.json",
    "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "status": status,
    "scope": "Mechanical correction-batch checks only; lane 06 remains the independent readiness authority.",
    "checks": checks,
}
OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
for item in checks:
    print(f"{item['status']}: {item['check_id']} — {item['detail']}")
print(f"GATE_A_MECHANICAL={status}")
raise SystemExit(0 if status == "PASS" else 1)
