import unittest
import tkinter as tk
from src.ui import FMGeneratorUI


class UITest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.started_paths = []
        self.stopped = False
        self.saved_configs = []
        self.run_now_paths = []

        self.ui = FMGeneratorUI(
            root=self.root,
            start_callback=lambda w, g: self.started_paths.append((w, g)),
            stop_callback=lambda: setattr(self, "stopped", True),
            save_config_callback=lambda *a, **kw: self.saved_configs.append((a, kw)),
            run_now_callback=lambda w, g: self.run_now_paths.append((w, g))
        )

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_ui_initialization_defaults(self):
        self.assertEqual(self.ui.watch_path_var.get(), "./exports")
        self.assertEqual(self.ui.graphics_path_var.get(), "./graphics/AI Newgen Faces")
        self.assertEqual(self.ui.sampler_var.get(), "euler_a")
        self.assertEqual(self.ui.concurrency_var.get(), 1)
        self.assertFalse(self.ui.watcher_running)

    def test_ui_stat_and_progress_updates(self):
        self.ui.update_stats(45, 3)
        self.root.update()
        self.assertEqual(self.ui.stat_box_mapped.cget("text"), "45")
        self.assertEqual(self.ui.stat_box_queued.cget("text"), "3")

        self.ui.update_progress(5, 10, "Downloading faces (5/10)...")
        self.root.update()
        self.assertEqual(self.ui.progress_bar.cget("value"), 50.0)

    def test_ui_log_syntax_highlighting(self):
        self.ui.log("[Success] Face generated for UID 2000000001")
        self.ui.log("[Warning] Directory missing")
        self.ui.log("[Error] Provider unreachable")
        self.root.update()
        console_text = self.ui.console.get("1.0", "end-1c")
        self.assertIn("Face generated for UID 2000000001", console_text)
        self.assertIn("Provider unreachable", console_text)

    def test_ui_watcher_toggle(self):
        self.ui._toggle_watcher()
        self.assertTrue(self.ui.watcher_running)
        self.assertEqual(len(self.started_paths), 1)

        self.ui._toggle_watcher()
        self.assertFalse(self.ui.watcher_running)
        self.assertTrue(self.stopped)

    def test_ui_set_generating_state(self):
        self.ui.set_generating(True)
        self.root.update()
        self.assertEqual(self.ui.btn_cancel.cget("state"), "normal")

        self.ui.set_generating(False)
        self.root.update()
        self.assertEqual(self.ui.btn_cancel.cget("state"), "disabled")

    def test_design_tokens_loading(self):
        from src.design import DesignTokens
        tokens = DesignTokens.load()
        self.assertEqual(tokens.colors.primary, "#6c5ce7")
        self.assertEqual(tokens.colors.background, "#121214")
        self.assertEqual(tokens.interface_type, "desktop-app")
        self.assertEqual(tokens.spacing.unit, 4)
        self.assertEqual(self.ui.bg_dark, "#121214")
        self.assertEqual(self.ui.color_accent, "#6c5ce7")


if __name__ == "__main__":
    unittest.main()
