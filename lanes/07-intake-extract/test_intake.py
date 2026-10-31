import hashlib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from intake import _numeric, inspect_document


class IntakeTests(unittest.TestCase):
    def test_numeric_lexemes_are_display_strings(self):
        self.assertEqual(_numeric("x $1,234.50 and (500) at 12%"), ["$1,234.50", "(500)", "12%"])

    def test_header_and_manifest_fail_closed(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "x.pdf"; p.write_bytes(b"not a pdf")
            out = inspect_document(p, {"id": "X", "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}, lambda _: {})
            self.assertEqual(out["class_label"], "UNRESOLVED")


if __name__ == "__main__": unittest.main()
