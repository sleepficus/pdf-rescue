"""Lane 03 fixture generator - common rendering helpers.

Frozen per GENERATOR-SPEC.md. No RNG anywhere. All text ASCII.
Base-14 fonts only. Pages are LETTER (612x792), invariant=1 for determinism.
"""
import io
import re

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = letter          # 612 x 792
MARGIN = 72.0
TEXT_W = PAGE_W - 2 * MARGIN     # 468
BODY_TOP = 704.0                 # first baseline for body area
FOOTER_Y = 36.0
HEADER_Y = 752.0
BOTTOM_LIMIT = 56.0              # body cursor must never go below this

HELV = "Helvetica"
HELVB = "Helvetica-Bold"
TIMES = "Times-Roman"
TIMESB = "Times-Bold"
COUR = "Courier"

TITLE_META = {
    "F01": ("F01 memo (synthetic fixture)", "Harborview Logistics (fictional)"),
    "F02": ("F02 business letter (synthetic fixture)", "Cedar & Vane Ltd (fictional)"),
    "F03": ("F03 short report (synthetic fixture)", "Larkspur grants program (fictional)"),
    "F04": ("F04 agenda/notices sheet (synthetic fixture)", "Cedar Hollow Residents Committee (fictional)"),
    "F05": ("F05 two-column article (synthetic fixture)", "Cedar Hollow Review (fictional)"),
    "F06": ("F06 two-column report with numeric table (synthetic fixture)", "Northbridge Supply Co. (fictional)"),
    "F07": ("F07 dense multi-page report (synthetic fixture)", "Alder Grange Estate Trust (fictional)"),
    "F08": ("F08 data-heavy statement page (synthetic fixture)", "Northbridge Supply Co. (fictional)"),
    "R01": ("R01 encrypted refusal control (synthetic fixture)", "lane 03 fixture pack"),
    "R02": ("R02 signed-looking refusal control (synthetic fixture)", "lane 03 fixture pack"),
    "R03": ("R03 XFA refusal control (synthetic fixture)", "lane 03 fixture pack"),
    "R04": ("R04 active-content refusal control (synthetic fixture)", "lane 03 fixture pack"),
    "B01": ("B01 benign clean control (synthetic fixture)", "Riverside Reading Group (fictional)"),
    "B02": ("B02 benign navigation control (synthetic fixture)", "Riverside Reading Group (fictional)"),
}

CREATOR = "lane03-fixture-generator (reportlab, invariant=1)"


def sw(text, font, size):
    return stringWidth(text, font, size)


class LayoutError(Exception):
    pass


class Cursor:
    """Vertical cursor for one text region of one page. Explicit, no auto
    page breaks: content is authored per page/column and overflow raises."""

    def __init__(self, c, x0, x1, y=BODY_TOP):
        self.c = c
        self.x0 = x0
        self.x1 = x1
        self.y = y

    @property
    def width(self):
        return self.x1 - self.x0

    def require_room(self, needed):
        if self.y - needed < BOTTOM_LIMIT:
            raise LayoutError(
                "overflow: need %.1fpt below y=%.1f (limit %.1f)" % (needed, self.y, BOTTOM_LIMIT))

    def gap(self, h):
        self.y -= h
        self.require_room(0)

    def line(self, text, font, size, leading, indent=0.0, align="left"):
        """Draw one literal line (no wrapping)."""
        self.require_room(leading)
        x = self.x0 + indent
        if align == "right":
            x = self.x1 - sw(text, font, size)
        elif align == "center":
            x = self.x0 + (self.width - sw(text, font, size)) / 2.0
        t = self.c.beginText(x, self.y)
        t.setFont(font, size)
        t.textOut(text)
        self.c.drawText(t)
        self.y -= leading

    def rawlines(self, lines, font, size, leading, indent=0.0, align="left"):
        """Draw authored lines verbatim (used for declared line-end
        hyphenation). Each line must fit the region width."""
        w = self.width - indent
        for ln in lines:
            if sw(ln, font, size) > w + 0.5:
                raise LayoutError("rawline too wide (%.1f > %.1f): %r"
                                  % (sw(ln, font, size), w, ln))
        for ln in lines:
            self.line(ln, font, size, leading, indent=indent, align=align)

    def para(self, text, font, size, leading, indent=0.0, align="left"):
        """Greedy word-wrap paragraph preserving internal multi-spaces."""
        w = self.width - indent
        tokens = re.findall(r" +|[^ ]+", text)
        lines, cur = [], ""
        for tok in tokens:
            cand = cur + tok
            if sw(cand, font, size) <= w:
                cur = cand
                continue
            if not tok.strip():
                # trailing spaces do not fit: flush without them
                if cur.strip():
                    lines.append(cur.rstrip())
                cur = ""
                continue
            if sw(tok, font, size) > w:
                raise LayoutError("single word wider than region: %r" % tok)
            if cur.strip():
                lines.append(cur.rstrip())
                cur = tok
            else:
                cur = tok
        if cur.strip():
            lines.append(cur.rstrip())
        for ln in lines:
            self.line(ln, font, size, leading, indent=indent, align=align)

    def rowset(self, rows, font, size, leading, gap_after=8.0,
               label_indent=0.0, value_font=None, value_size=None):
        """Inline numeric row set: label left, value right-aligned."""
        vf = value_font or font
        vs = value_size or size
        for label, value in rows:
            self.require_room(leading)
            t = self.c.beginText(self.x0 + label_indent, self.y)
            t.setFont(font, size)
            t.textOut(label)
            self.c.drawText(t)
            vx = self.x1 - sw(value, vf, vs)
            t2 = self.c.beginText(vx, self.y)
            t2.setFont(vf, vs)
            t2.textOut(value)
            self.c.drawText(t2)
            self.y -= leading
        self.y -= gap_after

    def hrule(self, weight=0.5, pad=2.0):
        self.require_room(pad + weight)
        self.c.setLineWidth(weight)
        self.c.line(self.x0, self.y + pad, self.x1, self.y + pad)


def draw_text_line(c, x, y, text, font, size, align=None, x_right=None, x_center=None):
    if align == "right" or x_right is not None:
        x = x_right - sw(text, font, size)
    if align == "center" or x_center is not None:
        x = x_center - sw(text, font, size) / 2.0
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.textOut(text)
    c.drawText(t)


def draw_wrapped_at(c, x, y_top, width, text, font, size, leading):
    """Greedy wrap for header-zone fragments; returns y below last line."""
    tokens = re.findall(r" +|[^ ]+", text)
    lines, cur = [], ""
    for tok in tokens:
        cand = cur + tok
        if sw(cand, font, size) <= width:
            cur = cand
            continue
        if cur.strip():
            lines.append(cur.rstrip())
        cur = tok.strip() or ""
    if cur.strip():
        lines.append(cur.rstrip())
    y = y_top
    for ln in lines:
        t = c.beginText(x, y)
        t.setFont(font, size)
        t.textOut(ln)
        c.drawText(t)
        y -= leading
    return y


def new_canvas(meta_id):
    title, author = TITLE_META[meta_id]
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, invariant=1)
    c.setTitle(title)
    c.setAuthor(author)
    c.setSubject("Synthetic fixture for the guarded text-native PDF experiment")
    c.setCreator(CREATOR)
    return c, buf
