"""
Unified entry point for the FM AI Newgen Generator.

- `python main.py`              -> runs the app; on a fresh distribution build it
                                   runs the first-run Setup Wizard first.
- `python main.py --repair`     -> force the Setup Wizard in repair mode (re-checks
                                   and re-downloads any missing/corrupt pieces).
- `python main.py --uninstall`  -> confirm + remove the local AI engine/model.
"""
import sys
import tkinter as tk


def _launch_app():
    from src.app import FMGeneratorApp
    root = tk.Tk()
    FMGeneratorApp(root)
    root.mainloop()


def _confirm_and_uninstall():
    from tkinter import messagebox
    from src.setup_wizard import uninstall_all
    root = tk.Tk()
    root.withdraw()
    if messagebox.askyesno(
            "Uninstall",
            "Remove the local AI engine + model (~9 GB)?\n"
            "Your FM folders and generated faces are NOT touched."):
        uninstall_all()
        messagebox.showinfo("Uninstall", "Local AI engine removed.")
    root.destroy()


def _run_wizard(repair=False):
    from src.setup_wizard import SetupWizard
    root = tk.Tk()

    def _after_wizard():
        root.destroy()
        _launch_app()

    SetupWizard(root, on_finish=_after_wizard, repair=repair)
    root.mainloop()


def main():
    from src.setup_wizard import setup_wizard_needed, needs_repair

    if "--uninstall" in sys.argv:
        _confirm_and_uninstall()
        return

    if "--repair" in sys.argv or needs_repair():
        _run_wizard(repair=True)
        return

    if not setup_wizard_needed():
        _launch_app()
        return

    # First run -> show the wizard; the wizard launches the app on finish.
    _run_wizard(repair=False)


if __name__ == "__main__":
    main()