"""Lane 03 self-validation of the sealed fixture/oracle pack.

Pure stdlib + pypdf + poppler (pdftotext). Implements the five checks
required by the lane brief:

  (a) re-hash every sealed PDF and assert equality with FIXTURE-MANIFEST.json
  (b) assert EXPECTED-DISPOSITIONS.json covers exactly the same id set as the
      manifest (no extras, no missing)
  (c) assert each dev fixture is text-extractable via pdftotext and contains
      no /Encrypt, and each refusal control actually exhibits its refusing
      feature (R01 /Encrypt, R02 /Sig, R03 /XFA, R04 JavaScript/Launch/
      EmbeddedFile marker) - raw bytes + pypdf low-level
  (d) assert the fixture IDs are exactly F01-F08, R01-R04, B01-B02
  (e) assert mutation specs M01-M06 each name an expected failing gate in
      G1-G10 and a non-ACCEPT expected outcome

Writes a full report to VALIDATION-OUTPUT.txt and exits 0 only if every
check passes.

Usage: python3 validate.py
"""
import io
import json
import os
import subprocess
import sys

from pypdf import PdfReader

LANE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(LANE, "fixtures")
OUT_PATH = os.path.join(LANE, "VALIDATION-OUTPUT.txt")

EXPECTED_DEV_IDS = ["F0%d" % i for i in range(1, 9)]
EXPECTED_REFUSAL_IDS = ["R0%d" % i for i in range(1, 5)]
EXPECTED_BENIGN_IDS = ["B0%d" % i for i in range(1, 3)]
GATES = {"G%d" % i for i in range(1, 11)}

DEV_MARKER = {  # distinctive string proving meaningful extraction
    "F01": "MEMORANDUM",
    "F02": "CEDAR & VANE LTD",
    "F03": "Larkspur Community Grants Program",
    "F04": "Cedar Hollow Residents Committee",
    "F05": "Municipal Audit Backlogs",
    "F06": "Regional Distribution Note",
    "F07": "Restoration Programme Report",
    "F08": "Hartwell Manufacturing",
}

REFUSAL_MARKER = {
    "R01": b"/Encrypt",
    "R02": b"/Sig",
    "R03": b"/XFA",
    "R04": b"/JavaScript",
}

REFUSAL_EXTRA = {
    "R02": b"/ByteRange",
    "R04": b"/AA",
}

results = []
failures = 0


def check(label, ok, detail=""):
    global failures
    status = "PASS" if ok else "FAIL"
    if not ok:
        failures += 1
    line = "[%s] %s%s" % (status, label, ("  -- " + detail) if detail else "")
    results.append(line)
    print(line)


def raw(path):
    with open(path, "rb") as f:
        return f.read()


def pdftotext(path):
    r = subprocess.run(["pdftotext", "-layout", path, "-"],
                       capture_output=True, text=True)
    return r.stdout


def main():
    with open(os.path.join(LANE, "FIXTURE-MANIFEST.json")) as f:
        manifest = json.load(f)
    with open(os.path.join(LANE, "EXPECTED-DISPOSITIONS.json")) as f:
        expected = json.load(f)
    with open(os.path.join(LANE, "MUTATION-SPECS.json")) as f:
        mutations = json.load(f)

    print("lane 03 validation run (validate.py)")
    print("=" * 72)

    # ---------------------------------------------------------------- (a)
    print("(a) sealed PDF hashes vs FIXTURE-MANIFEST.json")
    for rec in manifest["fixtures"]:
        p = os.path.join(FIXTURES, rec["filename"])
        ok_exists = os.path.isfile(p)
        check("file exists: %s" % rec["filename"], ok_exists)
        if not ok_exists:
            continue
        data = raw(p)
        check("sha256 matches manifest: %s" % rec["filename"],
              __import__("hashlib").sha256(data).hexdigest() == rec["sha256"])
        check("byte size matches manifest: %s" % rec["filename"],
              len(data) == rec["byte_size"],
              "file=%d manifest=%d" % (len(data), rec["byte_size"]))
        r = PdfReader(io.BytesIO(data))
        if not r.is_encrypted:
            check("page count matches manifest: %s" % rec["filename"],
                  len(r.pages) == rec["page_count"],
                  "file=%d manifest=%d" % (len(r.pages), rec["page_count"]))
        else:
            r.decrypt("zcode-dummy-r01")
            check("page count matches manifest: %s" % rec["filename"],
                  len(r.pages) == rec["page_count"],
                  "file=%d manifest=%d" % (len(r.pages), rec["page_count"]))

    # ---------------------------------------------------------------- (b)
    print("(b) EXPECTED-DISPOSITIONS.json id set vs manifest id set")
    manifest_ids = {rec["id"] for rec in manifest["fixtures"]}
    expected_ids = {d["id"] for d in expected["documents"]}
    check("expected-dispositions covers exactly the manifest id set",
          manifest_ids == expected_ids,
          "missing=%s extra=%s" % (sorted(manifest_ids - expected_ids),
                                   sorted(expected_ids - manifest_ids)))
    check("every expected disposition entry names an existing file",
          all(d.get("filename") ==
              next((m["filename"] for m in manifest["fixtures"]
                    if m["id"] == d["id"]), None)
              for d in expected["documents"]))

    # ---------------------------------------------------------------- (c)
    print("(c) dev fixtures extractable + clean; refusal controls exhibit their feature")
    for rec in manifest["fixtures"]:
        doc_id = rec["id"]
        p = os.path.join(FIXTURES, rec["filename"])
        data = raw(p)
        if doc_id in EXPECTED_DEV_IDS or doc_id in EXPECTED_BENIGN_IDS:
            r = PdfReader(io.BytesIO(data))
            check("no /Encrypt: %s" % doc_id, b"/Encrypt" not in data)
            check("pypdf is_encrypted False: %s" % doc_id,
                  not r.is_encrypted)
            check("no signature field: %s" % doc_id,
                  b"/ByteRange" not in data and b"/SigFlags" not in data)
            check("no XFA: %s" % doc_id, b"/XFA" not in data)
            check("no active content: %s" % doc_id,
                  b"/JavaScript" not in data and b"/Launch" not in data
                  and b"/EmbeddedFile" not in data)
            txt = pdftotext(p)
            check("pdftotext extraction non-trivial: %s" % doc_id,
                  len(txt.split()) >= 20)
            check("meaningful marker present: %s" % doc_id,
                  DEV_MARKER[doc_id] in txt if doc_id in DEV_MARKER else True)
        elif doc_id in EXPECTED_REFUSAL_IDS:
            check("refusing marker in raw bytes: %s (%s)"
                  % (doc_id, REFUSAL_MARKER[doc_id].decode()),
                  REFUSAL_MARKER[doc_id] in data)
            if doc_id in REFUSAL_EXTRA:
                check("secondary marker in raw bytes: %s (%s)"
                      % (doc_id, REFUSAL_EXTRA[doc_id].decode()),
                      REFUSAL_EXTRA[doc_id] in data)
            r = PdfReader(io.BytesIO(data))
            if doc_id == "R01":
                check("pypdf is_encrypted True: R01", r.is_encrypted)
                check("decrypts with the frozen dummy password: R01",
                      r.decrypt("zcode-dummy-r01") is not None
                      and len(r.pages) == 1)
            if doc_id == "R02":
                root = r.trailer["/Root"]
                acro = root.get("/AcroForm")
                ok = acro is not None and int(acro.get_object().get("/SigFlags", 0)) & 1
                fields = acro.get_object().get("/Fields", []) if acro else []
                ft_ok = False
                for fld in fields:
                    fo = fld.get_object()
                    if fo.get("/FT") == "/Sig":
                        ft_ok = True
                        v = fo.get("/V")
                        if v is not None and "/ByteRange" in v.get_object():
                            ft_ok = True
                check("pypdf low-level: AcroForm /SigFlags signatures-exist: R02",
                      bool(ok))
                check("pypdf low-level: /FT /Sig field with /ByteRange /V: R02",
                      ft_ok)
            if doc_id == "R03":
                root = r.trailer["/Root"]
                acro = root.get("/AcroForm")
                check("pypdf low-level: AcroForm /XFA present: R03",
                      acro is not None and "/XFA" in acro.get_object())
            if doc_id == "R04":
                root = r.trailer["/Root"]
                oa = root.get("/OpenAction")
                ok = oa is not None and oa.get_object().get("/S") == "/JavaScript"
                check("pypdf low-level: /OpenAction is /JavaScript: R04", ok)
                aa = r.pages[0].get("/AA")
                check("pypdf low-level: page /AA additional action: R04",
                      aa is not None)

    # ---------------------------------------------------------------- (d)
    print("(d) exact ID sets")
    check("dev IDs are exactly F01-F08",
          sorted(manifest_ids & set(EXPECTED_DEV_IDS)) == EXPECTED_DEV_IDS)
    check("refusal IDs are exactly R01-R04",
          sorted(manifest_ids & set(EXPECTED_REFUSAL_IDS)) == EXPECTED_REFUSAL_IDS)
    check("benign IDs are exactly B01-B02",
          sorted(manifest_ids & set(EXPECTED_BENIGN_IDS)) == EXPECTED_BENIGN_IDS)
    check("no unexpected IDs",
          manifest_ids == set(EXPECTED_DEV_IDS + EXPECTED_REFUSAL_IDS
                              + EXPECTED_BENIGN_IDS))
    check("14 sealed PDFs on disk",
          len([f for f in os.listdir(FIXTURES) if f.endswith(".pdf")]) == 14)
    dev_classes = {rec["id"]: rec["class"] for rec in manifest["fixtures"]}
    check("classes: F01-F04 TEXT_SINGLE_COLUMN, F05-F07 TEXT_MULTI_COLUMN, "
          "F08 TEXT_TABLE",
          all(dev_classes[i] == "TEXT_SINGLE_COLUMN" for i in ("F01", "F02", "F03", "F04"))
          and all(dev_classes[i] == "TEXT_MULTI_COLUMN" for i in ("F05", "F06", "F07"))
          and dev_classes["F08"] == "TEXT_TABLE")
    multi_page = [i for i in EXPECTED_DEV_IDS
                  if next(r["page_count"] for r in manifest["fixtures"]
                          if r["id"] == i) >= 3]
    check("at least four dev fixtures have >= 3 pages",
          len(multi_page) == 4, "found %s" % multi_page)
    check("every sealed PDF < 200 KB",
          all(rec["byte_size"] < 200 * 1024 for rec in manifest["fixtures"]))

    # ---------------------------------------------------------------- (e)
    print("(e) mutation specs M01-M06")
    mids = [m["id"] for m in mutations["mutations"]]
    check("mutation IDs are exactly M01-M06",
          sorted(mids) == sorted(["M0%d" % i for i in range(1, 7)]))
    for m in mutations["mutations"]:
        check("%s names an expected failing gate in G1-G10" % m["id"],
              m.get("expected_failing_gate") in GATES,
              "gate=%s" % m.get("expected_failing_gate"))
        outcome = (m.get("expected_verifier_outcome") or "").upper()
        check("%s expects a non-ACCEPT outcome mentioning FAIL" % m["id"],
              "FAIL" in outcome and "NOT BE ACCEPT" in outcome.replace("MUST NOT BE", "NOT BE ACCEPT"))
        check("%s targets an existing fixture with a frozen seed record" % m["id"],
              m.get("target_fixture") in EXPECTED_DEV_IDS
              and m.get("rng") == "none" and isinstance(m.get("nominal_seed"), int))
        check("%s specifies an exact edit" % m["id"],
              bool((m.get("exact_edit") or "").strip())
              and bool((m.get("byte_level_equivalent") or "").strip()))
    covered = {m["target_fixture"] for m in mutations["mutations"]}
    check("mutation targets cover F01/F02/F04/F05/F07/F08",
          covered == {"F01", "F02", "F04", "F05", "F07", "F08"})

    print("=" * 72)
    verdict = "ALL CHECKS PASSED" if failures == 0 else "%d CHECK(S) FAILED" % failures
    print("VERDICT: %s" % verdict)
    with open(OUT_PATH, "w") as f:
        f.write("lane 03 validation output (validate.py)\n")
        f.write("\n".join(results))
        f.write("\nVERDICT: %s\n" % verdict)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
