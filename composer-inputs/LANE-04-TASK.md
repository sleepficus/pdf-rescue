# Lane 04 task — dependencies and independence

You are lane `04-dependencies-independence` from `ASSIGNMENT.md`.

Use only the sealed packet. Do not install, call the network, inspect unrelated
files, or invent tool availability. Reconcile your work with the frozen lane
01 protocol, lane 02 schemas/invariants, lane 03 fixture/oracle pack, and
`ENVIRONMENT-INVENTORY.md`.

Your single `RESULT.md` must be a complete integration packet containing three
clearly delimited file bodies in this exact order:

1. `DEPENDENCY-SPIKE.md`
2. `TOOLCHAIN.json`
3. `LICENSE-NOTES.md`

Use headings `## FILE: <name>` before each body. `TOOLCHAIN.json` must be valid
JSON when copied verbatim from its section. Freeze exact executable/library
roles, observed versions and paths, decisive-path independence rules, which
gates each tool supports, known gaps, and the fail-closed behavior when a tool
or independence claim is unavailable. Do not claim production safety or a
license fact that is not evidenced in the packet. End with a short mechanical
validation checklist Main can execute locally.
