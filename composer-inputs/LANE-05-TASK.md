# Lane 05 task — safety budgets

You are lane `05-safety-budgets` from `ASSIGNMENT.md`.

Use only the sealed packet. Do not install, call the network, inspect unrelated
files, or invent measurements. Base the guarded experiment limits on the
observed fixture measurements in `ENVIRONMENT-INVENTORY.md`, with conservative
headroom. This is a synthetic local vertical slice, not a production service.

Your single `RESULT.md` must be a complete integration packet containing three
clearly delimited file bodies in this exact order:

1. `SAFETY-SPEC.md`
2. `BUDGETS.json`
3. `TRIP-CASES.json`

Use headings `## FILE: <name>` before each body. Both JSON bodies must be valid
JSON when copied verbatim from their sections. Freeze values, units, scope,
measurement points, trip behavior, atomic-output behavior, private per-run
temporary storage, cleanup/crash evidence, no-network evidence, redaction,
retention, and dependency provenance. Every trip must discard a partial
candidate, preserve the original and receipt, and yield the appropriate
fail-closed evidence state. End with a short mechanical validation checklist.
