# Render review

Date: 2026-09-29
Reviewer: Main

Poppler rendered every original and candidate page at 120 DPI. The review
covered 38 page PNGs through eight source/candidate contact sheets.

| Fixture | Pages reviewed | Visual verdict |
|---|---:|---|
| F01 | 2 source + 2 candidate | PASS — no visible shift or clipping |
| F02 | 1 source + 1 candidate | PASS — intended small sentence spacing cleanup; no clipping |
| F03 | 2 source + 2 candidate | PASS — text, numeric rows, footer and rule preserved |
| F04 | 1 source + 1 candidate | PASS — agenda and notices preserved; no hidden visible ink |
| F05 | 3 source + 3 candidate | PASS — both columns and left-to-right layout preserved |
| F06 | 3 source + 3 candidate | PASS — two-column layout and numeric strings preserved |
| F07 | 4 source + 4 candidate | PASS — TOC, sections, headers and footers preserved |
| F08 | 3 source + 3 candidate | PASS — grid, row labels, prices and total preserved |

No page was blank, truncated, reordered, rotated, or visibly corrupted. F02's
automated changed-pixel fraction was `0.0033140819964349376`; the frozen limit
was `0.005`. All other candidates had a zero fraction.

Contact sheets are under `outputs/renders/contact-sheets/`; individual PNGs are
under `outputs/renders/source/` and `outputs/renders/candidate/`.
