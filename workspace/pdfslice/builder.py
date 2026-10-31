"""Deterministic candidate builder; it never publishes the final path."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, ByteStringObject, ContentStream,
                           DecodedStreamObject, DictionaryObject, NameObject,
                           NumberObject, BooleanObject, TextStringObject)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize_text_strings(content: Any, pdf: PdfWriter) -> bytes:
    """Collapse repeated spaces only inside PDF text-showing operands.

    A raw byte replacement would also rewrite PDF operators and delimiters.
    Parsing the content stream first keeps the operation deliberately bounded
    to strings displayed by Tj, TJ, ', and \" operators.
    """
    stream = ContentStream(content, pdf)
    for operands, operator in stream.operations:
        values: list[Any] = []
        if operator in (b"Tj", b"'", b'"'):
            values = operands
        elif operator == b"TJ" and operands and isinstance(operands[0], ArrayObject):
            values = operands[0]
        for index, value in enumerate(values):
            if isinstance(value, TextStringObject) and "  " in str(value):
                values[index] = TextStringObject(" ".join(str(value).split()))
            elif isinstance(value, ByteStringObject) and b"  " in bytes(value):
                values[index] = ByteStringObject(b" ".join(bytes(value).split()))
    return stream.get_data()


def _mark_and_tidy(writer: PdfWriter, normalize_spacing: bool) -> None:
    elements = ArrayObject()
    parent_nums = ArrayObject()
    for index, page in enumerate(writer.pages):
        content = page.get_contents()
        data = content.get_data() if content is not None else b""
        if normalize_spacing and content is not None:
            data = _normalize_text_strings(content, writer)
        stream = DecodedStreamObject()
        stream.set_data(b"/P <</MCID 0>> BDC\n" + data + b"\nEMC\n")
        page[NameObject("/Contents")] = writer._add_object(stream)
        page[NameObject("/StructParents")] = NumberObject(index)
        elem = DictionaryObject({
            NameObject("/Type"): NameObject("/StructElem"),
            NameObject("/S"): NameObject("/P"),
            NameObject("/Pg"): page.indirect_reference,
            NameObject("/K"): NumberObject(0),
        })
        elem_ref = writer._add_object(elem)
        elements.append(elem_ref)
        parent_nums.extend([NumberObject(index), ArrayObject([elem_ref])])
    parent_tree = writer._add_object(DictionaryObject({
        NameObject("/Nums"): parent_nums,
    }))
    root = DictionaryObject({
        NameObject("/Type"): NameObject("/StructTreeRoot"),
        NameObject("/K"): elements,
        NameObject("/ParentTree"): parent_tree,
        NameObject("/ParentTreeNextKey"): NumberObject(len(writer.pages)),
    })
    root_ref = writer._add_object(root)
    for elem_ref in elements:
        elem_ref.get_object()[NameObject("/P")] = root_ref
    writer._root_object[NameObject("/StructTreeRoot")] = root_ref
    writer._root_object[NameObject("/MarkInfo")] = DictionaryObject({NameObject("/Marked"): BooleanObject(True)})


def build_candidate(source: str | Path, intake: dict[str, Any], plan: dict[str, Any],
                    temp_output: str | Path) -> dict[str, Any]:
    if not plan or intake.get("status") != "READY" or intake.get("class_label") == "BENIGN":
        raise ValueError("unsupported or zero-operation document is not rebuilt")
    src = Path(source); out = Path(temp_output)
    before = src.read_bytes(); source_sha = hashlib.sha256(before).hexdigest()
    reader = PdfReader(src, strict=False)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    normalize = any(op.get("op_type") == "OP_SPACING_NORMALIZE" for op in plan["operations"])
    _mark_and_tidy(writer, normalize)
    writer.add_metadata({
        "/Title": f"Guarded candidate {intake['document_id']}",
        "/Author": "PDFSlice synthetic experiment",
        "/Creator": "PDFSlice 1",
        "/Producer": "PDFSlice 1",
        "/CreationDate": "D:20260929000000Z",
        "/ModDate": "D:20260929000000Z",
    })
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as handle:
        writer.write(handle); handle.flush(); os.fsync(handle.fileno())
    if src.read_bytes() != before:
        raise RuntimeError("source changed during build")
    return {
        "document_id": intake["document_id"], "source_sha256": source_sha,
        "candidate_sha256": _sha(out), "candidate_bytes": out.stat().st_size,
        "page_count": len(writer.pages), "temp_path": str(out),
        "operations_applied": [op["op_type"] for op in plan["operations"]],
    }
