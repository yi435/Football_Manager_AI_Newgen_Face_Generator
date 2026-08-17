import os
import sys
import json
import ssl
import shutil
import threading
import subprocess
import asyncio
import tkinter as tk
from tkinter import ttk, messagebox

import aiohttp
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    # certifi not installed: fall back to the system CA store. Both verify TLS.
    _SSL_CTX = ssl.create_default_context()

# ---------------------------------------------------------------------------
# Locations & download sources
# ---------------------------------------------------------------------------
APP_NAME = "FM Newgen Generator"
CHECKPOINT_FILENAME = "RealVisXL_V5.0_fp16.safetensors"
CHECKPOINT_URL = (
    "https://huggingface.co/SG161222/RealVisXL_V5.0/resolve/main/"
    "RealVisXL_V5.0_fp16.safetensors"
)
COMFYUI_FILENAME = "ComfyUI_windows_portable_nvidia.7z"
COMFYUI_URL = (
    "https://github.com/Comfy-Org/ComfyUI/releases/latest/download/"
    "ComfyUI_windows_portable_nvidia.7z"
)
COMFYUI_DIR_NAME = "ComfyUI_windows_portable"
# Standalone 7-Zip console binary used to extract the ComfyUI portable
# archive. It is the only reliable way to handle the archive's BCJ2 solid
# compression (which py7zr cannot decode). Downloaded silently to the install
# root the first time it is needed.
SEVENZA_FILENAME = "7za.exe"
SEVENZA_URL = (
    "https://raw.githubusercontent.com/develar/7zip-bin/master/"
    "win/x64/7za.exe"
)
REQUIRED_DISK_GB = 25
MIN_CHECKPOINT_BYTES = 100 * 1024 * 1024


def app_root():
    """
    Returns the folder that should own an EXE-distributed install.
    - Frozen (PyInstaller onefile): folder containing the .exe.
    - Running from source: this project folder.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def install_root():
    """Where the wizard installs ComfyUI + the model. Local app data."""
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    else:
        base = os.path.expanduser("~")
    return os.path.join(base, "FM Newgen Generator")


def comfyui_root():
    return os.path.join(install_root(), COMFYUI_DIR_NAME)


def checkpoint_dest():
    """
    Where the checkpoint must live so ComfyUI's CheckpointLoaderSimple can
    actually load it: inside the embedded engine's models/checkpoints folder.
    """
    return os.path.join(comfyui_root(), "ComfyUI", "models", "checkpoints",
                        CHECKPOINT_FILENAME)


def config_path():
    return os.path.join(app_root(), "config.json")


def setup_marker():
    return os.path.join(install_root(), ".setup_complete")


# ---------------------------------------------------------------------------
# System checks
# ---------------------------------------------------------------------------
def detect_nvidia_gpu():
    """Returns a display string or None if no NVIDIA GPU is found."""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        name = out.stdout.strip()
        if name and "NVIDIA" in name:
            return name
    except Exception:
        pass
    return None


def free_disk_gb(path):
    try:
        return shutil.disk_usage(path).free / (1024 ** 3)
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Downloads (aiohttp, resumable, threaded)
# ---------------------------------------------------------------------------
async def _download_file_async(url, dest, progress_cb=None, cancel_event=None):
    """
    Streams a file from url to dest.
    - Resumes from a partial file using HTTP Range when the server allows it.
    - Calls progress_cb(downloaded_bytes, total_bytes, speed_bps) periodically.
    """
    dest_tmp = dest + ".part"
    start = 0
    if os.path.exists(dest_tmp):
        start = os.path.getsize(dest_tmp)

    headers = {"Range": f"bytes={start}-"} if start else {}
    speed = 0.0

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, headers=headers, timeout=None,
                                        ssl=_SSL_CTX) as resp:
                    if resp.status not in (200, 206):
                        raise RuntimeError(f"HTTP {resp.status} downloading {url}")

                    total = int(resp.headers.get("Content-Length", 0))
                    if resp.status == 200:
                        # Server ignored Range -> restart from scratch
                        total = total + start
                    total = max(total, start)

                    mode = "ab" if start and resp.status == 206 else "wb"
                    with open(dest_tmp, mode) as f:
                        downloaded = start
                        last_update = asyncio.get_event_loop().time()
                        last_bytes = start
                        async for chunk in resp.content.iter_chunked(1024 * 256):
                            if cancel_event and cancel_event.is_set():
                                return False, "cancelled"
                            f.write(chunk)
                            downloaded += len(chunk)
                            now = asyncio.get_event_loop().time()
                            if now - last_update >= 0.5:
                                speed = (downloaded - last_bytes) / (now - last_update)
                                last_update, last_bytes = now, downloaded
                                if progress_cb:
                                    progress_cb(downloaded, total, speed)
                    # Only consider the transfer complete if we hit the target size
                    if os.path.getsize(dest_tmp) >= total - 1:
                        os.replace(dest_tmp, dest)
                        return True, dest
                    # Otherwise the connection closed early -> retry with Range
                    start = os.path.getsize(dest_tmp)
                    headers = {"Range": f"bytes={start}-"}
            except aiohttp.ClientError as e:
                raise RuntimeError(f"Network error: {e}") from e


def download_file(url, dest, progress_cb=None, cancel_event=None):
    """Synchronous wrapper used inside a worker thread."""
    return asyncio.run(_download_file_async(url, dest, progress_cb, cancel_event))


def extract_7z(archive_path, dest_dir):
    """
    Extracts archive_path into dest_dir using the standalone 7-Zip console
    binary (7za.exe). The official ComfyUI portable archive uses BCJ2 solid
    compression, which py7zr cannot decode, so we fetch 7za.exe once and run
    it via subprocess instead of requiring the user to install 7-Zip.
    """
    import urllib.request

    os.makedirs(dest_dir, exist_ok=True)

    sevenza = os.path.join(install_root(), SEVENZA_FILENAME)
    if not os.path.exists(sevenza):
        try:
            urllib.request.urlretrieve(SEVENZA_URL, sevenza)
        except Exception as e:
            raise RuntimeError(
                f"Could not download the 7-Zip extractor (needed to unpack "
                f"ComfyUI). Check your internet connection and retry. "
                f"({type(e).__name__}: {e})")
    if not os.path.exists(sevenza) or os.path.getsize(sevenza) < 512 * 1024:
        raise RuntimeError("7-Zip extractor download failed — it is missing "
                           "or incomplete. Please retry setup.")

    try:
        proc = subprocess.run(
            [sevenza, "x", archive_path, f"-o{dest_dir}", "-y", "-aoa"],
            capture_output=True, text=True)
    except Exception as e:
        raise RuntimeError(f"Failed to run the 7-Zip extractor: {e}")
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        detail = " | ".join(tail[-3:]) if tail else f"exit code {proc.returncode}"
        raise RuntimeError(f"Extracting ComfyUI failed ({detail}). "
                           "Please retry setup.")

    try:
        os.unlink(sevenza)
    except OSError:
        pass


def is_installed():
    """True when ComfyUI + checkpoint already exist on disk."""
    marker = os.path.exists(setup_marker())
    comfy = os.path.isdir(comfyui_root())
    ckpt = os.path.exists(checkpoint_dest())
    return marker and comfy and ckpt


def _comfy_ok():
    """A valid ComfyUI portable install has an embedded Python + nvidia runner."""
    root = comfyui_root()
    if not os.path.isdir(root):
        return False
    has_py = os.path.isdir(os.path.join(root, "python_embeded"))
    has_bat = os.path.isfile(os.path.join(root, "run_nvidia_gpu.bat"))
    return has_py and has_bat


def _checkpoint_ok():
    """The checkpoint must exist and be a plausible size (a truncated file is broken)."""
    p = checkpoint_dest()
    if not os.path.exists(p):
        return False
    try:
        return os.path.getsize(p) >= MIN_CHECKPOINT_BYTES
    except OSError:
        return False


def needs_repair():
    """
    True when a previous install attempt exists (marker written) but one of the
    pieces is missing or corrupt, or a partial download is left behind.
    """
    if not os.path.exists(setup_marker()):
        return False
    return not _comfy_ok() or not _checkpoint_ok() or os.path.exists(
        os.path.join(install_root(), COMFYUI_FILENAME + ".part"))


def uninstall_all():
    """
    Removes the whole local install (ComfyUI + model + marker + partial files)
    and clears the comfyui_install_dir key from config.json.
    Your FM folders and generated faces are never touched.
    """
    root_folder = install_root()
    if os.path.isdir(root_folder):
        shutil.rmtree(root_folder, ignore_errors=True)
    cfg_path = config_path()
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "comfyui_install_dir" in data:
                del data["comfyui_install_dir"]
                with open(cfg_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
        except Exception:
            pass


def setup_wizard_needed():
    """
    True when this is a fresh distribution build with no embedded install:
    no config.json, or a config that does not point at an embedded ComfyUI.
    """
    if is_installed():
        return False
    cfg = config_path()
    if os.path.exists(cfg):
        try:
            with open(cfg, "r", encoding="utf-8") as f:
                data = json.load(f)
            install_dir = data.get("comfyui_install_dir", "")
            if install_dir and os.path.isdir(install_dir):
                return False
        except Exception:
            pass
    # A source-tree checkout (dev) has ./graphics and ./exports next to it —
    # treat that as already set up rather than forcing the big download.
    if os.path.isdir(os.path.join(app_root(), "src")):
        return False
    return True


# ---------------------------------------------------------------------------
# Tkinter wizard UI
# ---------------------------------------------------------------------------
class SetupWizard:
    def __init__(self, root, on_finish=None, repair=False):
        self.root = root
        self.on_finish = on_finish
        self.repair = repair
        self.cancel_event = threading.Event()

        # Theme (matches src/ui.py)
        self.bg_dark = "#121214"
        self.bg_panel = "#1a1a1e"
        self.bg_input = "#26262b"
        self.fg_light = "#f1f1f5"
        self.fg_muted = "#a5a5b5"
        self.color_accent = "#6c5ce7"
        self.color_success = "#00b894"
        self.color_error = "#d63031"
        self.color_warning = "#fdcb6e"

        self.root.title(f"{APP_NAME} — Setup")
        self.root.geometry("640x520")
        self.root.configure(bg=self.bg_dark)
        self._build_ui()

    def _build_ui(self):
        # Header
        mode_title = "Repair Setup" if self.repair else "First-Run Setup"
        tk.Label(self.root, text=f"{APP_NAME} — {mode_title}",
                 font=("Segoe UI", 16, "bold"), fg=self.fg_light,
                 bg=self.bg_dark).pack(anchor="w", padx=24, pady=(20, 2))
        intro = (
            "This will check your local AI (ComfyUI + realism model) and download "
            "only the pieces that are missing or damaged, so faces are generated "
            "on your own GPU — free, unlimited and offline."
            if self.repair else
            "This will install local AI (ComfyUI + a realism model) so faces "
            "are generated on your own GPU — free, unlimited and offline."
        )
        self.status_lbl = tk.Label(
            self.root,
            text=intro,
            font=("Segoe UI", 9), fg=self.fg_muted, bg=self.bg_dark,
            wraplength=580, justify="left")
        self.status_lbl.pack(anchor="w", padx=24, pady=(0, 16))

        # Body (stack of labels)
        self.body = tk.Frame(self.root, bg=self.bg_panel)
        self.body.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        self.line1 = self._body_label("1. Checking your system…")
        self.line2 = self._body_label("2. Downloading ComfyUI (AI engine, ~2 GB)")
        self.line3 = self._body_label("3. Downloading the realism model (~7 GB)")
        self.line4 = self._body_label("4. Linking everything together…")
        self.detail_lbl = tk.Label(self.body, text="",
                                   font=("Consolas", 8), fg=self.fg_muted,
                                   bg=self.bg_panel, anchor="w", justify="left",
                                   wraplength=580)
        self.detail_lbl.pack(fill="x", padx=16, pady=(8, 0))

        # Progress bar
        self.progress = ttk.Progressbar(self.root, maximum=1.0, length=580,
                                        mode="determinate")
        self.progress.pack(padx=24, pady=(0, 12))
        self.progress_lbl = tk.Label(self.root, text="Idle",
                                     font=("Segoe UI", 8), fg=self.fg_muted,
                                     bg=self.bg_dark)
        self.progress_lbl.pack(anchor="w", padx=24)

        # Buttons
        btn_frame = tk.Frame(self.root, bg=self.bg_dark)
        btn_frame.pack(fill="x", padx=24, pady=16)
        self.cancel_btn = tk.Button(btn_frame, text="Cancel", bg=self.bg_input,
                                    fg=self.fg_light, bd=0, padx=14, pady=4,
                                    command=self._on_cancel)
        self.cancel_btn.pack(side="left")
        self.uninstall_btn = None
        if self.repair:
            self.uninstall_btn = tk.Button(btn_frame, text="Uninstall", bg="#d63031",
                                           fg=self.fg_light, bd=0, padx=14, pady=4,
                                           command=self._on_uninstall)
            self.uninstall_btn.pack(side="left", padx=(8, 0))
        self.next_btn = tk.Button(btn_frame, text="Install Now", bg=self.color_accent,
                                  fg=self.fg_light, bd=0, padx=18, pady=4,
                                  activebackground="#5848c2", command=self._start)
        self.next_btn.pack(side="right")

    def _body_label(self, text):
        lbl = tk.Label(self.body, text=text, font=("Segoe UI", 10, "bold"),
                       fg=self.fg_muted, bg=self.bg_panel, anchor="w")
        lbl.pack(fill="x", padx=16, pady=3)
        return lbl

    # -- UI helpers ---------------------------------------------------------
    def _set_line(self, line, text, color=None):
        line.config(text=text, fg=color or self.fg_light)

    def _log(self, msg):
        self.detail_lbl.config(text=msg[:160])

    def _set_progress(self, fraction, label=""):
        self.progress["value"] = min(1.0, max(0.0, fraction))
        if label:
            self.progress_lbl.config(text=label)
        self.root.update_idletasks()

    def _disable_actions(self):
        self.next_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")

    def _on_cancel(self):
        self.cancel_event.set()
        self.status_lbl.config(text="Cancelling… please wait.",
                               fg=self.color_warning)

    def _on_uninstall(self):
        if not messagebox.askyesno(
                "Uninstall",
                "Remove the local AI engine + model (~9 GB)?\n"
                "Your FM folders and generated faces are NOT touched."):
            return
        if self.next_btn:
            self.next_btn.config(state="disabled")
        if self.uninstall_btn:
            self.uninstall_btn.config(state="disabled")
        self.status_lbl.config(text="Uninstalling…", fg=self.color_warning)
        threading.Thread(target=self._do_uninstall, daemon=True).start()

    def _do_uninstall(self):
        try:
            uninstall_all()
        except Exception as e:
            msg = f"Uninstall error: {e}"
            self.root.after(0, lambda m=msg: self._fail(m))
            return
        self.root.after(0, self._uninstall_done)

    def _uninstall_done(self):
        self.status_lbl.config(
            text="Uninstalled. The next launch will re-run setup.",
            fg=self.color_success)
        if self.uninstall_btn:
            self.uninstall_btn.pack_forget()
        self.next_btn.config(state="normal", text="Close")
        self.next_btn.config(command=self._launch)
        self.cancel_btn.config(state="disabled", text="")

    def _fail(self, msg):
        self.status_lbl.config(
            text=f"Setup failed. {msg}\nYou can retry; downloads resume from "
                 "where they left off.", fg=self.color_error)
        self.next_btn.config(state="normal", text="Retry")
        self.cancel_btn.config(state="disabled")

    def _start(self):
        self.cancel_event.clear()
        self.next_btn.config(state="disabled", text="Working…")
        self.cancel_btn.config(state="normal")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        """Runs the whole workflow off the UI thread."""
        title_color = self.color_success
        try:
            # Create the install folder first so the disk space check can
            # measure the real target volume (otherwise it reports 0.0 GB).
            os.makedirs(install_root(), exist_ok=True)

            # 1. System checks
            self.root.after(0, lambda: self._set_line(
                self.line1, "1. Checking your system…", self.color_accent))
            gpu = detect_nvidia_gpu()
            free = free_disk_gb(install_root())
            if free < REQUIRED_DISK_GB:
                raise RuntimeError(
                    f"Only {free:.1f} GB free disk space — need at least "
                    f"{REQUIRED_DISK_GB} GB.")
            if not gpu:
                self._log("No NVIDIA GPU detected — generation will fall back "
                          "to CPU (slow). You can still continue.")
            else:
                self._log(f"GPU found: {gpu}"[:160])
            self.root.after(0, lambda: self._set_line(
                self.line1, "1. System check passed — ready to install",
                self.color_success))

            # 2. ComfyUI portable
            self.root.after(0, lambda: self._set_line(
                self.line2, "2. Downloading ComfyUI (AI engine, ~2 GB)",
                self.color_accent))
            if not _comfy_ok():
                if os.path.isdir(comfyui_root()):
                    self._log("Existing ComfyUI folder is incomplete — "
                              "removing it and re-installing.")
                    shutil.rmtree(comfyui_root(), ignore_errors=True)
                archive = os.path.join(install_root(), COMFYUI_FILENAME)
                ok, dest = download_file(
                    COMFYUI_URL, archive,
                    progress_cb=self._comfy_progress,
                    cancel_event=self.cancel_event)
                if not ok:
                    self.status_lbl.config(text="Setup cancelled.", fg=self.color_warning)
                    return
                self._set_progress(0, "Extracting ComfyUI…")
                self._log("Extracting (this can take a few minutes)…")
                extract_7z(archive, install_root())
                os.unlink(archive)
            self.root.after(0, lambda: self._set_line(
                self.line2, "2. ComfyUI installed ✓", self.color_success))

            # 3. Checkpoint
            self.root.after(0, lambda: self._set_line(
                self.line3, "3. Downloading the realism model (~7 GB)",
                self.color_accent))
            if not _checkpoint_ok():
                if os.path.exists(checkpoint_dest()):
                    self._log("Existing model file is truncated — re-downloading.")
                    os.unlink(checkpoint_dest())
                # Older builds placed the model next to the install root; if we
                # find a good file there, move it into ComfyUI's models folder
                # instead of forcing a ~7 GB re-download.
                old_dest = os.path.join(install_root(), CHECKPOINT_FILENAME)
                if os.path.exists(old_dest):
                    try:
                        if os.path.getsize(old_dest) >= MIN_CHECKPOINT_BYTES:
                            os.makedirs(os.path.dirname(checkpoint_dest()),
                                        exist_ok=True)
                            os.replace(old_dest, checkpoint_dest())
                            self._log("Moved existing model into ComfyUI's "
                                      "checkpoints folder.")
                        else:
                            os.unlink(old_dest)
                    except OSError as e:
                        self._log(f"Could not move old model file ({e}).")
                if not _checkpoint_ok():
                    ok, dest = download_file(
                        CHECKPOINT_URL, checkpoint_dest(),
                        progress_cb=self._model_progress,
                        cancel_event=self.cancel_event)
                    if not ok:
                        self.status_lbl.config(text="Setup cancelled.", fg=self.color_warning)
                        return
            self.root.after(0, lambda: self._set_line(
                self.line3, "3. Realism model installed ✓", self.color_success))

            # 4. Write config.json
            self.root.after(0, lambda: self._set_line(
                self.line4, "4. Linking everything together…", self.color_accent))
            self._write_config()
            self._drop_marker()
            self.root.after(0, lambda: self._set_line(
                self.line4, "4. Setup complete ✓", self.color_success))
            self._set_progress(1.0, "Done")

            self.root.after(0, self._finish)
        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            self.root.after(0, lambda m=msg: self._fail(m))

    # -- step callbacks -----------------------------------------------------
    def _comfy_progress(self, downloaded, total, speed):
        frac = downloaded / total if total else 0
        self.root.after(0, lambda: self._show_download(
            "2. Downloading ComfyUI (AI engine, ~2 GB)", frac,
            downloaded, total, speed))

    def _model_progress(self, downloaded, total, speed):
        frac = downloaded / total if total else 0
        self.root.after(0, lambda: self._show_download(
            "3. Downloading the realism model (~7 GB)", frac,
            downloaded, total, speed))

    def _show_download(self, line_text, frac, downloaded, total, speed):
        mb = lambda v: v / (1024 ** 2)
        speed_mb = speed / (1024 ** 2) if speed else 0
        if total:
            self._set_progress(
                frac,
                f"{mb(downloaded):.1f} / {mb(total):.1f} MB   "
                f"({speed_mb:.1f} MB/s)")
        else:
            self._set_progress(0, f"{mb(downloaded):.1f} MB "
                                  f"({speed_mb:.1f} MB/s)")
        self._log(f"{line_text}\n{mb(downloaded):.0f} MB of ~{mb(total):.0f} MB")

    # -- finalize -----------------------------------------------------------
    def _drop_marker(self):
        with open(setup_marker(), "w", encoding="utf-8") as f:
            f.write("complete")

    def _write_config(self):
        db = os.path.expanduser("~")
        if sys.platform.startswith("win"):
            fm_graphics = os.path.join(
                db, "Documents", "Sports Interactive",
                "Football Manager 2024", "graphics", "AI Newgen Faces")
            exports = os.path.join(db, "Documents", "FM Newgen", "exports")
        else:
            fm_graphics = os.path.join(db, "FM Newgen", "graphics",
                                       "AI Newgen Faces")
            exports = os.path.join(db, "FM Newgen", "exports")

        cfg = {
            "watch_directory": exports,
            "graphics_directory": fm_graphics,
            "face_style": "professional sports media day headshot portrait of a [AGE]-year-old male [NATIONALITY] football player, [PERSONALITY], clean blank unbranded solid-color v-neck athletic shirt, direct frontal view, head and shoulders, looking directly into camera, neutral expression, isolated on a plain solid white studio background, high-key studio lighting, shot on 85mm portrait lens, f/4, sharp focus on eyes, highly detailed, photorealistic, realistic skin texture, visible pores, real life photo",
            "concurrency_limit": 1,
            "auto_reload_skin_hotkey": False,
            "provider": "comfyui",
            "comfyui_base_url": "http://127.0.0.1:8188",
            "comfyui_model": CHECKPOINT_FILENAME,
            "comfyui_negative_prompt": "wrinkles, full body, crossed arms, hands, legs, lower body, background scenery, grass, soccer field, training pitch, trees, crowd, text, brand logos, badges, graphics, distorted logos, deformed crests, deformed apparel, waxy skin, CGI, 3D render, cartoon, illustration, drawing, digital art, makeup, smooth skin, airbrushed, blurred eyes, double chin, out of focus",
            "comfyui_steps": 25,
            "comfyui_cfg": 6.0,
            "comfyui_sampler": "euler",
            "comfyui_scheduler": "karras",
            "comfyui_width": 896,
            "comfyui_height": 1152,
            "comfyui_install_dir": comfyui_root(),
            "uid_prefix": "2",
        }
        with open(config_path(), "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)

    def _finish(self):
        self.status_lbl.config(
            text="Setup complete. Launching ComfyUI and the generator…",
            fg=self.color_success)
        self.next_btn.config(state="normal", text="Launch")
        self.next_btn.config(command=self._launch)
        self.cancel_btn.config(state="disabled")

    def _launch(self):
        if self.on_finish:
            self.on_finish()
        else:
            self.root.destroy()

    @staticmethod
    def startup_command():
        """Returns the command that launches embedded ComfyUI (or None)."""
        launcher = os.path.join(comfyui_root(), "run_nvidia_gpu.bat")
        if os.path.exists(launcher):
            return launcher
        return os.path.join(comfyui_root(), "run_cpu.bat")


def run(on_finish=None):
    """Entry point: shows the wizard; calls on_finish() when setup completes."""
    root = tk.Tk()
    SetupWizard(root, on_finish=_wrap_finish(on_finish))
    root.mainloop()


def _wrap_finish(on_finish):
    def _done():
        root = tk._default_root
        if root is not None:
            root.destroy()
        if on_finish:
            on_finish()
    return _done


if __name__ == "__main__":
    run()