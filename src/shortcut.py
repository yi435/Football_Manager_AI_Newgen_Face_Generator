"""
Desktop shortcut creation utility for Windows and Linux.
"""
import os
import sys
import subprocess


def get_desktop_path():
    """Returns the user's Desktop directory, including OneDrive redirection."""
    home = os.path.expanduser("~")
    desktop = os.path.join(home, "Desktop")
    if os.path.isdir(desktop):
        return desktop
    onedrive_desktop = os.path.join(home, "OneDrive", "Desktop")
    if os.path.isdir(onedrive_desktop):
        return onedrive_desktop
    return home


def create_desktop_shortcut(app_title="FM AI Newgen Generator"):
    """
    Creates a desktop shortcut pointing to the application executable or launcher.
    Returns (success: bool, message: str).
    """
    desktop = get_desktop_path()

    if getattr(sys, "frozen", False):
        target_exe = os.path.abspath(sys.executable)
        work_dir = os.path.dirname(target_exe)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        target_exe = sys.executable
        work_dir = base_dir

    if sys.platform.startswith("win"):
        shortcut_path = os.path.join(desktop, f"{app_title}.lnk")
        if getattr(sys, "frozen", False):
            ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{shortcut_path}')
$s.TargetPath = '{target_exe}'
$s.WorkingDirectory = '{work_dir}'
$s.Description = '{app_title}'
$s.Save()
"""
        else:
            main_py = os.path.join(work_dir, "main.py")
            ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{shortcut_path}')
$s.TargetPath = '{sys.executable}'
$s.Arguments = '"{main_py}"'
$s.WorkingDirectory = '{work_dir}'
$s.Description = '{app_title}'
$s.Save()
"""
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True, text=True, timeout=10
            )
            if res.returncode == 0 and os.path.exists(shortcut_path):
                return True, f"Desktop shortcut created at:\n{shortcut_path}"
            return False, f"Could not create shortcut: {res.stderr or res.stdout}"
        except Exception as e:
            return False, f"Failed to create Windows shortcut: {e}"

    elif sys.platform.startswith("linux"):
        desktop_file = os.path.join(desktop, "fm-newgen-generator.desktop")
        main_py = os.path.join(work_dir, "main.py")
        content = f"""[Desktop Entry]
Type=Application
Name={app_title}
Exec={sys.executable} "{main_py}"
Path={work_dir}
Terminal=false
Categories=Game;Utility;
"""
        try:
            with open(desktop_file, "w", encoding="utf-8") as f:
                f.write(content)
            os.chmod(desktop_file, 0o755)
            return True, f"Desktop shortcut created at:\n{desktop_file}"
        except Exception as e:
            return False, f"Failed to create Linux desktop shortcut: {e}"

    return False, "Unsupported platform for desktop shortcut creation."
