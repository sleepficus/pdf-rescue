import unittest

from planner import plan_document


class PlannerTests(unittest.TestCase):
    def test_benign_is_zero_operation(self):
        intake = {"status": "READY", "class_label": "BENIGN", "document_id": "B01", "page_count": 1, "pages": []}
        self.assertEqual(plan_document(intake)["operations"], [])

    def test_supported_has_structure(self):
        intake = {"status": "READY", "class_label": "TEXT_SINGLE_COLUMN", "document_id": "F01", "page_count": 1, "pages": [{"reading_text": "a  b"}]}
        ops = [x["op_type"] for x in plan_document(intake)["operations"]]
        self.assertEqual(ops, ["OP_STRUCTURE_TAGS", "OP_SPACING_NORMALIZE"])


if __name__ == "__main__": unittest.main()
