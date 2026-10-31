"""Double-generation determinism proof.

Generates the full sealed set (14 PDFs) plus all six mutants into two scratch
directories and asserts pairwise sha256 equality. Evidence lines are printed
in SEALED.md format for the lane receipt.

Usage: python3 generator/doublegen_check.py DIR_A DIR_B
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from generator import generate_all
except ImportError:
    import generate_all


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dir_hashes(d):
    out = {}
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".pdf"):
            with open(os.path.join(d, fn), "rb") as f:
                out[fn] = sha(f.read())
    return out


def main():
    dir_a, dir_b = sys.argv[1], sys.argv[2]
    all_ids = list(generate_all.BUILDERS.keys())
    generate_all.emit(dir_a, all_ids)
    generate_all.emit(dir_b, all_ids)
    mutant_ids = list(generate_all.MUTATION_TARGETS.values())
    doc_to_mut = {tid: mid for mid, tid in generate_all.MUTATION_TARGETS.items()}
    generate_all.emit(os.path.join(dir_a, "mutants"), mutant_ids,
                      mutated=doc_to_mut)
    generate_all.emit(os.path.join(dir_b, "mutants"), mutant_ids,
                      mutated=doc_to_mut)

    ha, hb = dir_hashes(dir_a), dir_hashes(dir_b)
    ma, mb = dir_hashes(os.path.join(dir_a, "mutants")), \
        dir_hashes(os.path.join(dir_b, "mutants"))
    assert set(ha) == set(hb), "file sets differ between generations"
    assert set(ma) == set(mb), "mutant file sets differ between generations"
    failures = []
    print("double-generation determinism evidence")
    print("file                                     gen-a sha256 (first 16)   equal")
    for fn in sorted(ha):
        eq = ha[fn] == hb[fn]
        if not eq:
            failures.append(fn)
        print("%-40s %s  %s" % (fn, ha[fn][:16], "OK" if eq else "MISMATCH"))
    for fn in sorted(ma):
        eq = ma[fn] == mb[fn]
        if not eq:
            failures.append(fn)
        print("%-40s %s  %s" % (fn, ma[fn][:16], "OK" if eq else "MISMATCH"))
    total = len(ha) + len(ma)
    print("total files compared: %d ; mismatches: %d" % (total, len(failures)))
    if failures:
        raise SystemExit("DETERMINISM FAILURE: %r" % failures)
    print("DETERMINISM PROVEN: every file byte-identical across generations")


if __name__ == "__main__":
    main()
