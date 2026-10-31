# Test receipt

Date: 2026-09-29

## Final checks

- Input SHA-256 manifest: 6/6 `OK`.
- Gate A mechanical verifier: 15/15 `PASS`.
- Lane 07 unit tests: 2/2 `PASS`.
- Lane 08 unit tests: 3/3 `PASS`.
- Lane 09 unit tests: 2/2 `PASS`.
- Integrated clean run: `all_expected=true`, `all_deterministic=true`,
  `all_sources_unchanged=true`, `at_least_one_visible_improvement=true`.
- Integrated candidates: 8/8 `ACCEPT`; no candidate gate was `FAIL` or
  `ERROR`. G7 was correctly `NOT_EXERCISED` for non-table documents and `PASS`
  for F08.
- Hostile mutation run: 6/6 preregistered target gates returned `FAIL`; 0/6
  mutants were accepted.
- Strict pypdf reopen: 8/8 `PASS`.
- Poppler `pdfinfo`: 8/8 `PASS`, expected page counts 2/1/2/1/3/3/4/3.
- Render inventory: 19 source PNGs, 19 candidate PNGs, 8 contact sheets.

The exact console transcript is preserved in `CLOSURE-CHECKS.txt`. Integrated
run records are in `RUN-RESULTS.json`; hostile mutation records are in
`MUTATION-RESULTS.json`.

## Deterministic candidate hashes

| Candidate | SHA-256 |
|---|---|
| F01-memo-candidate.pdf | `369633157961a295ac6c00980dd7952d778928a964e2f3051e12462a8bfffb87` |
| F02-letter-candidate.pdf | `0742185104cf0c5f52ae8fd18abed069c52612ce6f464e6eead806b5dfebe1db` |
| F03-report-candidate.pdf | `eedeaa1f7d25e5eb16837fe1e68b84a24a325e2b72e63ada8f7cad68a934c0ce` |
| F04-agenda-candidate.pdf | `b5c5717b63a7258c49c4d940af7d3d982453f5c74a02da522cb316628cbece89` |
| F05-article-candidate.pdf | `c315dae57466226f29a1dafec0389b4c9f09b358363d64bdd8a1f88da769f3ad` |
| F06-column-report-candidate.pdf | `4dc657fc8497d35280d51643b1f50a7547aa2cc75dd37f3a8e1a54068def5de3` |
| F07-dense-report-candidate.pdf | `9083dd0fd3c5e6b69915bcc8ecb9bf6e86b7d8fe8716d10ea58e421b4296ced1` |
| F08-statement-candidate.pdf | `5f188d23c5f7b1bc50f93b9288c7be810393fb5f36dc2d70d575262cdc26e349` |

## No-network claim boundary

The Python harness blocked socket `connect` and `create_connection` while the
pipeline and mutation checks ran. Poppler child processes were passed local
paths only, but their process-level socket activity was not independently
audited. This is a scoped synthetic-experiment receipt, not a claim of hardened
production sandboxing.
