# PDF Rescue

Can we fix a PDF without quietly changing what it says?

PDF Rescue is a local research prototype for that question. It preserves source
files, creates separate candidates, and checks text, numbers, reading order,
page geometry, navigation, and rendered pages before accepting a result.

**Current status: a bounded synthetic experiment, not a general PDF repair app
or a ready-to-install service.**

[Project overview on Misfit Circuit](https://www.misfitcircuit.com/tools/pdf-rescue/)

## What the saved experiment shows

The [September 29 results](outputs/RESULTS.md) record eight text-native fixture
PDFs with their expected acceptance outcomes. One fixture had a measured spacing
improvement; the other seven had no visible change. Two builds produced matching
candidate hashes, and the original fixture bytes remained unchanged.

Six deliberately damaged candidates failed their intended checks; none was
accepted, and all six were sent to REVIEW.
These are results on selected synthetic documents, not a success rate for
arbitrary PDFs or proof of accessibility compliance.

Scanned/OCR, signed, encrypted, XFA, JavaScript-bearing, complex RTL/bidi, private,
and arbitrary online PDFs are outside the demonstrated support. The recorded
agent-provider execution also did not complete as planned; the result report
keeps that failure separate from the artifact checks.

## Start with the evidence

- [Results and scope](outputs/RESULTS.md)
- [Test receipt](outputs/TEST-RECEIPT.md)
- [Render review](outputs/RENDER-REVIEW.md)
- [Side-by-side contact sheets](outputs/renders/contact-sheets/)
- [Mutation results](outputs/MUTATION-RESULTS.json)
- [Implementation](workspace/pdfslice/)

`START-HERE.md`, `ASSIGNMENT.md`, and the lane documents are historical run
instructions. They describe the original experiment; they are not installation
requirements for readers and do not require you to launch a crew of agents.

## Download and inspect

```sh
git clone https://github.com/sleepficus/pdf-rescue.git
cd pdf-rescue
```

The saved reports, PDFs, and contact sheets can be inspected without running the
pipeline. No upload service or hosted PDF processing endpoint is provided here.

## Running the code

There is no portable installer yet. The historical Python 3.12 setup used
`pypdf`, `reportlab`, `pdfplumber`, `pdfminer.six`, and `Pillow`, plus Poppler's
`pdftotext`, `pdftoppm`, and `pdfinfo` programs. See the recorded
[toolchain](lanes/04-dependencies-independence/TOOLCHAIN.json) for the original
versions; those observations are not a portable dependency lock file.

`workspace/run_slice.py` and `workspace/run_mutations.py` contain an absolute
`pdftoppm` path from the original Mac. A fresh machine needs that path adapted
and its dependencies checked before a full rerun. Run in a disposable copy:
the harness writes outputs, so do not overwrite the saved experiment evidence.

One small standard-library check can be run from the repository root without
installing the PDF libraries:

```sh
PYTHONPATH=workspace/pdfslice python3 -m unittest discover -s workspace/tests -p test_verifier.py -v
```

That checks two disposition rules only. It does not rerun PDF reconstruction or
verify the saved experiment end to end.

## Dependencies and reuse

Third-party tools retain their own licenses. The historical
[dependency notes](lanes/04-dependencies-independence/LICENSE-NOTES.md) mark their
license findings as unverified; those notes are not a completed license audit.

Built by Stephen Luc and the Misfit Circuit crew. See the
[Lab](https://www.misfitcircuit.com/labs/) for related experiments.

## License

[MIT](LICENSE). You may use, modify, and share this project, including commercially,
while keeping the copyright and license notice. Third-party dependencies and any
separately attributed material retain their own terms.
