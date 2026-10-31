"""Lane 03 fixture generator orchestrator.

Usage (from the lane root):
  python3 generator/generate_all.py --out DIR            # all 14 sealed-set PDFs
  python3 generator/generate_all.py --out DIR --only F01,F05
  python3 generator/generate_all.py --out DIR --mutate M01   # one mutant
  python3 generator/generate_all.py --out DIR --all-mutants  # all six mutants

Writes build-report.json into DIR. Deterministic: no RNG, invariant=1,
pinned trailer IDs. Running twice into two directories must yield identical
sha256 for every file (double-generation proof, see SEALED.md).
"""
import argparse
import hashlib
import json
import os
import sys

LANE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LANE_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from generator import content, controls  # noqa: E402
except ImportError:
    import content, controls  # noqa: E402

import reportlab
import pypdf

BUILDERS = {
    "F01": content.f01, "F02": content.f02, "F03": content.f03,
    "F04": content.f04, "F05": content.f05, "F06": content.f06,
    "F07": content.f07, "F08": content.f08,
    "B01": content.b01, "B02": content.b02,
    "R01": controls.r01, "R02": controls.r02,
    "R03": controls.r03, "R04": controls.r04,
}

MUTATION_TARGETS = {
    "M01": "F01", "M02": "F02", "M03": "F05",
    "M04": "F08", "M05": "F07", "M06": "F04",
}

FILENAMES = {
    "F01": "F01-memo.pdf", "F02": "F02-letter.pdf", "F03": "F03-report.pdf",
    "F04": "F04-agenda.pdf", "F05": "F05-article.pdf",
    "F06": "F06-column-report.pdf", "F07": "F07-dense-report.pdf",
    "F08": "F08-statement.pdf",
    "R01": "R01-encrypted.pdf", "R02": "R02-signed.pdf",
    "R03": "R03-xfa.pdf", "R04": "R04-active.pdf",
    "B01": "B01-clean.pdf", "B02": "B02-clean-navigation.pdf",
}


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def page_count(b):
    from pypdf import PdfReader
    import io
    r = PdfReader(io.BytesIO(b))
    if r.is_encrypted:
        r.decrypt(content.R01_PW)  # known frozen dummy password (R01 only)
    return len(r.pages)


def build(doc_id, mutate=False):
    return BUILDERS[doc_id](mutate=mutate)


def emit(out_dir, ids, mutated=None, report_name="build-report.json"):
    mutated = mutated or {}
    os.makedirs(out_dir, exist_ok=True)
    report = {
        "generator": "lane03-fixture-generator",
        "versions": {"python": sys.version.split()[0],
                     "reportlab": reportlab.Version,
                     "pypdf": pypdf.__version__},
        "seed_record": {"rng": "none", "nominal_seed": 20260929,
                        "mode": "deterministic no-RNG; invariant=1; pinned /ID"},
        "files": [],
    }
    for doc_id in ids:
        is_mutant = doc_id in mutated
        data = build(doc_id, mutate=is_mutant)
        if is_mutant:
            fname = "%s-%s-mutant.pdf" % (doc_id, mutated[doc_id])
        else:
            fname = FILENAMES[doc_id]
        path = os.path.join(out_dir, fname)
        with open(path, "wb") as f:
            f.write(data)
        report["files"].append({
            "id": doc_id,
            "filename": fname,
            "bytes": len(data),
            "sha256": sha256(data),
            "pages": page_count(data),
            "mutant_of": mutated[doc_id] if is_mutant else None,
        })
    with open(os.path.join(out_dir, report_name), "w") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default=None,
                    help="comma-separated fixture ids (default: all 14)")
    ap.add_argument("--mutate", default=None,
                    help="mutation id M01..M06: build only that mutant")
    ap.add_argument("--all-mutants", action="store_true")
    args = ap.parse_args()

    mutated = {}
    if args.mutate:
        mid = args.mutate
        if mid not in MUTATION_TARGETS:
            ap.error("unknown mutation %r" % mid)
        mutated = {MUTATION_TARGETS[mid]: mid}
        ids = [MUTATION_TARGETS[mid]]
    elif args.all_mutants:
        ids = list(MUTATION_TARGETS.values())
        mutated = {v: k for k, v in MUTATION_TARGETS.items()}
    else:
        ids = list(BUILDERS.keys())

    if args.only:
        wanted = [x.strip() for x in args.only.split(",") if x.strip()]
        ids = [x for x in wanted if x in BUILDERS]
        mutated = {k: v for k, v in mutated.items() if k in ids}

    report = emit(args.out, ids, mutated=mutated)
    for entry in report["files"]:
        print("%-28s %7d bytes  %s  pages=%d%s" % (
            entry["filename"], entry["bytes"], entry["sha256"][:16],
            entry["pages"], "  (mutant of %s)" % entry["mutant_of"]
            if entry["mutant_of"] else ""))


if __name__ == "__main__":
    main()
