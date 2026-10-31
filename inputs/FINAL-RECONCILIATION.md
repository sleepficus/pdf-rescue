# Online PDF reconstruction — final implementation-readiness reconciliation

Date: 2026-09-29

Status: `INVESTIGATION_COMPLETE`

## Final disposition

`NOT_READY_FOR_BUILD`

The product concept and its smallest architecture are coherent, but the first
implementation would still require a builder to invent values that determine
whether a document is accepted, reviewed, refused, or declared unverifiable.
That would make the experiment capable of grading itself after the fact.

This is not a rejection of the product. It is a bounded prerequisite:

> Freeze the protocol, fixtures, independent checks, and decision rules first;
> then build the narrow text-native vertical slice against those frozen rules.

## Evidence reviewed

- the frozen 19-file source capsule, independently reverified 19/19;
- five exact `glm-5.3-flashx` specialist investigations;
- Main's consolidated GLM synthesis;
- five exact `opencode/mimo-v2.6-flash-free` contradiction and coverage seats;
- five exact `opencode-go/deepseek-v4.1-flash` architecture seats;
- five exact `swe-2-high` implementation-readiness seats;
- every Composer `RESULT.md`, `TERMINAL.json`, `SEAT-RECEIPT.json`, and
  `STAGE-MANIFEST.json`;
- the terminal run summary reporting 15 verified seats, zero failures, zero
  pending seats, and zero fallbacks.

Thirteen Composer seats returned `READY_WITH_CHANGES`. Two returned
`NOT_READY`: the contradiction scan and the deterministic disposition-engine
review. Those two findings govern the build decision because both identify
missing definitions that directly control automatic acceptance.

## What is ready

The following design decisions survived every wave:

1. The original PDF is immutable and is never the only record.
2. Phase 0 is intentionally narrow: text-native, unsigned, unencrypted,
   non-active PDFs with page boundaries and reading order preserved.
3. Every visible change is a named operation with a source anchor and expected
   delta.
4. Builder and verifier paths are separated wherever a shared failure mode
   could create a false green.
5. A score cannot overrule one material failure; the worst material element
   governs.
6. `NOT_EXERCISED` never means `PASS`.
7. Tables preserve cell identity, units, displayed numeric strings, and
   arithmetic divergence without silently correcting the source.
8. Existing AcroForms require an exact field/value/widget round trip. Inferred
   fields require explicit human confirmation.
9. Scans preserve the original raster and answer ink; OCR is a searchable
   companion, not source truth.
10. Unsupported or hostile inputs are refused precisely instead of being
    coerced into the happy path.
11. Batch work is isolated per document, with atomic outputs, resumable
    manifests, immutable sources, and no cross-document temporary state.
12. The online service comes only after the local correctness and security
    experiment passes.

The smallest module boundary set is also ready in shape:

`intake -> preflight -> extract -> plan -> apply -> verify -> dispose`

`review-bundle` stays minimal and `run-manifest` stays deferred until the local
vertical slice works.

## Why the build is not ready

### 1. Automatic acceptance is not yet mechanical

The packet does not yet define:

- what counts as a `material` element or material visual difference;
- which verification gates are required for each document class;
- the mapping from `PASS | FAIL | NOT_EXERCISED | ERROR` to a disposition;
- precedence between `REFUSE`, `REVIEW`, and `NOT_VERIFIABLE`;
- six scenario outcomes where two reasonable builders could disagree;
- the effect of a human `CONFIRM` decision on the next disposition.

Until those are frozen, two correct implementations can grade the same file
differently.

### 2. One acceptance gate is in the wrong layer

The human A/B usability study is currently listed inside the per-document
verification chain. That makes automatic `ACCEPT` unreachable for every
document. It belongs at experiment closure, not inside each document's
mechanical acceptance predicate.

### 3. The verification oracle does not exist yet

The capsule intentionally contains no PDF fixtures. The review found:

- no executable expected-disposition manifest;
- 32 concrete missing fixture scenarios;
- only 4 of 11 refusal families represented by controls;
- no benign controls proving the verifier is not simply over-strict;
- no frozen mutation generator or seed record;
- no named independent renderer or second extractor;
- no published normalization whitelist.

Without those, a green test suite would not yet prove the idea.

### 4. Resource and security rules are intent, not measured controls

The design names CPU, memory, decode, object, page, pixel, nesting, disk, and
wall-clock budgets, but it does not freeze values, units, trip behavior, or a
measured isolation primitive. Temporary-file lifecycle, all-output redaction,
no-network evidence, retention, and dependency provenance also need explicit
receipts.

### 5. No product behavior has been exercised

This was an implementation-readiness investigation. No real PDF fixture was
processed, no verification gate ran against a candidate, no usability result
was measured, and no security property was exercised. The correct evidence
state is therefore design-ready-with-prerequisites, not working product.

## One consolidated correction batch

Complete this once before implementation. Do not begin an audit/fix loop.

### Protocol pack

1. Freeze `material` for text tokens, numeric lexemes, table cells, fields,
   reading-order elements, navigation targets, and visible ink.
2. Freeze document classes and the class-by-gate required matrix.
3. Freeze gate statuses, disposition mapping, and precedence.
4. Move the human A/B study to experiment closure.
5. Freeze the normalization whitelist and expected-delta rules.
6. Separate run-level `INVALID_EXPERIMENT` from document dispositions.
7. Define the effect of human confirmation on REVIEW replay.
8. Define independence mechanically rather than by declaration.

### Fixture and oracle pack

9. Create the named development fixtures, 32 missing scenario fixtures, seven
   missing refusal controls, benign controls, and ten sealed holdouts.
10. Freeze deterministic mutation specs, seeds, expected failing gate, and
    expected disposition.
11. Publish an independently authored expected-disposition manifest.
12. Seal holdout access; opening it before protocol freeze invalidates the run.

### Dependency and safety pack

13. Run the bounded dependency/license spike to select a permissive primary
    toolchain, an independent second extractor, and an independent renderer.
14. Freeze resource-budget values after measurement and define trip semantics:
    terminate worker, discard partial candidate, preserve original and receipt,
    emit `REFUSE/resource_budget`.
15. Freeze per-document process isolation, private temporary storage,
    no-network evidence, all-output redaction, retention/access policy, and
    dependency provenance receipts.
16. Freeze receipt and manifest schemas with `NOT_EXERCISED` and `ERROR` as
    first-class states.

## Smallest authorized-next-step candidate

If Steve later authorizes a build, the first build should not be the PDF
reconstructor. It should be the frozen protocol/fixture/oracle pack plus the
dependency spike. Only after that packet is independently sealed should a
builder implement the eight-document text-native development slice.

No production build, installation, upload service, or public deployment was
authorized or performed by this investigation.
