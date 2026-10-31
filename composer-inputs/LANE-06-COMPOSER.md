# Lane 06 Composer closure task

Act only as the independent prebuild breaker from lane 06. Read all supplied
lane 01–05 artifacts. Do not edit or repair them and do not write
implementation code.

Return one concise `RESULT.md` of at most 14,000 UTF-8 bytes containing exactly:

1. `## FILE: PREBUILD-VERDICT.md`
2. `## FILE: CONTRADICTIONS.json`

The JSON body must be complete valid JSON inside one fenced `json` block. The
verdict must be exactly `READY_FOR_VERTICAL_SLICE` or `NOT_READY`. Attempt to
produce conflicting outcomes, identify shared decisive paths, compare every
schema vocabulary and gate id, test whether the budgets and trip semantics are
mechanical, and flag unproven environment or no-network claims. List every
Gate A requirement with evidence path and PASS/FAIL/NOT_EXERCISED/ERROR.

Do not soften a failure because implementation would be useful. Conversely,
do not require production assurance from this synthetic local experiment.
`NOT_EXERCISED` is not PASS. End with exact machine checks Main should run and
the smallest consolidated correction if the verdict is NOT_READY.
