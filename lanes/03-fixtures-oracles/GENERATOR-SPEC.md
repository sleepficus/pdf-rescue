# Lane 03 generator spec — frozen BEFORE generation

Lane: `03-fixtures-oracles`
Date (frozen constant, not a wall-clock timestamp): 2026-09-29
Status: `SPEC_FROZEN`

This file freezes the seeds, layout constants, content decisions, and control
recipes for the lane 03 fixture/oracle pack. It was written before any sealed
PDF was generated. Any throwaway PDF used to probe library mechanics lives in
`scratch/` and is deleted before sealing; the sealed set is only what this
spec describes and what `SEALED.md` lists.

## 1. Seed record (frozen)

```json
{
  "rng": "none",
  "nominal_seed": 20260929,
  "mode": "fully deterministic; no random number generator is used anywhere in the generator",
  "mutation_nominal_seeds": {
    "M01": 2026092901, "M02": 2026092902, "M03": 2026092903,
    "M04": 2026092904, "M05": 2026092905, "M06": 2026092906
  }
}
```

Nominal seeds are assigned for the record only. Because there is no RNG, every
generation run from the same generator code and spec is required to produce
byte-identical files; this is proven by double generation (see section 8).

## 2. Determinism requirements (frozen)

- `reportlab` canvas is created with `invariant=1`; page size LETTER
  (612 x 792 pt) for every fixture; base-14 fonts only (Helvetica,
  Helvetica-Bold, Times-Roman, Times-Bold, Courier). No TTFs, no images.
- Fixed metadata on every document: Producer/Creator/Title/Author are constant
  strings from the generator; no wall-clock timestamps anywhere in the PDFs or
  in any lane artifact.
- `pypdf` post-processing (controls) pins the trailer `/ID` to fixed bytes and
  writes fixed metadata; `R01` uses RC4-128 with fixed dummy passwords (no
  IV/randomness), so encrypted output is deterministic given the pinned `/ID`.
- Proof: every PDF is generated twice into `scratch/gen-a/` and
  `scratch/gen-b/`; all SHA-256 values must match pairwise; only the `gen-a`
  copy is promoted to `fixtures/`. Evidence is recorded in `SEALED.md`.

## 3. Frozen gate vocabulary (consumed by lanes 01/07/08/09/10)

| Gate | Name |
|---|---|
| G1 | source hash integrity |
| G2 | page geometry |
| G3 | text identity |
| G4 | visible/text agreement (incl. hidden text) |
| G5 | reading order |
| G6 | navigation integrity (bookmarks/outline/TOC/links) |
| G7 | table/numeric lexeme identity |
| G8 | refusal scan (encryption/signature/XFA/active content) |
| G9 | budget/no-network |
| G10 | render accounting |

## 4. Frozen layout constants

- Page: 612 x 792 pt. Single-column text width 468 pt (margins 72).
- Two-column (F05, F06): columns 219 pt, gutter 30 pt, margins 72 pt;
  reading order is left column fully, then right column, per page.
- Header zone baseline y=752; footer zone baseline y=36; body top y=704.
- Hyphenation: greedy word wrap with a frozen hyphenation dictionary; a
  declared break inserts the prefix plus a hyphen at line end. Declared
  hyphenation points (only these): exam-|ple, oper-|ations, recommend-|ations,
  assess-|ment, main-|tenance, distrib-|ution, condi-|tion, back-|log.

## 5. Frozen fixture content decisions

All content is original synthetic English about fictional entities
(Harborview Logistics, Cedar & Vane Ltd, Larkspur grants program, Cedar Hollow
Residents Committee, Cedar Hollow Review, Northbridge Supply Co., Alder Grange
Estate Trust, Hartwell Manufacturing). No real documents, no real data.

- F01 `F01-memo.pdf` — memo, 2 pages, TEXT_SINGLE_COLUMN. Running header
  `INTERNAL MEMO  REF: HL-2027-014` + `Harborview Logistics` and footer
  `Harborview Logistics — internal use only` + `Page N of 2` on every page.
  Ugliness: literal double spaces in some sentences, paragraph gaps varying
  (4/8/14 pt), indents 0/18/24 pt, mixed families/sizes for body
  (Helvetica 10.5, Times-Roman 11, Courier 9.5), declared line-end hyphenation
  (exam-|ple, oper-|ations), NO bookmarks, no structure tags.
- F02 `F02-letter.pdf` — business letter, 1 page, TEXT_SINGLE_COLUMN.
  Centered letterhead, right-aligned date, indented address block, body
  Helvetica 11 with one double-spaced sentence, gaps 6/12/18 pt. NO bookmarks.
  Frozen sentence used by M02: "Enclosed with this letter are the signed
  service invoice and the receipt for the replacement valve assembly."
- F03 `F03-report.pdf` — short report, 2 pages, TEXT_SINGLE_COLUMN. Title 14,
  headings 11.5, body 10, footnote-like trailing note 8.5. Inline numeric row
  set (plain text lines, no grid): Applications received 118; Awards approved
  42; Median award (USD) 4,250; Success rate 36%; Uncommitted balance 11,300.
  FLAT bookmarks (4 top-level entries, no nesting). Declared hyphenation
  (assess-|ment).
- F04 `F04-agenda.pdf` — agenda/notices sheet, 1 page, TEXT_SINGLE_COLUMN.
  Centered Times-Bold title, items at varying indents, one right-aligned line,
  notices block at 9 pt, irregular gaps. NO bookmarks. M06 target.
- F05 `F05-article.pdf` — two-column article, 3 pages, TEXT_MULTI_COLUMN,
  order-sensitive (left column then right column per page). Title spans both
  columns. Mixed sizes 9.5/10, declared hyphenation (back-|log, condi-|tion),
  irregular spacing. NO bookmarks. M03 target (page 1 column order swap).
- F06 `F06-column-report.pdf` — two-column report, 3 pages,
  TEXT_MULTI_COLUMN. Small numeric table (text rows) in the left column of
  page 2 with the four frozen lexemes: `1,234.50`, `(500)`, `12%`, `$0.75`.
  No arithmetic consistency obligation (see ORACLE-NOTES.md). NO bookmarks.
- F07 `F07-dense-report.pdf` — dense report, 4 pages, TEXT_MULTI_COLUMN.
  Repeated header/footer on every page; page 1 carries a Contents list whose
  page numbers are accurate (Section 1 p.2, Section 2 p.2, Section 3 p.3,
  Section 4 p.4); at least one internal cross-reference phrase ("as detailed
  in Section 3 (page 3)"); FLAT bookmarks (4 top-level entries). Declared
  hyphenation (main-|tenance, recommend-|ations). M05 target.
- F08 `F08-statement.pdf` — data statement, 3 pages, TEXT_TABLE. Drawn grid,
  columns Item | Quantity | Unit Price | Amount, ten rows plus TOTAL row
  (arithmetic consistent, descriptive only), units note "All amounts in
  USD." and "negative amounts appear in parentheses". Frozen lexeme used by
  M04: `1,234.50` (Unit Price of row "Consolidated freight"). NO bookmarks.

Multi-page requirement: F05, F06, F08 have 3 pages; F07 has 4 pages (>= 3 for
four fixtures). Every PDF < 200 KB (text-only, trivially satisfied).

## 6. Frozen control recipes

- R01 `R01-encrypted.pdf` — REFUSE_ENCRYPTED. One-page base built here, then
  `pypdf PdfWriter.encrypt(user_password="zcode-dummy-r01", owner_password=
  "zcode-dummy-r01-owner", algorithm="RC4-128")`. Must contain `/Encrypt`.
- R02 `R02-signed.pdf` — REFUSE_SIGNED. AcroForm with `/SigFlags 3`, one
  `/FT /Sig` widget with `/V` signature dictionary containing `/ByteRange
  [0 000 000 000]` placeholder-free deterministic dummy range, `/Contents`
  dummy hex string, `/SubFilter /adbe.pkcs7.detached`, fixed `/M D:20260101000000Z`.
  Must contain `/Sig` and `/ByteRange`.
- R03 `R03-xfa.pdf` — REFUSE_XFA. AcroForm dictionary carries `/XFA` with a
  small synthetic XDP XML stream. Must contain `/XFA`.
- R04 `R04-active.pdf` — REFUSE_ACTIVE. Catalog `/OpenAction` is a
  `/JavaScript` action with a benign synthetic JS string; page 1 also carries
  an `/AA` additional-action JavaScript entry. Must contain `/JavaScript`.
- B01 `B01-clean.pdf` — BENIGN, 2 pages. Consistent Helvetica 10.5, uniform
  6 pt paragraph gaps, zero indent variation, correct hierarchical bookmarks,
  no ugliness. Expected zero operations.
- B02 `B02-clean-navigation.pdf` — BENIGN, 2 pages. As B01 plus exactly one
  internal GoTo link annotation (named destination to page 2) over the visible
  sentence "See the attendance list on page 2." Expected zero or near-zero ops.

## 7. Frozen mutation pack (specs only; lane 09 implements)

Full machine-readable specs live in `MUTATION-SPECS.json` (frozen before
generation because the generator implements exactly these edits as named
deterministic modes). Summary:

| ID | Ability | Target | Exact edit | Expected failing gate | Outcome |
|---|---|---|---|---|---|
| M01 | token deletion | F01 | delete token `exception` from the frozen sentence "Each session runs forty minutes and covers the revised scan points, the exception queue, and the escalation contact." | G3 | FAIL, not ACCEPT |
| M02 | token transposition | F02 | swap `invoice` and `receipt` in the frozen enclosure sentence | G3 | FAIL, not ACCEPT |
| M03 | wrong reading order | F05 | draw page 1 right column before left column | G5 | FAIL, not ACCEPT |
| M04 | numeric reassignment | F08 | Unit Price of row "Consolidated freight": `1,234.50` -> `1,238.50` (same shape) | G7 | FAIL, not ACCEPT |
| M05 | bookmark loss | F07 | remove the flat outline entry "Section 3: Cost plan" | G6 | FAIL, not ACCEPT |
| M06 | hidden-text poison | F04 | insert invisible (render mode 3) Helvetica 10 string "CONFIDENTIAL DRAFT DO NOT DISTRIBUTE" at (72, 648) on page 1 | G4 | FAIL, not ACCEPT |

Each mutant is producible by the sealed generator via
`python3 generator/generate_all.py --out DIR --mutate M0x`, which applies the
edit at the content-model level and re-renders deterministically; lane 09 may
instead implement the equivalent edit on the sealed PDF bytes. No RNG, nominal
seeds per section 1.

## 8. Sealing procedure (frozen)

1. Generate all 14 PDFs into `scratch/gen-a` and again into `scratch/gen-b`.
2. Assert 14/14 pairwise SHA-256 equality; record in `SEALED.md`.
3. Promote the `gen-a` copies to `fixtures/`; write `FIXTURE-MANIFEST.json`
   from the build report; write `EXPECTED-DISPOSITIONS.json` (authored
   independently of any builder code; none exists); run `validate.py`.
4. Empty `scratch/`.

Immutability: after sealing, `fixtures/*.pdf` are never edited. If a defect is
found later, the finding is recorded; the sealed bytes stay untouched.
