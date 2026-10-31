"""Lane 03 fixture content and per-fixture renderers.

All content is original synthetic English about fictional entities.
Renderers are deterministic: no RNG, no timestamps, invariant=1 canvases.
Mutation modes M01..M06 are implemented here exactly as frozen in
MUTATION-SPECS.json.
"""
from .common import (HELV, HELVB, TIMES, TIMESB, COUR,
                     Cursor, LayoutError, MARGIN, PAGE_W, TEXT_W, BODY_TOP,
                     draw_text_line, new_canvas, sw)

COL_X0 = MARGIN                    # left column origin
COL_W = 219.0                      # two-column width (F05/F06)
COL_GUTTER = 30.0
COL_X1 = COL_X0 + COL_W            # 291
RCOL_X0 = COL_X1 + COL_GUTTER      # 321
RCOL_X1 = RCOL_X0 + COL_W          # 540


def finish(c, buf):
    c.save()
    return buf.getvalue()


# ---------------------------------------------------------------- F01 memo

M01_SENTENCE_SOURCE = ("Each session runs forty minutes and covers the "
                       "revised scan points, the exception queue, and the "
                       "escalation contact.")
M01_SENTENCE_MUTANT = ("Each session runs forty minutes and covers the "
                       "revised scan points, the queue, and the "
                       "escalation contact.")


def _f01_header_footer(c, page_no, total):
    draw_text_line(c, MARGIN, 752, "INTERNAL MEMO  REF: HL-2027-014", HELVB, 9)
    draw_text_line(c, PAGE_W - MARGIN, 752, "Harborview Logistics", HELV, 9,
                   x_right=PAGE_W - MARGIN)
    draw_text_line(c, MARGIN, 36, "Harborview Logistics - internal use only",
                   HELV, 8)
    draw_text_line(c, PAGE_W - MARGIN, 36, "Page %d of %d" % (page_no, total),
                   HELV, 8, x_right=PAGE_W - MARGIN)


def f01(mutate=False):
    c, buf = new_canvas("F01")
    p3_text = M01_SENTENCE_MUTANT if mutate else M01_SENTENCE_SOURCE
    total = 2

    _f01_header_footer(c, 1, total)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.line("MEMORANDUM", HELVB, 14, 18, align="center")
    cur.gap(14)
    for label, value in [("To:", "Warehouse Operations Leads"),
                         ("From:", "D. Okafor, Operations Manager"),
                         ("Date:", "14 January 2027"),
                         ("Subject:", "Pallet scanning rollout, phase two")]:
        cur.line("%s  %s" % (label, value), HELV, 10.5, 13.5)
        cur.gap(2)
    cur.gap(10)
    cur.para("This memo confirms the second phase of the pallet scanning "
             "rollout. The first phase covered receiving docks three and "
             "four; the second phase extends the same configuration to the "
             "overflow aisles, where scan rates dropped last quarter.",
             HELV, 10.5, 13)
    cur.gap(14)
    cur.rawlines([
        "We expect the change to be small in scope but visible in daily",
        "reporting. As an exam-",
        "ple, the overflow aisles will appear as separate lines in the",
        "nightly summary once the new scan points are registered, which",
        "affects how operations leads read the weekly trend.",
    ], TIMES, 11, 13.5, indent=18)
    cur.gap(8)
    cur.para(p3_text, HELV, 10.5, 13)
    cur.gap(14)
    cur.line("Rollout checkpoint: docks 3-4 complete; overflow aisles",
             COUR, 9.5, 12, indent=24)
    cur.line("pending; go/no-go review 28 January 2027.", COUR, 9.5, 12,
             indent=24)

    c.showPage()
    _f01_header_footer(c, 2, total)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.rawlines([
        "Supervisors should update the aisle maps before the first shift",
        "ends, because the oper-",
        "ations summary splits overflow scans from dock scans from that",
        "evening onward.",
    ], TIMES, 11, 13.5)
    cur.gap(10)
    cur.para("Questions about the exception queue workflow go to the duty "
             "supervisor, not to the project mailbox.", HELV, 10.5, 13,
             indent=12)
    cur.gap(16)
    cur.para("Please acknowledge receipt of this memo by replying in the "
             "ops channel.", HELV, 10.5, 13)
    cur.gap(20)
    for ln in ["D. Okafor", "Operations Manager", "Harborview Logistics"]:
        cur.line(ln, TIMES, 11, 13.5)
        cur.gap(2)
    return finish(c, buf)


# ---------------------------------------------------------------- F02 letter

M02_SENTENCE_SOURCE = ("Enclosed with this letter are the signed service "
                       "invoice and the receipt for the replacement valve "
                       "assembly.")
M02_SENTENCE_MUTANT = ("Enclosed with this letter are the signed service "
                       "receipt and the invoice for the replacement valve "
                       "assembly.")


def f02(mutate=False):
    c, buf = new_canvas("F02")
    enc = M02_SENTENCE_MUTANT if mutate else M02_SENTENCE_SOURCE

    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.line("CEDAR & VANE LTD", TIMESB, 14, 18, align="center")
    cur.line("22 Quartermaster Row, Portsmouth PO1 2AF", TIMES, 9.5, 12,
             align="center")
    cur.gap(18)
    cur.line("9 February 2027", HELV, 10.5, 13, align="right")
    cur.gap(12)
    for ln in ["Ms. R. Whitfield", "Facilities Director", "Alder Court Estates",
               "12 Beacon Terrace, Portsmouth PO2 8LL"]:
        cur.line(ln, HELV, 10.5, 13)
        cur.gap(2)
    cur.gap(10)
    cur.line("Dear Ms. Whitfield,", HELV, 11, 13.5)
    cur.gap(8)
    cur.para("Thank you for meeting our site team last Thursday. The visit "
             "confirmed that the planned maintenance schedule for Alder "
             "Court can begin in March without disturbing tenants.",
             HELV, 11, 13.5)
    cur.gap(12)
    cur.para(enc, HELV, 11, 13.5)
    cur.gap(6)
    cur.para("Our engineers will  arrive before eight in the morning, so the "
             "loading bay should be clear the evening before. If the parking "
             "permit for the service van has expired, please tell the front "
             "desk and we will issue a new one the same day.", HELV, 11, 13.5)
    cur.gap(12)
    cur.para("The revised contract rate applies from 1 March 2027 and is "
             "fixed for twelve months. No other terms change.", HELV, 11, 13.5)
    cur.gap(14)
    cur.line("Yours sincerely,", HELV, 11, 13.5)
    cur.gap(18)
    for ln in ["T. Marsh", "Client Services Lead", "Cedar & Vane Ltd"]:
        cur.line(ln, HELV, 10.5, 13)
        cur.gap(2)
    cur.gap(14)
    cur.line("cc: Building manager file", HELV, 9, 11)
    cur.line("Cedar & Vane Ltd - registered in England (fictional entity)",
             HELV, 8, 11)
    return finish(c, buf)


# ---------------------------------------------------------------- F03 report


def _f03_footer(c, page_no, total):
    draw_text_line(c, MARGIN, 36,
                   "Larkspur grants quarterly review - synthetic fixture",
                   HELV, 8)
    draw_text_line(c, PAGE_W - MARGIN, 36, "Page %d of %d" % (page_no, total),
                   HELV, 8, x_right=PAGE_W - MARGIN)


def f03(mutate=False):  # mutate unused; F03 has no mutation
    c, buf = new_canvas("F03")
    total = 2
    _f03_footer(c, 1, total)
    c.bookmarkPage("f03-s1")
    c.addOutlineEntry("Summary", "f03-s1", level=0)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.line("Quarterly Review: Larkspur Community Grants Program", TIMESB,
             14, 18)
    cur.gap(12)
    cur.line("1. Summary", HELVB, 11.5, 15)
    cur.gap(4)
    cur.para("The grants program closed its third quarter with a full "
             "pipeline and a modest surplus. Overall demand stayed close to "
             "the forecast prepared in April, and the committee approved "
             "every award on the schedule published in June.", HELV, 10, 12)
    cur.gap(10)
    c.bookmarkPage("f03-s2")
    c.addOutlineEntry("Grant activity", "f03-s2", level=0)
    cur.line("2. Grant activity", HELVB, 11.5, 15)
    cur.gap(4)
    cur.para("Activity was steady through the quarter. Two review panels met "
             "twice each, and the second panel cleared the backlog of "
             "appeals that had accumulated since the spring cycle.",
             HELV, 10, 12, indent=6)
    cur.gap(8)
    cur.rowset([("Applications received", "118"),
                ("Awards approved", "42"),
                ("Median award (USD)", "4,250"),
                ("Success rate", "36%"),
                ("Uncommitted balance", "11,300")],
               HELV, 9.5, 13, gap_after=4, label_indent=6, value_font=COUR,
               value_size=9.5)

    c.showPage()
    _f03_footer(c, 2, total)
    c.bookmarkPage("f03-s3")
    c.addOutlineEntry("Observations", "f03-s3", level=0)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.line("3. Observations", HELVB, 11.5, 15)
    cur.gap(4)
    cur.rawlines([
        "The committee observed that smaller grants were processed faster",
        "than large ones, mostly because large applications required an",
        "external assess-",
        "ment before the panel could vote. That step adds roughly three",
        "weeks to the timetable and should be scheduled in advance.",
    ], TIMES, 10.5, 13)
    cur.gap(10)
    c.bookmarkPage("f03-s4")
    c.addOutlineEntry("Recommended actions", "f03-s4", level=0)
    cur.line("4. Recommended actions", HELVB, 11.5, 15)
    cur.gap(4)
    cur.para("The panel recommends appointing a second assessor for the "
             "winter cycle and publishing the assessment criteria with the "
             "application form.", HELV, 10, 12, indent=12)
    cur.gap(14)
    cur.hrule(weight=0.5, pad=3)
    cur.gap(2)
    cur.para("Note 1: The success rate counts withdrawn applications as "
             "received but not assessed. Figures cover 1 July to 30 "
             "September 2026.", HELV, 8.5, 10.5)
    return finish(c, buf)


# ---------------------------------------------------------------- F04 agenda

HIDDEN_STRING = "CONFIDENTIAL DRAFT DO NOT DISTRIBUTE"


def f04(mutate=False):
    c, buf = new_canvas("F04")
    draw_text_line(c, MARGIN, 36,
                   "Cedar Hollow Residents Committee - synthetic fixture",
                   HELV, 8)
    draw_text_line(c, PAGE_W - MARGIN, 36, "Page 1 of 1", HELV, 8,
                   x_right=PAGE_W - MARGIN)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.line("AGENDA - Cedar Hollow Residents Committee", TIMESB, 13, 17,
             align="center")
    cur.line("Village hall, main room - Thursday 11 March 2027, 19:00",
             TIMES, 9.5, 12, align="center")
    cur.gap(14)
    items = [
        ("1. Welcome and apologies", 0),
        ("2. Minutes of the meeting held on 14 January 2027", 6),
        ("3. Matters arising: footpath lighting;  notice board repairs", 12),
        ("4. Treasurer's report", 0),
        ("5. Grant request: youth football equipment", 18),
        ("6. Any other business", 6),
    ]
    for text, indent in items:
        cur.line(text, HELV, 10.5, 13.5, indent=indent)
        cur.gap(4)
    cur.gap(8)
    cur.line("Chair: M. Aldana   Secretary: P. Lindqvist", HELV, 9.5, 12,
             align="right")
    cur.gap(16)
    cur.line("NOTICES", HELVB, 10, 13)
    cur.gap(3)
    cur.para("The hall kitchen remains closed for repairs until further "
             "notice. Rubbish collection moves to Tuesday from the first "
             "week of April. Contact the secretary to book the hall for "
             "private events.", HELV, 9, 11)
    cur.gap(6)
    cur.para("A refuse sack was left in the main room after the February "
             "meeting; the hall keeper asks that the last person out checks "
             "the corners of the room.", HELV, 9, 11)
    if mutate:
        # M06 hidden-text poison: render mode 3, no visible ink. Placed in
        # the empty top margin so every extractor sees the full string as
        # its own line (pre-seal spec correction: y moved 648 -> 770).
        th = c.beginText(72.0, 770.0)
        th.setFont(HELV, 10)
        th.setTextRenderMode(3)
        th.textOut(HIDDEN_STRING)
        c.drawText(th)
    return finish(c, buf)


# ---------------------------------------------------------------- F05 article

def _f05_footer(c, page_no, total):
    draw_text_line(c, MARGIN, 36, "Cedar Hollow Review - synthetic fixture",
                   HELV, 8)
    draw_text_line(c, PAGE_W - MARGIN, 36, "Page %d of %d" % (page_no, total),
                   HELV, 8, x_right=PAGE_W - MARGIN)


def _f05_col_body(c, page_no, mutate):
    """Returns (left_items, right_items) content per page."""
    if page_no == 1:
        left = [
            ("head", "Why backlogs form"),
            ("para", "Audit backlogs rarely appear because a review team "
                     "works slowly. They form when new cases arrive faster "
                     "than the team can close them for longer than one "
                     "budget cycle. A delay of two or three weeks in spring "
                     "becomes a queue of unopened files by autumn."),
            ("para", "The queue then changes how the office behaves. Staff "
                     "close the easy cases first, and the average age of "
                     "the remaining files  quietly rises while managers "
                     "report throughput instead of backlog age, which hides "
                     "the problem from the people who fund the team."),
        ]
        right = [
            ("para", "The pattern shows up in ordinary intake logs. Intake "
                     "stays flat while closures fall behind, and the gap "
                     "between the two curves is the backlog taking shape. "
                     "Nothing about that gap is mysterious; it is "
                     "arithmetic."),
            ("para", "Three forces push the gap wider. Intake grows with "
                     "the town, rules change more often than training does, "
                     "and vacancies stay unfilled until the next budget "
                     "year."),
        ]
        if mutate:
            right, left = left, right  # M03 page 1 column order swap
        return left, right
    if page_no == 2:
        left = [
            ("head", "Measuring the queue"),
            ("para", "A backlog is best measured by age, not by count. A "
                     "queue of four hundred files that are ninety days old "
                     "is a different problem from four hundred files that "
                     "are nine days old, even though both offices would "
                     "report the same headline number."),
            ("para", "The useful figures are the oldest open case, the "
                     "share of cases older than one quarter, and the "
                     "closure rate over the last ninety days. Those three "
                     "numbers, published monthly, make the queue visible "
                     "without any new tooling."),
        ]
        right = [
            ("rawlines", ["Publishing those three numbers changed the",
                          "conversation. The board stopped asking how busy",
                          "the team was and started asking which rule",
                          "change had made the back-",
                          "log wider without adding staff."]),
            ("para", "In the fictional example used throughout these notes, "
                     "the review office held 1,900 open files at the end of "
                     "2024, and 37 percent of them were older than one "
                     "quarter. The oldest case had waited 214 days."),
        ]
        return left, right
    left = [
        ("head", "Clearing older cases"),
        ("rawlines", ["Clearing a backlog is not the same as working",
                      "faster. The durable approach is to hold a small",
                      "share of capacity for old cases, month after month,",
                      "until the tail is gone. Teams that sprint for one",
                      "quarter usually hand the condi-",
                      "tion of the queue to the next quarter."]),
        ("para", "A simple rule works: every week, close the oldest case "
                 "that can be closed with the evidence already on file. The "
                 "rule needs no software, and it keeps the tail from "
                 "growing while the rest of the queue is serviced."),
    ]
    right = [
        ("head", "What worked in practice"),
        ("para", "In the example office, the oldest-case rule removed 90 "
                 "days from the maximum wait in five months without new "
                 "staff. The share of cases older than one quarter fell "
                 "from 37 percent to 11 percent."),
        ("para", "These are fictional working notes, but the shape of the "
                 "result matches what the wider literature reports: "
                 "backlogs yield to patient, published, age-first rules, "
                 "and they return the moment attention moves elsewhere."),
    ]
    return left, right


def _f05_draw_items(cur, items):
    for kind, payload in items:
        if kind == "head":
            cur.line(payload, HELVB, 10.5, 14)
            cur.gap(4)
        elif kind == "para":
            cur.para(payload, HELV, 9.5, 11.5)
            cur.gap(5)
        elif kind == "rawlines":
            cur.rawlines(payload, HELV, 9.5, 11.5)
            cur.gap(5)
        else:
            raise LayoutError("unknown item kind %r" % kind)


def f05(mutate=False):
    c, buf = new_canvas("F05")
    total = 3
    for page_no in (1, 2, 3):
        if page_no > 1:
            c.showPage()
        _f05_footer(c, page_no, total)
        if page_no == 1:
            cur = Cursor(c, MARGIN, PAGE_W - MARGIN)
            cur.line("Field Notes on Municipal Audit Backlogs", TIMESB, 14,
                     18, align="center")
            cur.line("Prepared for the Cedar Hollow Review - fictional "
                     "working notes, 2026", HELV, 9, 11, align="center")
            cur.gap(10)
            col_top = cur.y
        else:
            col_top = BODY_TOP
        left, right = _f05_col_body(c, page_no, mutate)
        lcur = Cursor(c, COL_X0, COL_X1, y=col_top)
        rcur = Cursor(c, RCOL_X0, RCOL_X1, y=col_top)
        _f05_draw_items(lcur, left)
        _f05_draw_items(rcur, right)
    return finish(c, buf)


# ---------------------------------------------------------------- F06 report

F06_TABLE = [("Regional net revenue", "1,234.50"),
             ("Returns and credits", "(500)"),
             ("Effective tax rate", "12%"),
             ("Variable cost per unit", "$0.75")]


def _f06_footer(c, page_no, total):
    draw_text_line(c, MARGIN, 36,
                   "Northbridge Supply Co. - synthetic fixture", HELV, 8)
    draw_text_line(c, PAGE_W - MARGIN, 36, "Page %d of %d" % (page_no, total),
                   HELV, 8, x_right=PAGE_W - MARGIN)


def _f06_draw_items(cur, items):
    for kind, payload in items:
        if kind == "head":
            cur.line(payload, HELVB, 10.5, 14)
            cur.gap(4)
        elif kind == "table":
            cur.hrule(weight=0.5, pad=3)
            cur.gap(1)
            cur.rowset(payload, HELV, 9.5, 13, gap_after=0)
            cur.hrule(weight=0.5, pad=3)
            cur.gap(5)
        elif kind == "note":
            cur.para(payload, HELV, 8.5, 10.5)
            cur.gap(5)
        elif kind == "para":
            cur.para(payload, HELV, 9.5, 11.5)
            cur.gap(5)
        else:
            raise LayoutError("unknown item kind %r" % kind)


def f06(mutate=False):  # no mutation for F06
    c, buf = new_canvas("F06")
    total = 3
    pages = [
        # (span_items, left_items, right_items)
        (True,
         [("para", "This note summarises regional distribution performance "
                   "for the first quarter of 2027 across the four depots "
                   "served by the Northbridge network. It is a fictional "
                   "working document prepared for fixture use."),
          ("para", "Throughput was close to plan for most of the quarter. "
                   "The Maple Street depot ran ahead of its pick rate after "
                   "the new label printers arrived, while the quayside "
                   "depot lost two days to the February storm closure.")],
         [("para", "Returns deserve attention. Roughly one return in five "
                   "arrived because the pick list showed the old part "
                   "number after a supplier renumbered its catalogue in "
                   "January."),
          ("para", "The operations committee asked for a compact set of "
                   "figures rather than a long narrative. The table "
                   "reproduced on page 2 is the set the regional "
                   "bookkeeper supplied.")]),
        (False,
         [("head", "Q1 figures"),
          ("table", F06_TABLE),
          ("note", "Values are reproduced exactly as supplied. Units and "
                   "bases differ between rows; no arithmetic relationship "
                   "between the displayed figures is asserted.")],
         [("para", "The revenue figure is stated in thousands of dollars "
                   "as reported, the returns figure counts items rather "
                   "than dollars, and the unit cost is stated in dollars "
                   "per unit. The bookkeeper's memo accompanying the "
                   "figures explains each basis."),
          ("para", "Because the bases differ, the figures must be "
                   "reproduced verbatim in any downstream report. "
                   "Reformatting them into a single column of comparable "
                   "numbers would misstate three of the four rows.")]),
        (False,
         [("para", "The committee agreed to keep the quarterly note to one "
                   "table and two pages of prose. Depots will receive their "
                   "own annex from April, drawn from the same source data."),
          ("para", "The next note will report the part-number renumbering "
                   "cleanup as a distinct line, so that returns caused by "
                   "catalogue changes stop blending with genuine quality "
                   "returns.")],
         [("para", "Preparation of the annexes needs no new tooling. The "
                   "depot leads already file weekly summaries in the same "
                   "format the bookkeeper uses, and the renumbering backlog "
                   "is small enough to clear before the summer cycle."),
          ("para", "End of note. Prepared as a synthetic fixture document; "
                   "all figures are fictional and must not be read as real "
                   "financial data.")]),
    ]
    for page_no, (span, left, right) in enumerate(pages, start=1):
        if page_no > 1:
            c.showPage()
        _f06_footer(c, page_no, total)
        if span:
            cur = Cursor(c, MARGIN, PAGE_W - MARGIN)
            cur.line("Northbridge Supply Co. - Regional Distribution Note",
                     TIMESB, 13, 17, align="center")
            cur.line("Quarter 1, 2027 - prepared for the operations "
                     "committee (fictional data)", HELV, 9, 11,
                     align="center")
            cur.gap(10)
            col_top = cur.y
        else:
            col_top = BODY_TOP
        lcur = Cursor(c, COL_X0, COL_X1, y=col_top)
        rcur = Cursor(c, RCOL_X0, RCOL_X1, y=col_top)
        _f06_draw_items(lcur, left)
        _f06_draw_items(rcur, right)
    return finish(c, buf)


# ---------------------------------------------------------------- F07 dense

M05_BOOKMARK_TO_DROP = "Section 3: Cost plan"


def _f07_header_footer(c, page_no, total):
    draw_text_line(c, MARGIN, 752,
                   "Alder Grange Estate Trust - Restoration Programme Report",
                   HELVB, 8.5)
    draw_text_line(c, PAGE_W - MARGIN, 752, "Draft 3", HELV, 8.5,
                   x_right=PAGE_W - MARGIN)
    draw_text_line(c, MARGIN, 36,
                   "Confidential draft for trustees - synthetic fixture",
                   HELV, 8)
    draw_text_line(c, PAGE_W - MARGIN, 36, "Page %d of %d" % (page_no, total),
                   HELV, 8, x_right=PAGE_W - MARGIN)


F07_TOC = [("Section 1: Background", "page 2", "f07-s1"),
           ("Section 2: Condition survey", "page 2", "f07-s2"),
           ("Section 3: Cost plan", "page 3", "f07-s3"),
           ("Section 4: Recommendations", "page 4", "f07-s4")]


def f07(mutate=False):
    c, buf = new_canvas("F07")
    total = 4
    _f07_header_footer(c, 1, total)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.line("Restoration Programme Report", TIMESB, 14, 18)
    cur.line("Alder Grange Estate Trust - trustees' draft, February 2027",
             HELV, 10, 13)
    cur.gap(12)
    cur.line("Contents", HELVB, 11.5, 15)
    cur.gap(3)
    for title, page_ref, _key in F07_TOC:
        cur.line("%s - %s" % (title, page_ref), HELV, 10, 13.5)
        cur.gap(2)
    cur.gap(8)
    cur.para("This report is a trustees' working draft for the 2027 "
             "restoration programme at Alder Grange, a fictional country "
             "estate used here as fixture material. It sets out the "
             "background to the programme, the findings of the condition "
             "survey, the cost plan, and the recommendations the trustees "
             "are asked to approve.", HELV, 10, 12.5)

    c.showPage()
    _f07_header_footer(c, 2, total)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    c.bookmarkPage("f07-s1")
    cur.line("Section 1: Background", HELVB, 12, 16)
    cur.gap(4)
    cur.para("Alder Grange was built in 1897 for the Vane family and passed "
             "to the trust in 1974. The estate comprises the main house, "
             "two cotenanted lodges, a walled garden, and forty-one rooms "
             "of varying condition across three floors. The trust has "
             "maintained the roof and services on an annual cycle, but no "
             "major restoration has been undertaken since 1998.",
             HELV, 10, 12.5)
    cur.gap(8)
    cur.para("The 2027 programme responds to two pressures. Rainwater goods "
             "and roof coverings have reached the end of their service "
             "life, and the trust has committed to opening the east wing "
             "to visitors by the summer of 2029, which requires fire and "
             "access works that cannot be deferred.", HELV, 10, 12.5)
    cur.gap(12)
    c.bookmarkPage("f07-s2")
    cur.line("Section 2: Condition survey", HELVB, 12, 16)
    cur.gap(4)
    cur.para("The condition survey was carried out in November 2026 over "
             "eleven survey days and covered all forty-one rooms together "
             "with the roof voids. The survey found the roof coverings "
             "generally sound but the lead flashings at the end of their "
             "life, and found localised timber decay in the east wing "
             "where gutters have overflowed.", HELV, 10, 12.5)
    cur.gap(8)
    cur.para("The survey report runs to ninety pages and is summarised "
             "here. Its central finding, as detailed in Section 3 "
             "(page 3), is that the roof programme dominates the cost plan "
             "and should be sequenced before any internal works.",
             HELV, 10, 12.5)

    c.showPage()
    _f07_header_footer(c, 3, total)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    c.bookmarkPage("f07-s3")
    cur.line("Section 3: Cost plan", HELVB, 12, 16)
    cur.gap(4)
    cur.para("The cost plan prices the roof and rainwater programme at "
             "2,150,000 and the stonework repairs at 840,000, both at 2027 "
             "prices from the trust's quantity surveyor. Internal access "
             "and fire works for the east wing are priced at 615,000 and "
             "are programmed to follow the roof works by one season.",
             HELV, 10, 12.5)
    cur.gap(8)
    cur.rawlines([
        "Contingency is held at ten percent of the construction total,",
        "which the quantity surveyor considers adequate given the survey",
        "coverage. The main-",
        "tenance reserve continues at its present level and is not drawn",
        "on by the programme.",
    ], TIMES, 10.5, 13)
    cur.gap(8)
    cur.para("Funding is planned from three sources: the trust's own "
             "restoration reserve, a heritage grant application submitted "
             "in January 2027, and a local fundraising appeal. The grant "
             "decision is expected in the autumn; the programme can start "
             "on the roof regardless of the outcome, at reduced scope if "
             "necessary.", HELV, 10, 12.5)

    c.showPage()
    _f07_header_footer(c, 4, total)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    c.bookmarkPage("f07-s4")
    cur.line("Section 4: Recommendations", HELVB, 12, 16)
    cur.gap(4)
    cur.rawlines([
        "The trustees are asked to approve the programme in principle, to",
        "confirm the roof works as the first phase, and to adopt the",
        "survey's recommend-",
        "ations as the basis for the grant application.",
    ], TIMES, 10.5, 13)
    cur.gap(8)
    cur.para("Subject to approval, the quantity surveyor will tender the "
             "roof programme in the spring, with work on site from June. "
             "The estate team will move the walled-garden nursery under "
             "cover in May, and the east wing will remain closed to "
             "visitors through the 2028 season.", HELV, 10, 12.5)
    cur.gap(8)
    cur.para("The next trustees' meeting will review tender returns. This "
             "draft was prepared for fixture use; names, figures, and "
             "findings are fictional.", HELV, 10, 12.5)

    # flat outline (built after all destinations exist)
    for _title, _page_ref, key in F07_TOC:
        title = dict((k, t) for t, _p, k in F07_TOC)[key]
        if mutate and title == M05_BOOKMARK_TO_DROP:
            continue  # M05 bookmark loss
        c.addOutlineEntry(title, key, level=0)
    c.showOutline()
    return finish(c, buf)


# ---------------------------------------------------------------- F08 statement

F08_ROWS = [
    ("Standard bracket", "24", "$0.75", "$18.00"),
    ("Heavy bracket", "6", "$2.40", "$14.40"),
    ("Alignment pin", "150", "$0.08", "$12.00"),
    ("Gasket set", "12", "$3.25", "$39.00"),
    ("Torque washer", "40", "$0.30", "$12.00"),
    ("Retainer clip", "90", "$0.12", "$10.80"),
    ("Guide rail", "4", "$6.10", "$24.40"),
    ("Spacer kit", "7", "$1.95", "$13.65"),
    ("Consolidated freight", "1", "$1,234.50", "$1,234.50"),
    ("Returned goods credit", "2", "($250.00)", "($500.00)"),
]
M04_ROW_LABEL = "Consolidated freight"
M04_FROM = "$1,234.50"
M04_TO = "$1,238.50"
F08_TOTAL = ("TOTAL", "", "", "$878.75")
# rows per page: page1 -> rows[0:4], page2 -> rows[4:8], page3 -> rows[8:10]
F08_ROWS_PER_PAGE = (4, 4, 2)

F08_X_EDGES = [MARGIN, 252.0, 312.0, 402.0, 540.0]
F08_HEADERS = ("Item", "Quantity", "Unit Price", "Amount")
F08_ALIGNS = ("left", "center", "right", "right")


def _f08_frame(c, page_no, total):
    draw_text_line(c, MARGIN, 752, "Northbridge Supply Co.", HELVB, 9.5)
    draw_text_line(c, PAGE_W - MARGIN, 752, "Statement of account", HELV, 9.5,
                   x_right=PAGE_W - MARGIN)
    draw_text_line(c, MARGIN, 36,
                   "Northbridge Supply Co. - synthetic fixture", HELV, 8)
    draw_text_line(c, PAGE_W - MARGIN, 36, "Page %d of %d" % (page_no, total),
                   HELV, 8, x_right=PAGE_W - MARGIN)


def _f08_cell(c, x0, x1, y, text, font, size, align):
    pad = 4.0
    if align == "left":
        x = x0 + pad
    elif align == "right":
        x = x1 - pad - sw(text, font, size)
    else:
        x = x0 + (x1 - x0 - sw(text, font, size)) / 2.0
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.textOut(text)
    c.drawText(t)


def _f08_table_page(c, y_top, rows, with_total=False):
    """Draw the F08 grid with a repeated header row. Returns bottom y."""
    edge = F08_X_EDGES
    row_h = 22.0
    head_h = 20.0
    # header row
    y_head = y_top - head_h
    for i, label in enumerate(F08_HEADERS):
        _f08_cell(c, edge[i], edge[i + 1], y_head + 6.0, label, HELVB, 9.5,
                  F08_ALIGNS[i])
    # grid lines
    c.setLineWidth(0.7)
    c.rect(edge[0], y_top - head_h - row_h * len(rows), edge[-1] - edge[0],
           head_h + row_h * len(rows))
    c.setLineWidth(1.0)
    c.line(edge[0], y_head, edge[-1], y_head)
    c.setLineWidth(0.5)
    for i in range(1, len(edge) - 1):
        c.line(edge[i], y_top - head_h - row_h * len(rows), edge[i], y_top)
    for r in range(len(rows)):
        yr = y_head - row_h * (r + 1)
        c.setLineWidth(0.5)
        c.line(edge[0], yr, edge[-1], yr)
    for r, row in enumerate(rows):
        yb = y_head - row_h * r - 6.0
        for i, cell in enumerate(row):
            font = HELV
            size = 9.5
            if row[0] == "TOTAL":
                font = HELVB
            _f08_cell(c, edge[i], edge[i + 1], yb, cell, font, size,
                      F08_ALIGNS[i])
    bottom = y_head - row_h * len(rows)
    if with_total:
        c.setLineWidth(1.2)
        c.line(edge[0], bottom, edge[-1], bottom)
        # redraw TOTAL row content (row supplied as last element)
        yb = bottom - 6.0
        c.setLineWidth(0.7)
        c.rect(edge[0], bottom - row_h, edge[-1] - edge[0], row_h)
        total_row = F08_TOTAL
        for i, cell in enumerate(total_row):
            _f08_cell(c, edge[i], edge[i + 1], yb, cell, HELVB, 9.5,
                      F08_ALIGNS[i])
        bottom = bottom - row_h
    return bottom


def f08(mutate=False):
    c, buf = new_canvas("F08")
    total = 3
    rows = [list(r) for r in F08_ROWS]
    if mutate:
        for r in rows:
            if r[0] == M04_ROW_LABEL:
                assert r[2] == M04_FROM
                r[2] = M04_TO
    page_rows = []
    idx = 0
    for count in F08_ROWS_PER_PAGE:
        page_rows.append(rows[idx:idx + count])
        idx += count

    for page_no in (1, 2, 3):
        if page_no > 1:
            c.showPage()
        _f08_frame(c, page_no, total)
        if page_no == 1:
            cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
            cur.line("Customer: Hartwell Manufacturing", HELV, 10, 13)
            cur.line("Account: HM-40213", HELV, 10, 13)
            cur.line("Statement date: 31 March 2027", HELV, 10, 13)
            cur.gap(10)
            top = cur.y + 10.0
            _f08_table_page(c, top, page_rows[page_no - 1])
        elif page_no == 2:
            _f08_table_page(c, BODY_TOP + 10.0, page_rows[page_no - 1])
        else:
            cur_top = BODY_TOP + 10.0
            bottom = _f08_table_page(c, cur_top, page_rows[page_no - 1],
                                     with_total=True)
            cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
            cur.y = bottom - 18.0
            cur.para("All amounts in USD.", HELV, 9, 11.5)
            cur.gap(3)
            cur.para("Quantities are whole units; negative amounts appear "
                     "in parentheses.", HELV, 9, 11.5)
            cur.gap(3)
            cur.para("Prepared by the Northbridge Supply Co. billing desk.",
                     HELV, 9, 11.5)
    return finish(c, buf)


# ---------------------------------------------------------------- B01 clean

def _b_footer(c, page_no, total):
    draw_text_line(c, PAGE_W - MARGIN, 36, "Page %d of %d" % (page_no, total),
                   HELV, 8, x_right=PAGE_W - MARGIN)


def b01(mutate=False):
    c, buf = new_canvas("B01")
    total = 2
    _b_footer(c, 1, total)
    c.bookmarkPage("b01-root")
    c.addOutlineEntry("Meeting summary", "b01-root", level=0)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.line("Riverside Reading Group - Meeting Summary", HELVB, 13, 17)
    cur.line("Held on 14 March 2027 at the community library, starting "
             "18:30.", HELV, 10.5, 13)
    cur.gap(6)
    c.bookmarkPage("b01-att")
    c.addOutlineEntry("Attendance", "b01-att", level=1)
    cur.line("Attendance", HELVB, 11, 14)
    cur.gap(4)
    cur.para("Nine members attended: A. Bennett, C. Osei, D. Farrell, "
             "H. Nakamura, J. Iyer, L. Moreau, M. Santos, P. Whitcombe, and "
             "R. Adjei. Two apologies were received.", HELV, 10.5, 13)
    cur.gap(6)
    c.bookmarkPage("b01-disc")
    c.addOutlineEntry("Discussion", "b01-disc", level=1)
    cur.line("Discussion", HELVB, 11, 14)
    cur.gap(4)
    cur.para("The group discussed the March title and agreed a mixed "
             "reception: six members finished it, and two stopped after the "
             "first hundred pages. The conversation covered the pacing of "
             "the middle chapters and the reliability of the narrator.",
             HELV, 10.5, 13)
    cur.gap(6)
    cur.para("The April title was chosen by ballot. The group will meet on "
             "11 April 2027 at the same venue, and H. Nakamura will prepare "
             "the questions.", HELV, 10.5, 13)

    c.showPage()
    _b_footer(c, 2, total)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.para("Two housekeeping points were settled. The shared reading list "
             "moves to the library noticeboard, and the deposit for the "
             "summer venue is refunded if the booking is cancelled before "
             "1 June.", HELV, 10.5, 13)
    cur.gap(6)
    c.bookmarkPage("b01-next")
    c.addOutlineEntry("Next meeting", "b01-next", level=1)
    cur.line("Next meeting", HELVB, 11, 14)
    cur.gap(4)
    cur.para("The next meeting is on 11 April 2027 at 18:30 in the "
             "community library meeting room. L. Moreau will bring the "
             "ballot box and the reading list.", HELV, 10.5, 13)
    c.showOutline()
    return finish(c, buf)


# ---------------------------------------------------------------- B02 clean

def b02(mutate=False):
    c, buf = new_canvas("B02")
    total = 2
    _b_footer(c, 1, total)
    c.bookmarkPage("b02-root")
    c.addOutlineEntry("Standing notes", "b02-root", level=0)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.line("Riverside Reading Group - Standing Notes", HELVB, 13, 17)
    cur.line("Updated 14 March 2027.", HELV, 10.5, 13)
    cur.gap(6)
    c.bookmarkPage("b02-meet")
    c.addOutlineEntry("Monthly meetings", "b02-meet", level=1)
    cur.line("Monthly meetings", HELVB, 11, 14)
    cur.gap(4)
    cur.para("These notes record the standing arrangements of the reading "
             "group. The group meets on the second Sunday of each month, "
             "keeps a shared reading list, and charges no membership fee.",
             HELV, 10.5, 13)
    cur.gap(6)
    link_y = cur.y
    cur.line("See the attendance list on page 2.", HELV, 10.5, 13)
    link_rect = (MARGIN, link_y - 2.0, MARGIN + sw("See the attendance list "
                                                   "on page 2.", HELV, 10.5),
                 link_y + 10.5)
    # attach the link annotation while page 1 is still the current page;
    # the named destination b02-att is resolved at save time.
    c.linkAbsolute("attendance list", "b02-att", link_rect)
    cur.gap(6)
    cur.para("The shared list is maintained by the secretary and read aloud "
             "at the start of each meeting. New titles are added by ballot, "
             "one ballot per meeting, with the proposer speaking for two "
             "minutes.", HELV, 10.5, 13)

    c.showPage()
    _b_footer(c, 2, total)
    c.bookmarkPage("b02-att")
    c.addOutlineEntry("Attendance list", "b02-att", level=1)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.line("Attendance list", HELVB, 11, 14)
    cur.gap(4)
    cur.para("The current attendance list is kept with the meeting "
             "summaries and is available to any member on request. The "
             "list holds nine names; the room comfortably seats twelve.",
             HELV, 10.5, 13)
    c.showOutline()
    return finish(c, buf)


# ---------------------------------------------------------------- refusals

R01_PW = "zcode-dummy-r01"
R01_PW_OWNER = "zcode-dummy-r01-owner"


def refusal_base_bytes(doc_id, title_line, body_text):
    """One-page visible base document for a refusal control."""
    c, buf = new_canvas(doc_id)
    cur = Cursor(c, MARGIN, MARGIN + TEXT_W)
    cur.line(title_line, HELVB, 12, 16)
    cur.gap(8)
    cur.para(body_text, HELV, 10.5, 13)
    cur.gap(6)
    cur.para("This page is the visible carrier for a synthetic control. It "
             "contains no real data and no executable behaviour beyond what "
             "the control is designed to exhibit.", HELV, 10.5, 13)
    return finish(c, buf)
