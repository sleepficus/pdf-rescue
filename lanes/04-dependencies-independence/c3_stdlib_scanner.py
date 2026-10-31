#!/usr/bin/env python3
"""Gate-A C3 probe: an independent, read-only, stdlib-only PDF byte scanner.

This is deliberately narrow.  It inventories indirect objects and reports raw
markers needed by the refusal/security and navigation cross-checks.  It does
not repair, decrypt, render, execute actions, or claim semantic equivalence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


OBJECT_RE = re.compile(rb"(?m)^\s*(\d+)\s+(\d+)\s+obj\b")
TOKEN_PATTERNS = {
    "encrypt": rb"/Encrypt\b",
    "signature_field": rb"/FT\s*/Sig\b|/Type\s*/Sig\b",
    "byte_range": rb"/ByteRange\b",
    "xfa": rb"/XFA\b",
    "javascript": rb"/JavaScript\b|/S\s*/JavaScript\b|/JS\b",
    "launch": rb"/S\s*/Launch\b|/Launch\b",
    "embedded_file": rb"/EmbeddedFile\b|/EmbeddedFiles\b",
    "remote_goto": rb"/S\s*/GoTo[RE]\b",
    "redact": rb"/Subtype\s*/Redact\b",
    "outlines": rb"/Outlines\b",
    "destinations": rb"/Dests\b|/Dest\b",
    "names": rb"/Names\b",
    "annotations": rb"/Annots\b",
    "link_annotations": rb"/Subtype\s*/Link\b",
}


def scan_pdf(path: Path) -> dict:
    data = path.read_bytes()
    objects = [
        {"object": int(m.group(1)), "generation": int(m.group(2)), "offset": m.start()}
        for m in OBJECT_RE.finditer(data)
    ]
    markers = {
        name: len(re.findall(pattern, data))
        for name, pattern in TOKEN_PATTERNS.items()
    }
    return {
        "path": str(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "header_is_pdf": data.startswith(b"%PDF-"),
        "eof_marker_present": b"%%EOF" in data[-1024:],
        "indirect_object_count": len(objects),
        "indirect_objects": objects,
        "markers": markers,
        "refusal_detection": {
            "encrypted": markers["encrypt"] > 0,
            "signed_or_certified": markers["signature_field"] > 0 or markers["byte_range"] > 0,
            "xfa_or_hybrid_xfa": markers["xfa"] > 0,
            "active_content": any(
                markers[key] > 0
                for key in ("javascript", "launch", "embedded_file", "remote_goto", "redact")
            ),
        },
        "navigation_inventory": {
            "outline_marker_count": markers["outlines"],
            "destination_marker_count": markers["destinations"],
            "link_annotation_count": markers["link_annotations"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    result = scan_pdf(args.pdf)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
