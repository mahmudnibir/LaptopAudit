import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "report" / "generate_report.py"
spec = importlib.util.spec_from_file_location("generate_report", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ReportTests(unittest.TestCase):
    def test_battery_classification_preserves_missing_data(self):
        self.assertEqual(module.battery_status({}), ("neutral", "Not available"))
        self.assertEqual(module.battery_status({"health_percent": 9}), ("critical", "Replace recommended"))
        self.assertEqual(module.battery_status({"health_percent": 94}), ("good", "Good"))
        self.assertEqual(module.battery_status({"health_percent": 79.9}), ("warning", "Aging"))

    def test_storage_classification_handles_all_states(self):
        self.assertEqual(module.storage_status({"smart_status": True}), ("critical", "SMART failure predicted"))
        self.assertEqual(module.storage_status({"smart_status": False}), ("good", "SMART prediction good"))
        self.assertEqual(module.storage_status({"smart_status": "TRUE"}), ("critical", "SMART failure predicted"))
        self.assertEqual(module.storage_status({}), ("neutral", "SMART not available"))

    def test_render_contains_device_and_unknown_storage(self):
        report = {
            "schema_version": "1.0",
            "generated_at": "2026-09-16T00:00:00Z",
            "device": {"manufacturer": "Test", "model": "Unit", "operating_system": "Windows"},
            "battery": {},
            "memory": {},
            "storage": [],
        }
        output = module.render(report)
        self.assertIn("Test Unit", output)
        self.assertIn("Not available", output)
        self.assertIn("Evidence-based summary", output)

    def test_single_storage_object_is_rendered(self):
        report = {
            "device": {},
            "battery": {},
            "memory": {},
            "storage": {"model": "Test SSD", "capacity_gb": 256},
        }
        self.assertIn("Test SSD", module.render(report))

    def test_render_escapes_untrusted_device_values(self):
        report = {
            "device": {"manufacturer": "<script>alert(1)</script>", "model": "Laptop & Pro"},
            "battery": {},
            "memory": {},
            "storage": [],
        }
        output = module.render(report)
        self.assertNotIn("<script>alert(1)</script>", output)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", output)
        self.assertIn("Laptop &amp; Pro", output)


if __name__ == "__main__":
    unittest.main()
