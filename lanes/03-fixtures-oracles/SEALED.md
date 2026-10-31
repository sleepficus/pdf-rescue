# Lane 03 sealing receipt

Lane: `03-fixtures-oracles`
Seal date (frozen constant): 2026-09-29
Status: `SEALED`

## 1. What is sealed

The 14 PDFs under `fixtures/` are the sealed fixture/oracle pack for the
text-native vertical slice. They are immutable from this point on: any later
defect is recorded as a finding; the sealed bytes are never edited in place.
Re-verification at any time: `python3 validate.py` (175 checks, must report
`ALL CHECKS PASSED`).

## 2. Sealed files and sha256 at seal time

```
1fad93c654fdb14c205719ac8bea7eddecc895b0461736ca2e103dc4e0e611ca  fixtures/B01-clean.pdf
1bedc9c90ce384acccd48c8d9609b35ca6f0bd5bbd714ac9bb7fe8c1da094a71  fixtures/B02-clean-navigation.pdf
203f751515606c543d1d730e707345ef3f3d270a23e1fedc53dc12d147a50ec7  fixtures/F01-memo.pdf
bbe15b2e7fa10f213f9876699db55513d9b66cebd59a3b5e1054e6f3621171ea  fixtures/F02-letter.pdf
54b84a8b39562705b6c9bf77f8a4cb22619d49298f944bb3533bafc04acda683  fixtures/F03-report.pdf
46e1e1ab8b415ffc1b38188ba0f948d617f83c084d1d852136d68e0c5fca4def  fixtures/F04-agenda.pdf
888e283dca1174834cae8bc62ea45ca56435ed92cbb4b54f0b200f4fda3437ef  fixtures/F05-article.pdf
6ba966997b869ed5ea90c39e29b8f6979ac21d7439f0aac99ba496fa5c75dde9  fixtures/F06-column-report.pdf
9021c2194f106e5ba2b5c38b423985d96b90377e5f61305f8fbddf859d790503  fixtures/F07-dense-report.pdf
9479c2bd1ca100f6970e09c222e1950e657f00d2c02cab51a4383024adff0238  fixtures/F08-statement.pdf
f101e7a3e1f56387461048993720af23005b50ef6b8755a1c211af4f79c6c9ca  fixtures/R01-encrypted.pdf
838ae03261655403fd5421337d2e5d33eee853f6999e55709c06cab2d3f735c7  fixtures/R02-signed.pdf
977ec97893ca54e35d2b3c3fb4d9c13fa4b6aa797eb7b9144b062d916855fcd6  fixtures/R03-xfa.pdf
a2fb30725e18db32a755fa3c4e56afff2c46b0d6330547e2d14c528f4ddaea42  fixtures/R04-active.pdf
```

(These values are duplicated in `FIXTURE-MANIFEST.json`, which is the
machine-readable authority. `shasum -a 256 fixtures/*.pdf` must reproduce
this table.)

## 3. Double-generation determinism evidence

Command: `python3 generator/doublegen_check.py scratch/gen-a scratch/gen-b`
(generates the full set twice: 14 sealed PDFs + 6 mutants into each
directory, then asserts pairwise sha256 equality).

Result:

```
file                                     gen-a sha256 (first 16)   equal
B01-clean.pdf                            1fad93c654fdb14c  OK
B02-clean-navigation.pdf                 1bedc9c90ce384ac  OK
F01-memo.pdf                             203f751515606c54  OK
F02-letter.pdf                           bbe15b2e7fa10f21  OK
F03-report.pdf                           54b84a8b39562705  OK
F04-agenda.pdf                           46e1e1ab8b415ffc  OK
F05-article.pdf                          888e283dca117483  OK
F06-column-report.pdf                    6ba966997b869ed5  OK
F07-dense-report.pdf                     9021c2194f106e5b  OK
F08-statement.pdf                        9479c2bd1ca100f6  OK
R01-encrypted.pdf                        f101e7a3e1f56387  OK
R02-signed.pdf                           838ae03261655403  OK
R03-xfa.pdf                              977ec97893ca54e3  OK
R04-active.pdf                           a2fb30725e18db32  OK
F01-M01-mutant.pdf                       beb43e69621f05bd  OK
F02-M02-mutant.pdf                       ebc4a8bb340b836a  OK
F04-M06-mutant.pdf                       6a45dee1c47f4c2f  OK
F05-M03-mutant.pdf                       e061395bc6041167  OK
F07-M05-mutant.pdf                       db0583e7c21ce784  OK
F08-M04-mutant.pdf                       a39bdf0630156a14  OK
total files compared: 20 ; mismatches: 0
DETERMINISM PROVEN: every file byte-identical across generations
```

Method frozen in `GENERATOR-SPEC.md` section 2: reportlab `invariant=1`,
fixed metadata, base-14 fonts, ASCII-only text, pinned pypdf trailer `/ID`
for the post-processed controls, RC4-128 encryption with frozen dummy
passwords, no RNG anywhere (nominal seed 20260929 is for the record only),
no wall-clock timestamps in any artifact.

## 4. Mutation pack status

`MUTATION-SPECS.json` is frozen. All six mutants were built with the
generator's frozen mutation modes and each exhibits its expected signature
(verified in this lane before sealing):

| ID | Target | Expected failing gate | Signature verified |
|---|---|---|---|
| M01 | F01 | G3 | yes |
| M02 | F02 | G3 | yes |
| M03 | F05 | G5 | yes (right column drawn before left on page 1) |
| M04 | F08 | G7 | yes ($1,238.50 present; $1,234.50 count 2 -> 1) |
| M05 | F07 | G6 | yes (outline has 3 entries, 'Section 3: Cost plan' gone) |
| M06 | F04 | G4 | yes (full hidden string in text layer; none in sealed F04) |

Mutants are disposable test inputs for lane 09, produced by
`python3 generator/generate_all.py --out DIR --mutate M0x` (or
`--all-mutants`); they are deterministic and reproducible but are NOT sealed
artifacts.

## 5. Tool provenance

- Python 3.12.7; reportlab 5.0.1 (builder, invariant=1); pypdf 6.14.2
  (control construction: encrypt / AcroForm / XFA / JavaScript objects);
- poppler 26.09.0 `pdftotext` (extraction self-checks in validate.py);
- No installs, no network, no services. Recorded as absent and unused:
  mutool, qpdf, gs, pikepdf, pdfminer, PyMuPDF.

## 6. Scratch disposition

`scratch/` (probe script, probe outputs, gen-a, gen-b) was emptied after
sealing. The generator reproduces everything from the frozen spec.
