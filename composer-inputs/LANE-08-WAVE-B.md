# Lane 08 — plan and apply

Implement only these files under the shared integration contract:

- `pdfslice/planner.py`
- `pdfslice/builder.py`
- `tests/test_builder.py`

Required behavior:

1. Explicit plans use only the ten frozen lane-01 operations and twelve frozen
   delta ids, with stable anchors, page scope, and bounded magnitudes.
2. F01-F08 include OP_STRUCTURE_TAGS; B01/B02 have zero operations; refused or
   unresolved records are not built.
3. Reconstruct supported sealed documents deterministically with installed
   reportlab + pypdf, preserving page count/order/MediaBox/CropBox/page text
   ownership and numeric lexemes. Use only base-14 fonts and fixed metadata.
4. Add an actual structure tree: marked-content MCIDs, StructTreeRoot,
   MarkInfo, StructParents, ParentTree, and stable structure elements.
5. Add bookmarks and verified internal navigation only when the plan declares
   them. Do not make network/external links.
6. Write only to the supplied temp candidate path. Never publish/rename final,
   mutate source, or repair after verifier results.
7. Tests check deterministic candidate hashes across two clean builds, source
   immutability, page geometry/count, structure markers, B01/B02 zero-op
   behavior, and refusal to build unsupported classes.

Do not implement intake, independent verification, CLI, or pipeline.

Keep the entire RESULT under 28,000 characters. Implement the smallest honest
vertical slice for the sealed synthetic fixtures; expose explicit unsupported
cases rather than adding speculative machinery. Return code blocks only in the
shared format; do not restate the supplied contracts.
