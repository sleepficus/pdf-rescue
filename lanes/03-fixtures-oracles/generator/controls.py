"""Lane 03 refusal and benign controls.

R01..R04 are built from a one-page visible base (reportlab) and then
post-processed with pypdf low-level object manipulation. The trailer /ID is
pinned and all metadata is fixed, so output bytes are deterministic.
"""
import io

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (NameObject, DictionaryObject, ArrayObject,
                           ByteStringObject, TextStringObject, NumberObject,
                           FloatObject, DecodedStreamObject)

from . import content

# Pinned trailer IDs (fixed bytes -> deterministic output)
PINNED_IDS = {
    "R01": b"lane03-r01-fixed-id",
    "R02": b"lane03-r02-fixed-id",
    "R03": b"lane03-r03-fixed-id",
    "R04": b"lane03-r04-fixed-id",
}


def _writer_from_base(base_bytes, doc_id):
    r = PdfReader(io.BytesIO(base_bytes))
    w = PdfWriter()
    w.append(r)
    w._ID = ArrayObject([ByteStringObject(PINNED_IDS[doc_id]),
                         ByteStringObject(PINNED_IDS[doc_id])])
    return w


def _write(w):
    b = io.BytesIO()
    w.write(b)
    return b.getvalue()


def r01(mutate=False):
    base = content.refusal_base_bytes(
        "R01", "Synthetic refusal control R01",
        "This one-page synthetic control document carries no special "
        "features of its own. Its bytes are encrypted with a known dummy "
        "password by the fixture generator, so a conforming pipeline must "
        "refuse it at the Phase 0 refusal scan because the input is "
        "encrypted.")
    w = _writer_from_base(base, "R01")
    w.encrypt(user_password=content.R01_PW,
              owner_password=content.R01_PW_OWNER,
              algorithm="RC4-128")
    return _write(w)


def _add_acroform(w, fields):
    acro = DictionaryObject({
        NameObject("/Fields"): ArrayObject(fields),
    })
    acro_ref = w._add_object(acro)
    w._root_object[NameObject("/AcroForm")] = acro_ref
    return acro_ref


def r02(mutate=False):
    base = content.refusal_base_bytes(
        "R02", "Synthetic refusal control R02",
        "This one-page synthetic control document carries an AcroForm with "
        "a signature field and a dummy signature dictionary. It is not a "
        "real signature and signs nothing; a conforming pipeline must "
        "refuse it because the input is signed.")
    w = _writer_from_base(base, "R02")
    page = w.pages[0]
    sig_dict = DictionaryObject({
        NameObject("/Type"): NameObject("/Sig"),
        NameObject("/Filter"): NameObject("/Adobe.PPKLite"),
        NameObject("/SubFilter"): NameObject("/adbe.pkcs7.detached"),
        NameObject("/ByteRange"): ArrayObject([NumberObject(0),
                                               NumberObject(180),
                                               NumberObject(360),
                                               NumberObject(180)]),
        NameObject("/Contents"): ByteStringObject(b"0" * 128),
        NameObject("/M"): TextStringObject("D:20260101000000Z"),
        NameObject("/Name"): TextStringObject("Synthetic Fixture Signer"),
        NameObject("/Reason"): TextStringObject("Synthetic fixture control - not a real signature"),
    })
    sig_v_ref = w._add_object(sig_dict)
    widget = DictionaryObject({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/FT"): NameObject("/Sig"),
        NameObject("/T"): TextStringObject("Signature1"),
        NameObject("/Rect"): ArrayObject([FloatObject(72.0),
                                          FloatObject(600.0),
                                          FloatObject(272.0),
                                          FloatObject(620.0)]),
        NameObject("/V"): sig_v_ref,
        NameObject("/F"): NumberObject(132),
    })
    widget_ref = w._add_object(widget)
    if "/Annots" in page:
        page["/Annots"].append(widget_ref)
    else:
        page[NameObject("/Annots")] = ArrayObject([widget_ref])
    acro = DictionaryObject({
        NameObject("/Fields"): ArrayObject([widget_ref]),
        NameObject("/SigFlags"): NumberObject(3),
    })
    acro_ref = w._add_object(acro)
    w._root_object[NameObject("/AcroForm")] = acro_ref
    return _write(w)


XFA_XML = (b'<?xml version="1.0"?>'
           b'<xdp:xdp xmlns:xdp="http://ns.adobe.com/xdp/">'
           b'<template><subform name="root">'
           b'<field name="syntheticField"/>'
           b'</subform></template>'
           b'</xdp:xdp>')


def r03(mutate=False):
    base = content.refusal_base_bytes(
        "R03", "Synthetic refusal control R03",
        "This one-page synthetic control document carries an AcroForm "
        "dictionary with an /XFA entry containing a small synthetic XDP "
        "stream. A conforming pipeline must refuse it because the input is "
        "XFA.")
    w = _writer_from_base(base, "R03")
    stream = DecodedStreamObject()
    stream.set_data(XFA_XML)
    xfa_ref = w._add_object(stream)
    acro = DictionaryObject({
        NameObject("/Fields"): ArrayObject([]),
        NameObject("/XFA"): ArrayObject([TextStringObject("template"),
                                         xfa_ref]),
    })
    acro_ref = w._add_object(acro)
    w._root_object[NameObject("/AcroForm")] = acro_ref
    return _write(w)


def r04(mutate=False):
    base = content.refusal_base_bytes(
        "R04", "Synthetic refusal control R04",
        "This one-page synthetic control document carries an /OpenAction "
        "JavaScript action and a page /AA additional action. The strings "
        "are inert in a viewer that blocks scripts, and they are synthetic; "
        "a conforming pipeline must refuse the input because it contains "
        "active content.")
    w = _writer_from_base(base, "R04")
    js_action = DictionaryObject({
        NameObject("/S"): NameObject("/JavaScript"),
        NameObject("/JS"): TextStringObject(
            "app.alert('synthetic fixture control R04 - active content');"),
    })
    js_ref = w._add_object(js_action)
    w._root_object[NameObject("/OpenAction")] = js_ref
    page = w.pages[0]
    aa = DictionaryObject({
        NameObject("/O"): DictionaryObject({
            NameObject("/S"): NameObject("/JavaScript"),
            NameObject("/JS"): TextStringObject("this.getField('syntheticField');"),
        }),
    })
    aa_ref = w._add_object(aa)
    page[NameObject("/AA")] = aa_ref
    return _write(w)
