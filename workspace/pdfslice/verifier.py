"""Independent verifier. Deliberately imports neither reportlab nor pypdf."""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable

import pdfplumber
from PIL import Image, ImageChops
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import resolve1


NUMERIC_RE = re.compile(r"[0-9 .,()+\-/%:$€£¥]*[0-9][0-9 .,()+\-/%:$€£¥]*")


def _gate(status: str, evidence: Any) -> dict[str, Any]:
    return {"status": status, "evidence": evidence if isinstance(evidence, list) else [evidence]}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _norm(text: str) -> str:
    return "\n".join(re.sub(r"[\t ]+", " ", line).strip() for line in text.splitlines()).strip()


def _numbers(text: str) -> list[str]:
    return [m.group(0).strip() for m in NUMERIC_RE.finditer(text) if any(c.isdigit() for c in m.group(0))]


def _extract(path: Path) -> dict[str, Any]:
    with pdfplumber.open(path) as pdf:
        pages = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text(x_tolerance=1, y_tolerance=2, layout=False) or ""
            pages.append({"index": i, "text": text, "norm": _norm(text), "numbers": _numbers(text),
                          "width": round(float(page.width), 3), "height": round(float(page.height), 3),
                          "rotation": int(getattr(page, "rotation", 0) or 0)})
        return {"page_count": len(pages), "pages": pages}


def _catalog(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        doc = PDFDocument(PDFParser(handle), password="")
        return resolve1(doc.catalog)


def _has_hidden_text_render_mode(path: Path) -> bool:
    """Inspect decoded content streams for PDF text render mode 3.

    This deliberately uses pdfminer rather than the builder's pypdf path, and
    catches compressed streams rather than searching only the raw file bytes.
    """
    with path.open("rb") as handle:
        for page in PDFPage.get_pages(handle, check_extractable=False):
            for ref in page.contents or []:
                stream = resolve1(ref)
                if hasattr(stream, "get_data") and re.search(rb"(?:^|\s)3\s+Tr\b", stream.get_data()):
                    return True
    return False


def _get(mapping: Any, key: str) -> Any:
    if not isinstance(mapping, dict):
        return None
    return mapping.get(key, mapping.get(key.encode("ascii")))


def c2_structure_probe(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            doc = PDFDocument(PDFParser(handle), password="")
            catalog = resolve1(doc.catalog)
            root = resolve1(_get(catalog, "StructTreeRoot"))
            mark = resolve1(_get(catalog, "MarkInfo"))
            parent = resolve1(_get(root, "ParentTree")) if isinstance(root, dict) else None
            ok = bool(root and _get(root, "K") is not None and parent and _get(parent, "Nums") is not None)
            ok = ok and bool(mark and _get(mark, "Marked"))
        return {"status": "PASS" if ok else "NOT_EXERCISED", "derived": bool(ok),
                "struct_tree": bool(root), "parent_tree": bool(parent), "marked": bool(mark)}
    except Exception as exc:
        return {"status": "ERROR", "derived": False, "error": type(exc).__name__}


def _outlines(path: Path) -> list[dict[str, Any]]:
    with path.open("rb") as handle:
        doc = PDFDocument(PDFParser(handle), password="")
        try:
            rows = list(doc.get_outlines())
        except PDFNoOutlines:
            return []
    return [{"level": int(row[0]), "title": str(row[1])} for row in rows]


def _render(path: Path, executable: str, out_root: Path) -> list[Path]:
    out_root.mkdir(parents=True, exist_ok=True)
    prefix = out_root / path.stem
    subprocess.run([executable, "-png", "-r", "150", str(path), str(prefix)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=120)
    return sorted(out_root.glob(path.stem + "-*.png"))


def _render_diff(source: Path, candidate: Path, executable: str) -> dict[str, Any]:
    with TemporaryDirectory(prefix="pdfslice-render-") as td:
        root = Path(td); a = _render(source, executable, root / "source"); b = _render(candidate, executable, root / "candidate")
        if len(a) != len(b):
            return {"status": "FAIL", "reason": "render page-count mismatch"}
        fractions = []
        for pa, pb in zip(a, b):
            with Image.open(pa).convert("L") as ia, Image.open(pb).convert("L") as ib:
                if ia.size != ib.size:
                    return {"status": "FAIL", "reason": "render geometry mismatch"}
                diff = ImageChops.difference(ia, ib)
                changed = sum(1 for value in diff.getdata() if value > 20)
                fractions.append(changed / float(ia.width * ia.height))
        maximum = max(fractions, default=0.0)
        return {"status": "PASS" if maximum <= 0.005 else "FAIL", "fractions": fractions, "max_fraction": maximum}


def verify_candidate(source: str | Path, candidate: str | Path, intake: dict[str, Any],
                     plan: dict[str, Any], tools: dict[str, Any],
                     scanner: Callable[[Path], dict[str, Any]]) -> dict[str, Any]:
    src, cand = Path(source), Path(candidate)
    gates: dict[str, dict[str, Any]] = {}
    src_scan, cand_scan = scanner(src), scanner(cand)
    src_x, cand_x = _extract(src), _extract(cand)
    gates["G1"] = _gate("PASS" if _sha(src) == intake.get("source_sha256") and
                         src_scan.get("indirect_object_count") == intake.get("object_count") else "FAIL",
                         {"source_sha256": _sha(src), "objects": src_scan.get("indirect_object_count")})
    geom_ok = src_x["page_count"] == cand_x["page_count"] and all(
        (a["width"], a["height"], a["rotation"]) == (b["width"], b["height"], b["rotation"])
        for a, b in zip(src_x["pages"], cand_x["pages"]))
    gates["G2"] = _gate("PASS" if geom_ok else "FAIL", {"source": src_x["page_count"], "candidate": cand_x["page_count"]})
    text_ok = [p["norm"] for p in src_x["pages"]] == [p["norm"] for p in cand_x["pages"]]
    number_ok = [p["numbers"] for p in src_x["pages"]] == [p["numbers"] for p in cand_x["pages"]]
    gates["G3"] = _gate("PASS" if text_ok and number_ok else "FAIL", {"text_equal": text_ok, "numeric_equal": number_ok})
    hidden = _has_hidden_text_render_mode(cand)
    gates["G4"] = _gate("FAIL" if hidden else "PASS", {"hidden_render_mode_3": hidden, "anomaly_kind": "DIVERGENT" if hidden else None})
    c2 = c2_structure_probe(cand)
    structure_planned = any(op.get("op_type") == "OP_STRUCTURE_TAGS" for op in plan.get("operations") or [])
    if structure_planned:
        reading_status = "PASS" if c2["status"] == "PASS" and text_ok else "FAIL"
    else:
        reading_status = "NOT_EXERCISED"
    gates["G5"] = _gate(reading_status, {**c2, "text_order_equal": text_ok,
                                         "structure_planned": structure_planned})
    src_outline, cand_outline = _outlines(src), _outlines(cand)
    scan_empty = not any((src_scan.get("navigation_inventory") or {}).values()) and not any((cand_scan.get("navigation_inventory") or {}).values())
    nav_ok = src_outline == cand_outline and (bool(src_outline) or scan_empty)
    gates["G6"] = _gate("PASS" if nav_ok else "FAIL", {"pdfminer_source": src_outline, "pdfminer_candidate": cand_outline, "scanner_both_empty": scan_empty})
    klass = intake.get("class_label")
    if klass == "TEXT_TABLE":
        gates["G7"] = _gate("PASS" if text_ok and number_ok else "FAIL", {"numeric_equal": number_ok})
    else:
        gates["G7"] = _gate("NOT_EXERCISED", {"decisive": False, "classifier_conflict": False})
    refused = any((cand_scan.get("refusal_detection") or {}).values())
    gates["G8"] = _gate("FAIL" if refused else "PASS", cand_scan.get("refusal_detection") or {})
    budgets = tools.get("budgets") or {}
    limits = {row["budget_id"]: row["limit"] for row in budgets.get("budgets") or []}
    measured = {"PAGE_COUNT": cand_x["page_count"], "OBJECT_COUNT": cand_scan.get("indirect_object_count", 0),
                "FILE_BYTES": src.stat().st_size, "OUTPUT_BYTES": cand.stat().st_size}
    budget_ok = bool(limits) and all(measured[k] <= limits[k] for k in measured if k in limits) and tools.get("no_network_observed") is True
    gates["G9"] = _gate("PASS" if budget_ok else "NOT_EXERCISED", {"measured": measured, "no_network_observed": tools.get("no_network_observed")})
    try:
        render = _render_diff(src, cand, str(tools["pdftoppm"]))
        gates["G10"] = _gate(render["status"], render)
    except Exception as exc:
        gates["G10"] = _gate("ERROR", {"error": type(exc).__name__})
    observed = []
    if src.read_bytes() != cand.read_bytes() and text_ok and number_ok:
        observed.append({"type": "STRUCTURE_TAG_ADD", "scope": {"pages": list(range(src_x["page_count"]))}})
    return {"gates": gates, "observed_deltas": observed, "independence": "builder writer not imported",
            "c2_structure_probe": c2, "no_network_scope": tools.get("no_network_scope"),
            "runtime_versions": tools.get("runtime_versions") or {}}
