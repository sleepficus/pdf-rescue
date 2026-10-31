#!/usr/bin/env python3
"""Offline self-validation for lane 02-cdrr-receipts (guarded, no network).

Checks:
  (a) CDRR-SCHEMA.json, RECEIPT-SCHEMA.json and every fixture JSON load as valid JSON;
  (b) if the jsonschema package is importable, the sample CDRR + receipt fixtures
      validate as positive examples and the deliberately broken fixtures fail
      (draft 2020-12 meta-schema is checked first);
  (c) if jsonschema is NOT importable, a minimal recursive structural validator
      (pure stdlib) implements exactly the JSON-Schema subset these schemas use -
      type, const, enum, required, properties, additionalProperties, items,
      minimum, maximum, exclusiveMinimum, minLength, pattern, minItems, maxItems,
      allOf, oneOf, if/then/else, $defs, local $ref - and runs the same
      positive/negative checks;
  (d) every invariant id frozen in INVARIANTS.md appears inside each schema
      (in field descriptions / the embedded x-invariants-registry table).

When jsonschema IS importable, the fallback validator additionally runs as a
cross-check and the two verdicts must agree.

Writes VALIDATION-OUTPUT.txt in this lane. Writes nowhere else. Exit code 0 on
success, 1 on any failure.
"""

from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

LANE = Path(__file__).resolve().parent
CDRR_SCHEMA_PATH = LANE / "CDRR-SCHEMA.json"
RECEIPT_SCHEMA_PATH = LANE / "RECEIPT-SCHEMA.json"
INVARIANTS_PATH = LANE / "INVARIANTS.md"
FIXTURES_DIR = LANE / "fixtures"
OUTPUT_PATH = LANE / "VALIDATION-OUTPUT.txt"

POSITIVE_FIXTURES = [
    "sample-cdrr-accept.json",
    "sample-cdrr-refused.json",
    "sample-operation-record.json",
    "sample-verifier-record-not-exercised.json",
    "sample-run-receipt.json",
    "sample-experiment-receipt.json",
]
NEGATIVE_FIXTURES = [
    "broken-cdrr-bad-gate-enum.json",
    "broken-cdrr-refuse-shape.json",
    "broken-run-receipt-temp-reuse.json",
    "broken-experiment-receipt-empty-conditions.json",
]

EXPECTED_INVARIANT_IDS = {f"INV-{i:02d}" for i in range(1, 25)}

REFUSED_EXTRACTION_SECTIONS = [
    "source_inventory",
    "pages",
    "text_spans",
    "structure",
    "tables",
    "visible_ink",
    "operation_plan",
    "applied_operations",
    "delta_reconciliation",
]


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failures = 0
        self.checks = 0

    def ok(self, msg: str) -> None:
        self.checks += 1
        self.lines.append(f"PASS: {msg}")

    def fail(self, msg: str) -> None:
        self.checks += 1
        self.failures += 1
        self.lines.append(f"FAIL: {msg}")

    def info(self, msg: str) -> None:
        self.lines.append(f"INFO: {msg}")


def deep_strings(obj):
    """Yield every string value found anywhere in a JSON-like structure."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from deep_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from deep_strings(v)


# --------------------------------------------------------------------------
# Minimal recursive structural validator (pure stdlib fallback).
# Implements exactly the keyword subset used by the two frozen schemas.
# --------------------------------------------------------------------------

_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _const_equal(a, b) -> bool:
    # JSON-Schema const equality distinguishes booleans from numbers.
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    return a == b


def fallback_validate(instance, schema, root, path="$"):
    """Return a list of error strings; empty list means valid."""
    errors: list[str] = []

    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            return [f"{path}: unsupported non-local $ref {ref!r}"]
        target = root["$defs"].get(ref[len("#/$defs/"):])
        if target is None:
            return [f"{path}: unresolved $ref {ref!r}"]
        return fallback_validate(instance, target, root, path)

    declared = schema.get("type")
    if declared is not None:
        types = declared if isinstance(declared, list) else [declared]
        if not any(_TYPE_CHECKS[t](instance) for t in types):
            errors.append(f"{path}: expected type {declared!r}, got {type(instance).__name__}")
            return errors  # further keyword checks are meaningless on a type mismatch

    if "const" in schema and not _const_equal(instance, schema["const"]):
        errors.append(f"{path}: const mismatch (expected {schema['const']!r})")

    if "enum" in schema and not any(_const_equal(instance, e) for e in schema["enum"]):
        errors.append(f"{path}: value {instance!r} not in enum")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            errors.append(f"{path}: {instance} <= exclusiveMinimum {schema['exclusiveMinimum']}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength {schema['minLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: {instance!r} does not match pattern {schema['pattern']!r}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: array has {len(instance)} items < minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: array has {len(instance)} items > maxItems {schema['maxItems']}")
        items = schema.get("items")
        if isinstance(items, dict):
            for i, value in enumerate(instance):
                errors.extend(fallback_validate(value, items, root, f"{path}[{i}]"))

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in properties:
                errors.extend(fallback_validate(value, properties[key], root, f"{path}.{key}"))
            elif additional is False:
                errors.append(f"{path}: unexpected additional property {key!r}")
            elif isinstance(additional, dict):
                errors.extend(fallback_validate(value, additional, root, f"{path}.{key}"))

    for sub in schema.get("allOf", []):
        errors.extend(fallback_validate(instance, sub, root, path))

    if "oneOf" in schema:
        matches = sum(1 for sub in schema["oneOf"] if not fallback_validate(instance, sub, root, path))
        if matches != 1:
            errors.append(f"{path}: oneOf matched {matches} branches, expected exactly 1")

    if "if" in schema:
        if not fallback_validate(instance, schema["if"], root, path):
            if "then" in schema:
                errors.extend(fallback_validate(instance, schema["then"], root, path))
        elif "else" in schema:
            errors.extend(fallback_validate(instance, schema["else"], root, path))

    return errors


def verdict(errors: list[str]) -> bool:
    return not errors


def main() -> int:
    report = Report()
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    report.info(f"lane: 02-cdrr-receipts")
    report.info(f"validation run (UTC): {utc_now}")
    report.info(f"python: {sys.version.split()[0]}")

    # ---------------------------------------------------------------- (a)
    schemas: dict[str, dict] = {}
    for path in (CDRR_SCHEMA_PATH, RECEIPT_SCHEMA_PATH):
        try:
            schemas[path.name] = json.loads(path.read_text(encoding="utf-8"))
            report.ok(f"{path.name} loads as valid JSON")
        except Exception as exc:  # noqa: BLE001
            report.fail(f"{path.name} does not load as JSON: {exc}")

    fixtures: dict[str, dict] = {}
    fixture_paths = sorted(FIXTURES_DIR.glob("*.json"))
    expected_fixture_names = set(POSITIVE_FIXTURES + NEGATIVE_FIXTURES)
    present_names = {p.name for p in fixture_paths}
    for name in sorted(expected_fixture_names):
        if name not in present_names:
            report.fail(f"missing fixture: fixtures/{name}")
    for path in fixture_paths:
        try:
            fixtures[path.name] = json.loads(path.read_text(encoding="utf-8"))
            report.ok(f"fixtures/{path.name} loads as valid JSON")
        except Exception as exc:  # noqa: BLE001
            report.fail(f"fixtures/{path.name} does not load as JSON: {exc}")

    # ------------------------------------------------- jsonschema availability
    have_jsonschema = False
    jsonschema_version = None
    try:  # guarded import: the brief forbids installing anything
        import jsonschema  # type: ignore
        from importlib.metadata import version as _pkg_version

        have_jsonschema = True
        try:
            jsonschema_version = _pkg_version("jsonschema")
        except Exception:  # noqa: BLE001
            jsonschema_version = "unknown"
        report.info(f"jsonschema importable: YES (version {jsonschema_version})")
    except ImportError:
        report.info("jsonschema importable: NO (falling back to the stdlib structural validator)")

    jsonschema_validators = {}
    if have_jsonschema:
        for name, schema in schemas.items():
            try:
                jsonschema.Draft202012Validator.check_schema(schema)
                jsonschema_validators[name] = jsonschema.Draft202012Validator(schema)
                report.ok(f"{name} passes the draft 2020-12 meta-schema check")
            except Exception as exc:  # noqa: BLE001
                report.fail(f"{name} fails the draft 2020-12 meta-schema check: {exc}")

    def validate_with(kind: str, schema_name: str, instance):
        """Return (valid, errors) using the requested validator kind."""
        if kind == "jsonschema":
            errors = sorted(jsonschema_validators[schema_name].iter_errors(instance),
                            key=lambda e: list(e.absolute_path))
            return (not errors), [e.message for e in errors]
        schema = schemas[schema_name]
        errors = fallback_validate(instance, schema, schema)
        return verdict(errors), errors

    def check_fixture(name: str, expect_valid: bool) -> None:
        instance = fixtures.get(name)
        if instance is None:
            report.fail(f"cannot validate fixtures/{name}: not loaded")
            return
        schema_name = "CDRR-SCHEMA.json" if instance.get("record_kind") == "CDRR" else "RECEIPT-SCHEMA.json"
        outcomes = {}
        if have_jsonschema and schema_name in jsonschema_validators:
            outcomes["jsonschema"] = validate_with("jsonschema", schema_name, instance)
        outcomes["fallback"] = validate_with("fallback", schema_name, instance)
        for kind, (valid, errors) in outcomes.items():
            if expect_valid and valid:
                report.ok(f"fixtures/{name} validates against {schema_name} [{kind}]")
            elif not expect_valid and not valid:
                report.ok(f"fixtures/{name} correctly REJECTED by {schema_name} [{kind}]")
            elif expect_valid:
                report.fail(f"fixtures/{name} should validate but FAILED {schema_name} [{kind}]: {errors[:5]}")
            else:
                report.fail(f"fixtures/{name} should be rejected but PASSED {schema_name} [{kind}]")
        if len(outcomes) > 1:
            verdicts = {valid for valid, _ in outcomes.values()}
            if len(verdicts) == 1:
                report.ok(f"fixtures/{name}: jsonschema and fallback validator verdicts AGREE")
            else:
                report.fail(f"fixtures/{name}: jsonschema and fallback validator verdicts DISAGREE")

    # ---------------------------------------------------------------- (b)/(c)
    report.info("validator path: "
                + ("jsonschema draft 2020-12 (with stdlib fallback cross-check)"
                   if have_jsonschema else "stdlib minimal structural validator (fallback)"))
    for name in POSITIVE_FIXTURES:
        check_fixture(name, expect_valid=True)
    for name in NEGATIVE_FIXTURES:
        check_fixture(name, expect_valid=False)

    # ------------------------------ refused-shape explicit structural checks
    refused = fixtures.get("sample-cdrr-refused.json")
    if refused is not None:
        if refused.get("disposition", {}).get("final_disposition") == "REFUSE":
            report.ok("refused fixture records final_disposition REFUSE")
        else:
            report.fail("refused fixture does not record final_disposition REFUSE")
        for section in REFUSED_EXTRACTION_SECTIONS:
            sec = refused.get(section)
            if not isinstance(sec, dict):
                report.fail(f"refused fixture: section {section} missing")
                continue
            if sec.get("status") != "NOT_EXERCISED":
                report.fail(f"refused fixture: section {section} status is {sec.get('status')!r}, expected NOT_EXERCISED")
            else:
                report.ok(f"refused fixture: section {section} present with status NOT_EXERCISED")
            if section in {"pages", "text_spans", "structure", "tables",
                           "operation_plan", "applied_operations", "delta_reconciliation"}:
                if sec.get("records") == []:
                    report.ok(f"refused fixture: section {section} records explicitly empty")
                else:
                    report.fail(f"refused fixture: section {section} records not empty")
        nav = refused.get("navigation", {})
        if nav.get("bookmarks") == [] and nav.get("toc_entries") == [] and nav.get("internal_links") == []:
            report.ok("refused fixture: navigation arrays explicitly empty")
        else:
            report.fail("refused fixture: navigation arrays not all explicitly empty")
    else:
        report.fail("refused fixture not loaded; refused-shape checks skipped")

    # ---------------------------------------------------------------- (d)
    try:
        inv_text = INVARIANTS_PATH.read_text(encoding="utf-8")
        invariant_ids = set(re.findall(r"\bINV-\d{2}\b", inv_text))
        missing_in_md = EXPECTED_INVARIANT_IDS - invariant_ids
        if not missing_in_md:
            report.ok(f"INVARIANTS.md defines all {len(EXPECTED_INVARIANT_IDS)} expected invariant ids (INV-01..INV-24)")
        else:
            report.fail(f"INVARIANTS.md is missing expected ids: {sorted(missing_in_md)}")
    except Exception as exc:  # noqa: BLE001
        report.fail(f"INVARIANTS.md could not be read: {exc}")
        invariant_ids = set()

    schema_strings = {name: set(deep_strings(schema)) for name, schema in schemas.items()}
    for name in ("CDRR-SCHEMA.json", "RECEIPT-SCHEMA.json"):
        if name not in schema_strings:
            continue
        strings = schema_strings[name]
        covered = {iid for iid in invariant_ids if any(iid in s for s in strings)}
        uncovered = invariant_ids - covered
        if not uncovered:
            report.ok(f"every INVARIANTS.md invariant id appears inside {name} (descriptions / x-invariants-registry)")
        else:
            report.fail(f"{name} does not cross-reference invariant ids: {sorted(uncovered)}")
        registry = schemas[name].get("x-invariants-registry", {}).get("invariants", {})
        if set(registry.keys()) >= invariant_ids:
            report.ok(f"{name} x-invariants-registry table lists all {len(invariant_ids)} invariant ids")
        else:
            missing = sorted(invariant_ids - set(registry.keys()))
            report.fail(f"{name} x-invariants-registry is missing ids: {missing}")

    # ------------------------------------------------------------------ done
    overall = "PASS" if report.failures == 0 else "FAIL"
    report.info(f"checks run: {report.checks}, failures: {report.failures}")
    report.info(f"OVERALL: {overall}")

    OUTPUT_PATH.write_text("\n".join(report.lines) + "\n", encoding="utf-8")
    print(f"validation {'PASSED' if report.failures == 0 else 'FAILED'}; wrote {OUTPUT_PATH.name}")
    return 0 if report.failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
