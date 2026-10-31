#!/usr/bin/env python3
"""Throwaway self-validation checker for lane 01-protocol-disposition.

Loads DISPOSITION-SPEC.json and SCENARIOS.json from this directory and proves:
  1. structural integrity of the spec (enums, finite whitelist, ordered rules,
     totality fallback);
  2. dispose(class, gate_statuses, reconciliation) is a pure, total function
     implemented directly from the spec's evaluation_dsl + precedence_rules;
  3. every enumerated (class, status-combination) case maps to exactly one
     disposition with a fired precedence rule;
  4. every precedence rule fires for at least one case, with its declared
     disposition;
  5. no case with any REQUIRED gate status != PASS is ever ACCEPT, and no
     out-of-scope class is ever ACCEPT;
  6. the six scenarios resolve to their frozen outcomes via the spec;
  7. the human-confirm replay semantics hold (CONFIRM cannot rescue a FAILed
     gate, and only U-FORCED-REVIEW-OP is confirmable);
  8. the normalization whitelist is finite and explicit.

Pure Python 3 standard library; no third-party packages; no network.
Exit code 0 iff every assertion passes.
"""

import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

GATES = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10"]
STATUS_ENUM = {"PASS", "FAIL", "NOT_EXERCISED", "ERROR"}
DISPOSITION_ENUM = {"ACCEPT", "REVIEW", "REFUSE", "NOT_VERIFIABLE"}
MATRIX_VALUES = {"REQUIRED", "NOT_REQUIRED", "OUT_OF_SCOPE"}

failures = []
checks_run = 0


def check(label, cond, detail=""):
    global checks_run
    checks_run += 1
    if not cond:
        failures.append(f"{label}: {detail}" if detail else label)
        print(f"  FAIL  {label} {detail}")
    else:
        print(f"  ok    {label}" + (f" ({detail})" if detail else ""))


def load(name):
    with open(os.path.join(HERE, name), "r", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Generic evaluator: implements the spec's evaluation_dsl literally.
# ---------------------------------------------------------------------------

def evaluate(cond, ctx, spec):
    """Recursively evaluate one condition object from the DSL."""
    if not isinstance(cond, dict) or len(cond) != 1:
        raise ValueError(f"malformed condition: {cond!r}")
    key, val = next(iter(cond.items()))
    if key == "else":
        return True
    if key == "all_of":
        return all(evaluate(c, ctx, spec) for c in val)
    if key == "any_of":
        return any(evaluate(c, ctx, spec) for c in val)
    if key == "not":
        return not evaluate(val, ctx, spec)
    if key == "class_in":
        return ctx["class"] in val
    if key == "gate_status_in":
        return ctx["gates"].get(val["gate"]) in val["statuses"]
    if key == "any_required_gate_status_in":
        req = spec["class_gate_matrix"][ctx["class"]]
        return any(
            ctx["gates"][g] in val
            for g in GATES
            if req.get(g) == "REQUIRED"
        )
    if key == "all_required_gate_statuses_in":
        req = spec["class_gate_matrix"][ctx["class"]]
        statuses = [ctx["gates"][g] for g in GATES if req.get(g) == "REQUIRED"]
        return all(s in val for s in statuses)
    if key == "recon_outcome_in":
        return ctx["recon"]["outcome"] in val
    if key == "recon_anomaly_kind_in":
        return ctx["recon"].get("anomaly_kind") in val
    if key == "plan_forced_review_unconfirmed":
        return bool(ctx["recon"].get("plan_forced_review", False)) and not ctx["confirmed"]
    raise ValueError(f"unknown DSL atom: {key}")


def dispose(ctx, spec):
    """Pure function: first-match-wins over the ordered precedence rules."""
    for rule in spec["precedence_rules"]:
        if evaluate(rule["when"], ctx, spec):
            return rule["id"], rule["disposition"]
    raise AssertionError("totality fallback missing: no rule fired")


def make_ctx(cls, gates, recon_outcome, anomaly_kind=None,
             plan_forced_review=False, confirmed=False):
    return {
        "class": cls,
        "gates": dict(gates),
        "recon": {
            "outcome": recon_outcome,
            "anomaly_kind": anomaly_kind,
            "plan_forced_review": plan_forced_review,
        },
        "confirmed": confirmed,
    }


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def structural_checks(spec):
    print("[1] Structural integrity of DISPOSITION-SPEC.json")
    check("spec_version present", bool(spec.get("spec_version")), spec.get("spec_version"))
    check("status enum exact", set(spec["gate_statuses"]["enum"]) == STATUS_ENUM)
    check("disposition enum exact", set(spec["document_dispositions"]["enum"]) == DISPOSITION_ENUM)
    check("exactly 10 gates in registry", set(spec["gate_registry"].keys()) == set(GATES))
    classes = spec["document_classes"]
    check("nine classes defined (8 fixture + UNRESOLVED)",
          set(classes.keys()) == {
              "TEXT_SINGLE_COLUMN", "TEXT_MULTI_COLUMN", "TEXT_TABLE",
              "REFUSE_ENCRYPTED", "REFUSE_SIGNED", "REFUSE_XFA", "REFUSE_ACTIVE",
              "BENIGN", "UNRESOLVED"})
    matrix = spec["class_gate_matrix"]
    check("matrix covers all classes", set(matrix.keys()) == set(classes.keys()))
    ok = all(set(row.keys()) == set(GATES) and set(row.values()) <= MATRIX_VALUES
             for row in matrix.values())
    check("matrix is class x G1-G10 with REQUIRED/NOT_REQUIRED/OUT_OF_SCOPE", ok)
    check("all three matrix values exercised",
          {v for row in matrix.values() for v in row.values()} == MATRIX_VALUES)
    rules = spec["precedence_rules"]
    ids = [r["id"] for r in rules]
    check("rule ids unique", len(set(ids)) == len(ids), ",".join(ids))
    check("rule dispositions valid", all(r["disposition"] in DISPOSITION_ENUM for r in rules))
    check("last rule is the else totality fallback",
          rules[-1]["when"] == {"else": True} and rules[-1]["id"] == "PR-14")
    check("every rule has a rationale", all(r.get("rationale") for r in rules))
    # DSL atoms used must all be documented. A condition dict is either a
    # combinator (all_of/any_of/not) or an atom; atom payloads (e.g. the
    # {gate, statuses} object of gate_status_in) are not condition dicts and
    # are deliberately not walked.
    documented = set(spec["evaluation_dsl"]["atoms"]) | set(spec["evaluation_dsl"]["combinators"])
    used = set()
    unknown = set()

    def walk(c):
        if not isinstance(c, dict) or not c:
            unknown.add(repr(c))
            return
        keys = set(c.keys())
        if keys <= documented:
            used.update(keys)
            for k, v in c.items():
                if k in ("all_of", "any_of"):
                    for item in v:
                        walk(item)
                elif k == "not":
                    walk(v)
                # atoms with structured payloads are not recursed into
        else:
            unknown.add(sorted(keys)[0])

    for r in rules:
        walk(r["when"])
    check("all condition keys are documented DSL vocabulary", not unknown and used <= documented,
          f"unknown={sorted(unknown)} missing={sorted(documented - used) if used - documented else ''}")
    check("every documented atom/combinator is used by at least one rule",
          used == documented, f"unused={sorted(documented - used)}")
    # Whitelist finite and explicit.
    wl = spec["normalization_whitelist"]
    entries = wl["entries"]
    check("normalization whitelist is a finite explicit list (3 entries)",
          isinstance(entries, list) and len(entries) == 3
          and [e["id"] for e in entries] == ["N-01", "N-02", "N-03"]
          and all(e.get("rule") for e in entries))
    excluded_blob = " ".join(wl["material_by_exclusion_examples"]).lower()
    check("material-by-exclusion examples present and distinct from whitelist",
          len(wl["material_by_exclusion_examples"]) >= 5
          and all(e["id"].lower() not in excluded_blob for e in entries))
    check("reconciliation outcomes complete",
          set(spec["reconciliation"]["outcomes"]) == {
              "RECONCILED", "UNDECLARED_MATERIAL_DELTA", "OUT_OF_BOUNDS",
              "PLAN_ILLEGAL", "HIDDEN_TEXT_ANOMALY", "CLASSIFIER_CONFLICT",
              "RECONCILIATION_NOT_RUN"})


def enumerate_cases(spec):
    """Yield (label, ctx) cases for every in-scope class and the guards."""
    recon_variants = [
        ("RECONCILED", None),
        ("UNDECLARED_MATERIAL_DELTA", None),
        ("OUT_OF_BOUNDS", None),
        ("PLAN_ILLEGAL", None),
        ("HIDDEN_TEXT_ANOMALY", "DUPLICATE_VERBATIM"),
        ("HIDDEN_TEXT_ANOMALY", "DIVERGENT"),
        ("CLASSIFIER_CONFLICT", None),
        ("RECONCILIATION_NOT_RUN", None),
    ]
    for cls in ["TEXT_SINGLE_COLUMN", "TEXT_MULTI_COLUMN", "TEXT_TABLE", "BENIGN"]:
        req = [g for g in GATES if spec["class_gate_matrix"][cls][g] == "REQUIRED"]
        oos = {g: ("NOT_EXERCISED" if spec["class_gate_matrix"][cls][g] == "OUT_OF_SCOPE"
                   else "PASS") for g in GATES}
        # Full cross product of PASS/FAIL over required gates x recon x plan flags.
        for combo in itertools.product(("PASS", "FAIL"), repeat=len(req)):
            gates = dict(oos)
            gates.update(dict(zip(req, combo)))
            for outcome, kind in recon_variants:
                for forced in (False, True):
                    for confirmed in (False, True):
                        yield (f"{cls}|{'/'.join(combo)}|{outcome}"
                               f"{'' if kind is None else ':' + kind}"
                               f"|forced={forced}|conf={confirmed}",
                               make_ctx(cls, gates, outcome, kind, forced, confirmed))
        # Single-fault sweeps: one required gate in ERROR / NOT_EXERCISED.
        for g in req:
            for s in ("ERROR", "NOT_EXERCISED"):
                gates = dict(oos)
                gates[g] = s
                yield (f"{cls}|sweep:{g}={s}",
                       make_ctx(cls, gates, "RECONCILED", None, False, False))
    # Guard classes: UNRESOLVED and the four REFUSE_* classes.
    for cls in ["UNRESOLVED", "REFUSE_ENCRYPTED", "REFUSE_SIGNED",
                "REFUSE_XFA", "REFUSE_ACTIVE"]:
        for outcome, kind in recon_variants:
            for forced in (False, True):
                yield (f"{cls}|{outcome}"
                       f"{'' if kind is None else ':' + kind}|forced={forced}",
                       make_ctx(cls, {g: "NOT_EXERCISED" for g in GATES},
                                outcome, kind, forced, False))
        yield (f"{cls}|all-PASS-gates",
               make_ctx(cls, {g: "PASS" for g in GATES}, "RECONCILED", None, False, False))


def totality_and_invariants(spec):
    print("[2] Totality, uniqueness, and acceptance invariants over enumerated cases")
    fired_rules = set()
    accept_by_class = {}
    n = 0
    for label, ctx in enumerate_cases(spec):
        n += 1
        rule_id, disp = dispose(ctx, spec)
        fired_rules.add(rule_id)
        # Uniqueness: the fired rule's own condition is true and the returned
        # disposition is the rule's declared one (dispose guarantees both).
        rule = next(r for r in spec["precedence_rules"] if r["id"] == rule_id)
        assert evaluate(rule["when"], ctx, spec) and rule["disposition"] == disp
        req = [g for g in GATES if spec["class_gate_matrix"][ctx["class"]][g] == "REQUIRED"]
        if any(ctx["gates"][g] != "PASS" for g in req):
            if disp == "ACCEPT":
                failures.append(f"ACCEPT with non-PASS required gate: {label}")
        if not spec["document_classes"][ctx["class"]]["in_scope"] and disp == "ACCEPT":
            failures.append(f"ACCEPT for out-of-scope class: {label}")
        if disp == "ACCEPT":
            accept_by_class.setdefault(ctx["class"], label)
    check(f"every enumerated case returned exactly one disposition ({n} cases)", n > 0)
    all_rule_ids = {r["id"] for r in spec["precedence_rules"]}
    check("every precedence rule fires for at least one case",
          fired_rules == all_rule_ids,
          f"missing={sorted(all_rule_ids - fired_rules)}")
    in_scope = [c for c, v in spec["document_classes"].items() if v["in_scope"]]
    check("each in-scope class has at least one ACCEPT case",
          all(c in accept_by_class for c in in_scope),
          f"accept_classes={sorted(accept_by_class)}")
    # Not-ACCEPT invariants, spot-checked explicitly.
    g_fail = {g: "PASS" for g in GATES}
    _, d1 = dispose(make_ctx("TEXT_TABLE", g_fail, "UNDECLARED_MATERIAL_DELTA"), spec)
    check("undeclared material delta refuses", d1 == "REFUSE", d1)
    _, d2 = dispose(make_ctx("TEXT_TABLE", {**g_fail, "G7": "NOT_EXERCISED"}, "RECONCILED"), spec)
    check("NOT_EXERCISED required gate blocks ACCEPT (NOT_VERIFIABLE)", d2 == "NOT_VERIFIABLE", d2)
    _, d3 = dispose(make_ctx("TEXT_TABLE", {**g_fail, "G7": "ERROR"}, "RECONCILED"), spec)
    check("ERROR treated worse than FAIL (blocks ACCEPT)", d3 == "NOT_VERIFIABLE", d3)
    _, d4 = dispose(make_ctx("REFUSE_ENCRYPTED", {g: "PASS" for g in GATES}, "RECONCILED"), spec)
    check("refusal class refuses even with all gates PASS", d4 == "REFUSE", d4)
    _, d5 = dispose(make_ctx("UNRESOLVED", {g: "PASS" for g in GATES}, "RECONCILED"), spec)
    check("UNRESOLVED class is NOT_VERIFIABLE", d5 == "NOT_VERIFIABLE", d5)
    _, d6 = dispose(make_ctx("TEXT_SINGLE_COLUMN", g_fail, "RECONCILIATION_NOT_RUN"), spec)
    check("reconciliation not run -> NOT_VERIFIABLE, never ACCEPT", d6 == "NOT_VERIFIABLE", d6)
    _, d7 = dispose(make_ctx("TEXT_SINGLE_COLUMN", {**g_fail, "G8": "FAIL"}, "RECONCILED"), spec)
    check("post-classification active content refuses (PR-04)", d7 == "REFUSE", d7)
    _, d8 = dispose(make_ctx("TEXT_SINGLE_COLUMN", {**g_fail, "G2": "FAIL"}, "RECONCILED"), spec)
    check("page invariant violation refuses (PR-05)", d8 == "REFUSE", d8)
    g4fail = {**g_fail, "G4": "FAIL"}
    _, d9 = dispose(make_ctx("TEXT_SINGLE_COLUMN", g4fail, "HIDDEN_TEXT_ANOMALY", "DIVERGENT"), spec)
    check("divergent hidden text refuses (PR-06)", d9 == "REFUSE", d9)
    _, d10 = dispose(make_ctx("TEXT_SINGLE_COLUMN", g4fail, "HIDDEN_TEXT_ANOMALY", "DUPLICATE_VERBATIM"), spec)
    check("verbatim-duplicate hidden text reviews, never accepts (PR-10)", d10 == "REVIEW", d10)
    _, d10b = dispose(make_ctx("TEXT_SINGLE_COLUMN", g_fail, "HIDDEN_TEXT_ANOMALY", "DUPLICATE_VERBATIM"), spec)
    check("anomaly without a FAILed G4 is inconsistent evidence -> NOT_VERIFIABLE",
          d10b == "NOT_VERIFIABLE", d10b)
    _, d11 = dispose(make_ctx("TEXT_SINGLE_COLUMN", {**g_fail, "G5": "FAIL"}, "RECONCILED"), spec)
    check("reading-order failure reviews, never accepts (PR-09)", d11 == "REVIEW", d11)
    _, d12 = dispose(make_ctx("TEXT_SINGLE_COLUMN", g_fail, "RECONCILED", None, True, False), spec)
    check("unconfirmed forced-review operation reviews (PR-12)", d12 == "REVIEW", d12)
    _, d13 = dispose(make_ctx("TEXT_SINGLE_COLUMN", g_fail, "RECONCILED", None, True, True), spec)
    check("confirmed forced-review op + all gates PASS -> ACCEPT via PR-13", d13 == "ACCEPT", d13)
    _, d14 = dispose(make_ctx("TEXT_SINGLE_COLUMN", {**g_fail, "G3": "FAIL"}, "RECONCILED", None, True, True), spec)
    check("CONFIRM cannot rescue a FAILed gate (still REFUSE via PR-07)", d14 == "REFUSE", d14)


def scenario_checks(spec, scen):
    print("[3] Scenario resolution against the spec")
    check("exactly six scenarios", len(scen["scenarios"]) == 6,
          str(len(scen["scenarios"])))
    for s in scen["scenarios"]:
        cases = s["evaluation_cases"]
        check(f"{s['id']} has machine-evaluable cases", len(cases) >= 1,
              f"{len(cases)} case(s)")
        for c in cases:
            ctx = make_ctx(
                c["class"], c["gates"], c["recon"]["outcome"],
                c["recon"].get("anomaly_kind"),
                c["recon"].get("plan_forced_review", False),
                c.get("confirmed", False))
            rule_id, disp = dispose(ctx, spec)
            check(f"{s['id']}/{c['case_id']} -> {c['expected_disposition']} "
                  f"via {c['expected_fired_rule']}",
                  disp == c["expected_disposition"] and rule_id == c["expected_fired_rule"],
                  f"got {disp} via {rule_id}")
        # The ambiguous readings themselves must never be ACCEPT; only an
        # explicitly marked compliant_alternative case may expect ACCEPT.
        ambiguous = [c for c in cases
                     if c["kind"] != "compliant_alternative"]
        check(f"{s['id']} ambiguous readings never ACCEPT",
              all(c["expected_disposition"] != "ACCEPT" for c in ambiguous)
              and all(dispose(make_ctx(
                  c["class"], c["gates"], c["recon"]["outcome"],
                  c["recon"].get("anomaly_kind"),
                  c["recon"].get("plan_forced_review", False),
                  c.get("confirmed", False)), spec)[1] != "ACCEPT"
                  for c in ambiguous))


def replay_checks(spec):
    print("[4] Human-confirmation replay semantics")
    replay = spec["human_confirm_replay"]
    check("replay path marked NOT_EXERCISED for this run",
          replay["run_status"] == "NOT_EXERCISED")
    confirmable = [u["id"] for u in replay["uncertainties"] if u["confirmable"]]
    check("only U-FORCED-REVIEW-OP is confirmable", confirmable == ["U-FORCED-REVIEW-OP"])
    nonconf = {u["id"] for u in replay["uncertainties"] if not u["confirmable"]}
    check("meaning-preservation uncertainties are not confirmable",
          {"U-READING-ORDER", "U-HIDDEN-TEXT"} <= nonconf)
    may_never = replay["uncertainties"][0]["may_never"]
    joined = " ".join(may_never).lower()
    check("CONFIRM may never convert FAIL/NOT_EXERCISED/ERROR into a pass",
          "fail, not_exercised, or error" in joined)
    check("CONFIRM may never make an out-of-scope class in-scope",
          "out-of-scope" in joined)


def main():
    spec = load("DISPOSITION-SPEC.json")
    scen = load("SCENARIOS.json")
    print(f"validate.py — lane 01-protocol-disposition self-check "
          f"(spec {spec['spec_version']})")
    print()
    structural_checks(spec)
    print()
    totality_and_invariants(spec)
    print()
    scenario_checks(spec, scen)
    print()
    replay_checks(spec)
    print()
    if failures:
        print(f"RESULT: FAIL — {len(failures)} failing check(s) of {checks_run}")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"RESULT: PASS — all {checks_run} checks passed")
    print("dispose(class, gate_statuses, reconciliation) is total, deterministic,")
    print("and implementable from DISPOSITION-SPEC.json alone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
