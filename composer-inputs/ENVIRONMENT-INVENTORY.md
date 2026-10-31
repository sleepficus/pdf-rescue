# Observed local environment inventory

Observed by Main on 2026-09-29 before Composer dispatch. This is evidence for
lanes 04 and 05, not permission to install or call the network.

## Runtime and libraries

- Bundled Python: 3.12.14
- reportlab: 4.4.9
- pypdf: 6.10.0
- pdfplumber: 0.11.9
- Pillow: 12.3.0
- pdftotext: Poppler 26.09.0 at `/opt/homebrew/bin/pdftotext`
- pdftoppm: Poppler 26.05.0 in the bundled runtime override path
- pdfinfo: Poppler 26.05.0 in the bundled runtime override path
- qpdf: not installed
- mutool: not installed
- Ghostscript (`gs`): not installed

Main successfully ran the lane 03 validator with the bundled Python. All
sealed PDF hashes, sizes, page counts, refusal markers, extractability checks,
fixture-id sets, and mutation specifications passed.

## Sealed fixture measurements

All supported and benign fixtures are US Letter, 612 x 792 points.

| Fixture | Bytes | Pages | `pdftotext -layout` wall s | `pdftoppm -png -r 150` wall s | Render bytes |
|---|---:|---:|---:|---:|---:|
| F01-memo | 3,762 | 2 | 0.04 | 4.96 | 215,253 |
| F02-letter | 2,721 | 1 | 0.01 | 3.35 | 140,085 |
| F03-report | 4,396 | 2 | 0.02 | 3.29 | 176,876 |
| F04-agenda | 2,719 | 1 | 0.01 | 3.20 | 102,644 |
| F05-article | 5,334 | 3 | 0.01 | 3.61 | 371,687 |
| F06-column-report | 4,961 | 3 | 0.01 | 3.44 | 293,953 |
| F07-dense-report | 6,969 | 4 | 0.02 | 3.62 | 461,550 |
| F08-statement | 4,207 | 3 | 0.01 | 3.31 | 166,438 |

The timings are one bounded observation on this Mac, not universal
performance claims. They are sufficient to choose conservative experiment
budgets with ample headroom and explicit trip semantics.

## Refusal controls

- R01-encrypted: 1,856 bytes, one encrypted page; `pdfinfo` without a password
  does not report a normal page count.
- R02-signed: 2,314 bytes, one page.
- R03-xfa: 1,861 bytes, one page.
- R04-active: 1,877 bytes, one page.

## Independence observation

The available minimum lineage split is:

- candidate construction: reportlab and, only where required for PDF object
  metadata/navigation, pypdf;
- independent text observation: Poppler `pdftotext`;
- independent page rendering: Poppler `pdftoppm`;
- additional structural observation: pypdf/pdfplumber, but no claim that two
  tools sharing a decisive library path are independent of one another.

Lane 04 must freeze the exact allowed roles of these tools and identify any
gate that remains `NOT_EXERCISED` or `NOT_VERIFIABLE` because stronger
independence is unavailable. Unknown license facts must remain unknown unless
supported by supplied evidence.
