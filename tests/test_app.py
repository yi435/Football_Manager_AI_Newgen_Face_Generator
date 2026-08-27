import os
import json
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.app import atomic_json_dump, FMGeneratorApp


class AppTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_atomic_json_dump_creates_valid_file(self):
        target_path = os.path.join(self.tmp_dir, "test_config.json")
        data = {"watch_directory": "./exports", "concurrency_limit": 1}
        atomic_json_dump(data, target_path)

        self.assertTrue(os.path.isfile(target_path))
        with open(target_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        self.assertEqual(loaded, data)

    def test_atomic_json_dump_overwrites_cleanly(self):
        target_path = os.path.join(self.tmp_dir, "metadata.json")
        data_v1 = {"2000000001": 16}
        data_v2 = {"2000000001": 20, "2000000002": 16}

        atomic_json_dump(data_v1, target_path)
        atomic_json_dump(data_v2, target_path)

        with open(target_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        self.assertEqual(loaded, data_v2)

    def test_get_active_milestone_boundaries(self):
        # We can test the milestone classification logic on an instance or mock
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        app = FMGeneratorApp(root)

        self.assertEqual(app.get_active_milestone("16"), 16)
        self.assertEqual(app.get_active_milestone("19"), 16)
        self.assertEqual(app.get_active_milestone("20"), 20)
        self.assertEqual(app.get_active_milestone("23"), 20)
        self.assertEqual(app.get_active_milestone("24"), 24)
        self.assertEqual(app.get_active_milestone("27"), 24)
        self.assertEqual(app.get_active_milestone("28"), 28)
        self.assertEqual(app.get_active_milestone("34"), 28)
        # Invalid / non-digit string fallback to 16
        self.assertEqual(app.get_active_milestone("invalid_age"), 16)
        self.assertEqual(app.get_active_milestone(None), 16)

        root.destroy()

    def test_translate_error_friendly_messages(self):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        app = FMGeneratorApp(root)

        msg_429 = app.translate_error("HTTP 429 Too Many Requests")
        self.assertIn("Rate Limited", msg_429)

        msg_comfy = app.translate_error("ComfyUI not running")
        self.assertIn("Start ComfyUI", msg_comfy)

        msg_conn = app.translate_error("ClientConnectorError")
        self.assertIn("Connection Failed", msg_conn)

        root.destroy()


if __name__ == "__main__":
    unittest.main()
