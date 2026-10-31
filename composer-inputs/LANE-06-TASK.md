# Lane 06 task — independent prebuild breaker

You are lane `06-independent-prebuild-review` from `ASSIGNMENT.md`.

You receive the sealed ZCode lanes 01–03 plus the exact predecessor
`RESULT.md` packets from Composer lanes 04 and 05. Read all of them. Do not
edit or repair their proposals. Attempt to create conflicting dispositions,
find circular/shared-path proofs, identify schema/tool/budget contradictions,
and determine whether Gate A can be made mechanical without invention.

Your single `RESULT.md` must contain two clearly delimited file bodies:

1. `PREBUILD-VERDICT.md`
2. `CONTRADICTIONS.json`

Use headings `## FILE: <name>` before each body. `CONTRADICTIONS.json` must be
valid JSON when copied verbatim from its section. The verdict must be exactly
`READY_FOR_VERTICAL_SLICE` or `NOT_READY`. List every required Gate A check,
its evidence location, its observed state, and any exact stop reason. Treat
`NOT_EXERCISED` as non-passing. Do not authorize implementation if any
prerequisite is ambiguous or non-mechanical. Do not write implementation code.
