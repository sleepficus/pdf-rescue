import unittest
from disposition import derive_disposition

class DispositionTests(unittest.TestCase):
    def test_not_exercised_never_passes(self):
        gates = {f"G{i}": {"status":"PASS"} for i in range(1,11)}
        gates["G5"] = {"status":"NOT_EXERCISED"}
        self.assertEqual(derive_disposition("TEXT_SINGLE_COLUMN", gates, {"outcome":"RECONCILED"})["rule"], "PR-08")
    def test_divergent_hidden_text_refuses(self):
        gates = {"G1":{"status":"PASS"},"G4":{"status":"FAIL"}}
        out = derive_disposition("TEXT_SINGLE_COLUMN", gates, {"outcome":"HIDDEN_TEXT_ANOMALY","anomaly_kind":"DIVERGENT"})
        self.assertEqual(out, {"disposition":"REFUSE","rule":"PR-06"})

if __name__ == "__main__": unittest.main()
