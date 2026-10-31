# Targeted completion for lane 05

The first exact-FlashX lane 05 request succeeded from the correct model, but
its response ended at the 32,768-token ceiling. `SAFETY-SPEC.md` and
`BUDGETS.json` are present in the preserved partial result, and the
`BUDGETS.json` fenced body parses as valid JSON. `TRIP-CASES.json` was cut off
before its closing fence.

Produce a concise replacement `RESULT.md` of at most 12,000 UTF-8 bytes with
exactly one section and no preamble or epilogue:

`## FILE: TRIP-CASES.json`

Return a complete, valid JSON object inside one fenced `json` block. Preserve
the already frozen limits and semantics from `L05-PARTIAL-RESULT.md`; do not
rewrite the other two files. Include a minimal but sufficient set of positive
and trip cases covering every budget, network use, atomic-output violation,
temp reuse, verifier exhaustion, and crash receipt preservation. Every trip
must discard a partial candidate, preserve and rehash the original, preserve a
receipt, and record the exact fail-closed outcome. Keep it compact.
