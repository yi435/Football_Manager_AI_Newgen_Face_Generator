import os
import sys
import json
import tkinter as tk
import asyncio
import threading
import time
from src.ui import FMGeneratorUI
from src.watcher import ExportWatcher
from src.parser import PlayerParser
from src.generator import FaceGenerator
from src.xml_manager import XMLManager

# Default configuration template
DEFAULT_CONFIG = {
    "watch_directory": "./exports",
    "graphics_directory": "./graphics/AI Newgen Faces",
    "face_style": "professional sports media day headshot portrait of a [AGE]-year-old male [NATIONALITY] football player, [PERSONALITY], clean blank unbranded solid-color v-neck athletic shirt, direct frontal view, head and shoulders, looking directly into camera, neutral expression, isolated on a plain solid white studio background, high-key studio lighting, shot on 85mm portrait lens, f/4, sharp focus on eyes, highly detailed, photorealistic, realistic skin texture, visible pores, real life photo",
    "concurrency_limit": 5,
    "auto_reload_skin_hotkey": False,
    "provider": "comfyui",
    "comfyui_base_url": "http://127.0.0.1:8188",
    "comfyui_model": "",
    "comfyui_negative_prompt": "wrinkles, full body, crossed arms, hands, legs, lower body, background scenery, grass, soccer field, training pitch, trees, crowd, text, brand logos, badges, graphics, distorted logos, deformed crests, deformed apparel, waxy skin, CGI, 3D render, cartoon, illustration, drawing, digital art, makeup, smooth skin, airbrushed, blurred eyes, double chin, out of focus",
    "comfyui_steps": 25,
    "comfyui_cfg": 6.0,
    "comfyui_sampler": "euler",
    "comfyui_scheduler": "karras",
    "comfyui_width": 896,
    "comfyui_height": 1152,
    "show_advanced_settings": False
}


def app_root():
    """
    Returns the folder that owns app state (config.json).
    - Frozen (PyInstaller): folder containing the .exe.
    - Running from source: this project folder.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FMGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.config_path = os.path.join(app_root(), "config.json")
        self.config = self._load_config()
        
        # Instantiate UI
        self.ui = FMGeneratorUI(
            root=root,
            start_callback=self.start_watcher,
            stop_callback=self.stop_watcher,
            save_config_callback=self.save_config,
            run_now_callback=self.run_now,
            check_provider_callback=self.check_provider,
            maintenance_callback=self.open_maintenance,
            face_style_callback=self.open_face_style
        )
        
        # Load configuration into UI
        self.ui.load_config(
            self.config["watch_directory"],
            self.config["graphics_directory"],
            self.config["auto_reload_skin_hotkey"],
            self.config.get("provider", "comfyui"),
            self.config.get("comfyui_base_url", "http://127.0.0.1:8188"),
            self.config.get("comfyui_steps", 25),
            self.config.get("comfyui_cfg", 6.0),
            self.config.get("comfyui_sampler", "euler"),
            self.config.get("comfyui_scheduler", "karras"),
            self.config.get("comfyui_width", 896),
            self.config.get("comfyui_height", 1152),
            self.config.get("concurrency_limit", 1),
            self.config.get("show_advanced_settings", False)
        )
        
        self.watcher = None
        self.processing_lock = threading.Lock()
        self.auto_start_comfyui()

    def auto_start_comfyui(self):
        """
        When the setup wizard installed an embedded ComfyUI (config key
        comfyui_install_dir), launch it silently on startup so the user never
        has to start a server manually. Skips if the server is already up.
        """
        import subprocess
        if not sys.platform.startswith("win"):
            return
        install_dir = self.config.get("comfyui_install_dir", "")
        if not install_dir or not os.path.isdir(install_dir):
            return
        try:
            import aiohttp
            base = self.config.get("comfyui_base_url", "http://127.0.0.1:8188")
            async def _ping():
                async with aiohttp.ClientSession() as s:
                    try:
                        async with s.get(f"{base}/system_stats", timeout=3,
                                         ssl=False) as r:
                            return r.status == 200
                    except Exception:
                        return False
            if not asyncio.run(_ping()):
                launcher = os.path.join(install_dir, "run_nvidia_gpu.bat")
                if not os.path.exists(launcher):
                    launcher = os.path.join(install_dir, "run_cpu.bat")
                if not os.path.exists(launcher):
                    print("[Warning] ComfyUI launcher not found — will not start.")
                else:
                    # Run the .bat hidden (no console window flashes up) and
                    # detached, so it keeps running on its own. Explicitly
                    # invoke cmd /c so the batch path is never parsed as a
                    # shell command line (no injection via a tampered config).
                    subprocess.Popen(["cmd", "/c", launcher], cwd=install_dir,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                    print(f"[Info] Auto-started embedded ComfyUI from {launcher}")
        except Exception as e:
            print(f"[Warning] Could not auto-start ComfyUI: {e}")

        # Background: wait until the server answers (it can take a couple of
        # minutes to boot on first launch) and reflect it in the UI status.
        base = self.config.get("comfyui_base_url", "http://127.0.0.1:8188")
        def _monitor_ready():
            from src.generator import wait_for_comfyui
            if asyncio.run(wait_for_comfyui(base, timeout=180)):
                self.ui.set_provider_status("Connected", "#00b894")
                self.ui.log("[Info] ComfyUI is ready — you can generate now.")
            else:
                self.ui.set_provider_status("Offline", "#d63031")
                self.ui.log("[Warning] ComfyUI did not come up — click "
                            "'Test Connection' or run Maintenance to repair.")
        threading.Thread(target=_monitor_ready, daemon=True).start()

    def _load_config(self):
        data = None
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading config: {e}. Loading defaults.")
        if data is None:
            data = {}
            # Create default config.json on first launch (next to the exe/app)
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_CONFIG, f, indent=2)
            except Exception as e:
                print(f"Error initializing config.json: {e}")
        # Merge keys to ensure compatibility
        for k, v in DEFAULT_CONFIG.items():
            if k not in data:
                data[k] = v
        # Resolve relative directory paths against the app folder so a frozen
        # EXE never depends on the working directory it was launched from.
        for key in ("watch_directory", "graphics_directory"):
            val = data.get(key, "")
            if val and not os.path.isabs(val):
                data[key] = os.path.normpath(os.path.join(app_root(), val))
        return data

    def save_config(self, watch_dir, graphics_dir, auto_reload, provider=None,
                    comfyui_base_url=None, tuning=None):
        self.config["watch_directory"] = watch_dir
        self.config["graphics_directory"] = graphics_dir
        self.config["auto_reload_skin_hotkey"] = auto_reload
        if provider:
            self.config["provider"] = provider
        if comfyui_base_url:
            self.config["comfyui_base_url"] = comfyui_base_url
        if tuning:
            for k, v in tuning.items():
                if v is not None:
                    self.config[k] = v
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.ui.log(f"[Error] Failed to save config.json: {e}")

    def open_face_style(self, mode, positive=None, negative=None):
        """
        Backing callback for the "Edit Face Style…" dialog.
        - mode "get":  returns (positive, negative, default_positive, default_negative)
        - mode "save": persists both prompts to config.json
        """
        if mode == "get":
            return (
                self.config.get("face_style", DEFAULT_CONFIG["face_style"]),
                self.config.get("comfyui_negative_prompt",
                                DEFAULT_CONFIG["comfyui_negative_prompt"]),
                DEFAULT_CONFIG["face_style"],
                DEFAULT_CONFIG["comfyui_negative_prompt"],
            )
        if mode == "save":
            self.config["face_style"] = positive
            self.config["comfyui_negative_prompt"] = negative
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=2)
                self.ui.log("[Info] Face style saved — new faces will use it.")
            except Exception as e:
                self.ui.log(f"[Error] Failed to save face style: {e}")
        return None

    def check_provider(self):
        """
        Pings the selected provider from a background thread and logs the result.
        """
        try:
            generator = FaceGenerator(
                self.config.get("graphics_directory", "./graphics/AI Newgen Faces"),
                concurrency_limit=1,
                provider=self.config.get("provider", "comfyui"),
                comfyui_base_url=self.config.get("comfyui_base_url", "http://127.0.0.1:8188")
            )
            ok, msg = asyncio.run(generator.check_connection())
            prefix = "[Success]" if ok else "[Error]"
            self.ui.log(f"{prefix} {generator.provider_name} connection: {msg}")
            return ok
        except Exception as e:
            self.ui.log(f"[Error] Provider check failed: {e}")
            return False

    def open_maintenance(self):
        """UI entry for repairing or uninstalling the embedded AI engine."""
        from tkinter import messagebox
        from src.setup_wizard import SetupWizard, is_installed

        win = tk.Toplevel(self.root)
        win.title("Installation Maintenance")
        win.configure(bg="#1a1a1e")
        win.resizable(0, 0)
        tk.Label(win, text="AI Engine Installation", font=("Segoe UI", 11, "bold"),
                 fg="#f1f1f5", bg="#1a1a1e").pack(anchor="w", padx=20, pady=(16, 4))
        status = "Installed" if is_installed() else "Not installed / incomplete"
        tk.Label(win, text=f"Status: {status}", font=("Segoe UI", 9),
                 fg="#a5a5b5", bg="#1a1a1e").pack(anchor="w", padx=20, pady=(0, 12))

        def do_repair():
            win.destroy()
            repair_win = tk.Toplevel(self.root)

            def _done():
                repair_win.destroy()
                self.ui.log("[Info] Maintenance finished.")
                self.auto_start_comfyui()

            SetupWizard(repair_win, on_finish=_done, repair=True)

        def do_uninstall():
            win.destroy()
            if not messagebox.askyesno(
                    "Uninstall",
                    "Remove the local AI engine + model (~9 GB)?\n"
                    "Your FM folders and generated faces are NOT touched."):
                return
            self.ui.log("[Info] Uninstalling local AI engine…")
            threading.Thread(target=self._run_uninstall, daemon=True).start()

        for text, cmd, color in (("Repair Install", do_repair, "#6c5ce7"),
                                 ("Uninstall", do_uninstall, "#d63031")):
            tk.Button(win, text=text, bg=color, fg="#f1f1f5", bd=0, padx=16, pady=6,
                      activebackground="#5848c2", command=cmd).pack(fill="x", padx=20, pady=4)
        tk.Button(win, text="Close", bg="#26262b", fg="#f1f1f5", bd=0, padx=16, pady=6,
                  command=win.destroy).pack(fill="x", padx=20, pady=(4, 16))

    def _run_uninstall(self):
        from src.setup_wizard import uninstall_all
        try:
            uninstall_all()
        except Exception as e:
            self.ui.log(f"[Error] Uninstall failed: {e}")
            return
        self.config.pop("comfyui_install_dir", None)
        self.ui.log("[Success] Local AI engine removed. Restart the app to reinstall.")

    def start_watcher(self, watch_dir, graphics_dir):
        try:
            self.watcher = ExportWatcher(watch_dir, self.on_export_detected)
            self.watcher.start()
            return True
        except Exception as e:
            self.ui.log(f"[Error] Failed to start watcher: {e}")
            return False

    def stop_watcher(self):
        if self.watcher:
            self.watcher.stop()
            self.watcher = None

    def run_now(self, watch_dir, graphics_dir):
        """
        Manually scans for any existing files in watch_dir and processes them.
        """
        if not os.path.exists(watch_dir):
            self.ui.log(f"[Warning] Watch directory '{watch_dir}' does not exist.")
            return 0

        files = [os.path.join(watch_dir, f) for f in os.listdir(watch_dir) 
                 if f.lower().endswith(('.rtf', '.html', '.htm', '.txt'))]
        
        if not files:
            self.ui.log("[Info] No export files found to process.")
            return 0

        processed_count = 0
        for filepath in sorted(files):
            self.ui.log(f"[Info] Manually processing file: {os.path.basename(filepath)}")
            self.on_export_detected(filepath)
            processed_count += 1
        return processed_count

    def on_export_detected(self, filepath):
        """
        Triggered in a background thread when a new export file is detected/created.
        """
        # Ensure we only process one export file at a time
        with self.processing_lock:
            self.ui.log(f"[Info] File detected: {os.path.basename(filepath)}")
            self.ui.update_progress(0, 0, "Reading export file...")
            
            try:
                # 1. Parse player list
                players = PlayerParser.parse_file(filepath)
                if not players:
                    self.ui.log(f"[Warning] No valid newgen players found in {os.path.basename(filepath)}.")
                    self.ui.update_progress(0, 0, "Ready")
                    return

                self.ui.log(f"[Info] Parsed {len(players)} newgens from export.")

                # 2. Setup folders and XML managers
                graphics_dir = self.config["graphics_directory"]
                xml_manager = XMLManager(graphics_dir)
                existing_mappings = xml_manager.load_mappings()

                # Load or initialize metadata (tracks generated age milestones)
                metadata_path = os.path.join(graphics_dir, "metadata.json")
                player_milestones = {}
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r", encoding="utf-8") as f:
                            player_milestones = json.load(f)
                    except Exception as e:
                        self.ui.log(f"[Warning] Failed to load metadata.json: {e}")

                # 3. Filter players based on Milestone Aging Engine
                players_to_generate = []
                for p in players:
                    uid = p["uid"]
                    current_age = p["age"]
                    current_milestone = self.get_active_milestone(current_age)
                    
                    # Verify if face file exists on disk
                    face_file = os.path.join(graphics_dir, f"{uid}.png")
                    has_face = os.path.exists(face_file) and uid in existing_mappings
                    
                    if not has_face:
                        # Case A: Player does not have a face yet -> Generate
                        players_to_generate.append(p)
                        player_milestones[uid] = current_milestone
                    else:
                        # Case B: Player has a face -> Check if they aged up to a new milestone
                        last_milestone = player_milestones.get(uid, 16) # Default to 16
                        if current_milestone > last_milestone:
                            self.ui.log(f"[Aging] Player {p['name']} (UID: {uid}) aged up ({last_milestone} -> {current_milestone}). Regenerating face...")
                            players_to_generate.append(p)
                            player_milestones[uid] = current_milestone

                # 3b. Load failed downloads queue (App Cache & Retry)
                failed_downloads_path = os.path.join(graphics_dir, "failed_downloads.json")
                failed_players = {}
                if os.path.exists(failed_downloads_path):
                    try:
                        with open(failed_downloads_path, "r", encoding="utf-8") as f:
                            failed_players = json.load(f)
                    except Exception as e:
                        self.ui.log(f"[Warning] Failed to load failed_downloads.json: {e}")

                # Merge currently failed players into players_to_generate if they aren't already there
                to_generate_uids = {p["uid"] for p in players_to_generate}
                added_from_failed = 0
                for f_uid, f_player in failed_players.items():
                    if f_uid not in to_generate_uids:
                        players_to_generate.append(f_player)
                        to_generate_uids.add(f_uid)
                        added_from_failed += 1

                if added_from_failed > 0:
                    self.ui.log(f"[Cache] Added {added_from_failed} previously failed downloads to the retry queue.")

                if not players_to_generate:
                    self.ui.log("[Success] All players in this list already have faces matching their age milestone. Nothing to do!")
                    self.ui.update_progress(0, 0, "Ready")
                    return

                # 4. Generate & Download Faces
                self.ui.log(f"[Info] Preparing to generate {len(players_to_generate)} faces...")
                self.ui.update_stats(len(existing_mappings), len(players_to_generate))

                provider = self.config.get("provider", "comfyui")
                generator = FaceGenerator(
                    graphics_dir,
                    self.config["concurrency_limit"],
                    provider=provider,
                    comfyui_base_url=self.config.get("comfyui_base_url", "http://127.0.0.1:8188"),
                    comfyui_model=self.config.get("comfyui_model", ""),
                    negative_prompt=self.config.get("comfyui_negative_prompt", ""),
                    steps=self.config.get("comfyui_steps", 25),
                    cfg=self.config.get("comfyui_cfg", 6.0),
                    sampler=self.config.get("comfyui_sampler", "euler"),
                    scheduler=self.config.get("comfyui_scheduler", "karras"),
                    width=self.config.get("comfyui_width", 896),
                    height=self.config.get("comfyui_height", 1152)
                )

                # Callback to update UI during download progress
                def on_progress(count, total, result):
                    nonlocal failed_players
                    self.ui.update_progress(count, total, f"Downloading faces...")
                    uid = result["uid"]
                    if result["status"] == "success":
                        # Add newly generated face to xml maps
                        existing_mappings[uid] = uid
                        if uid in failed_players:
                            del failed_players[uid]
                        self.ui.update_stats(len(existing_mappings), total - count)
                    else:
                        friendly_error = self.translate_error(result["error"])
                        self.ui.log(f"[Error] Failed for UID {uid}: {friendly_error}")
                        # Save player details to failed downloads queue for future retry
                        p_detail = next((p for p in players_to_generate if p["uid"] == uid), None)
                        if p_detail:
                            failed_players[uid] = p_detail

                # Run asynchronous download in standard thread loop
                async def _run_generation_checked():
                    # Pre-flight: verify the provider is reachable before queuing
                    # a whole batch of downloads (especially for local ComfyUI).
                    ok, msg = await generator.check_connection()
                    self.ui.log(f"[Provider] {generator.provider_name}: {msg}")
                    if not ok:
                        self.ui.log("[Error] Aborting batch - provider unreachable. "
                                    "Fix the issue, then retry (failed queue saved below).")
                        return False
                    await generator.generate_faces_async(
                        players_to_generate,
                        self.config["face_style"],
                        on_progress
                    )
                    return True

                generation_succeeded = asyncio.run(_run_generation_checked())

                # 5. Save XML Maps, Metadata, and Failed Downloads Queue
                if not generation_succeeded:
                    # Provider was unreachable: queue all pending players for the
                    # next retry and skip the success + skin reload steps.
                    for p in players_to_generate:
                        failed_players.setdefault(p["uid"], p)
                    try:
                        with open(failed_downloads_path, "w", encoding="utf-8") as f:
                            json.dump(failed_players, f, indent=2)
                    except Exception as e:
                        self.ui.log(f"[Warning] Failed to save failed_downloads.json: {e}")
                    self.ui.log(f"[Cache] Queued {len(failed_players)} players for retry when the provider is available.")
                    self.ui.update_progress(0, 0, "Provider unavailable")
                    return

                xml_manager.save_mappings(existing_mappings)
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(player_milestones, f, indent=2)
                
                try:
                    with open(failed_downloads_path, "w", encoding="utf-8") as f:
                        json.dump(failed_players, f, indent=2)
                    if failed_players:
                        self.ui.log(f"[Cache] Saved {len(failed_players)} failed downloads to queue for retry next time.")
                except Exception as e:
                    self.ui.log(f"[Warning] Failed to save failed_downloads.json: {e}")

                self.ui.log(f"[Success] Completed batch. Total faces mapped: {len(existing_mappings)}")
                self.ui.update_progress(0, 0, "Complete!")

                # 6. Trigger Game Auto Reload Skin
                if self.config["auto_reload_skin_hotkey"]:
                    self.trigger_skin_reload()

            except Exception as e:
                self.ui.log(f"[Error] Processing failed: {e}")
                self.ui.update_progress(0, 0, "Error occurred")

    def get_active_milestone(self, age_str):
        """
        Maps a player's age to their active milestone group (16, 20, 24, 28).
        """
        try:
            age = int(age_str)
        except:
            age = 16
        
        if age < 20:
            return 16
        elif age < 24:
            return 20
        elif age < 28:
            return 24
        else:
            return 28

    def trigger_skin_reload(self):
        """
        Simulates Shift + R key combination to force Football Manager skin reload.
        Uses ctypes on Windows for zero-dependency execution.
        """
        self.ui.log("[Action] Attempting automatic skin reload in Football Manager...")
        if sys.platform == "win32":
            try:
                import ctypes
                # Windows keyboard event virtual key codes
                VK_SHIFT = 0x10
                VK_R = 0x52
                KEYEVENTF_KEYUP = 0x0002

                # Press Shift
                ctypes.windll.user32.keybd_event(VK_SHIFT, 0, 0, 0)
                # Press R
                ctypes.windll.user32.keybd_event(VK_R, 0, 0, 0)
                time.sleep(0.05)
                # Release R
                ctypes.windll.user32.keybd_event(VK_R, 0, KEYEVENTF_KEYUP, 0)
                # Release Shift
                ctypes.windll.user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
                
                self.ui.log("[Success] Sent reload hotkey (Shift + R) to system.")
            except Exception as e:
                self.ui.log(f"[Warning] Failed to reload skin: {e}")
        else:
            self.ui.log("[Info] Auto-reload skin hotkey is only supported on Windows. Please press Shift + R manually in FM.")

    def translate_error(self, error_str):
        """
        Translates raw network exceptions or HTTP codes into clean user-facing explanations.
        """
        if "ComfyUI is not running" in error_str:
            return "ComfyUI not running (Start ComfyUI, then run 'Check Provider Connection' to verify)"
        elif "ComfyUI rejected request" in error_str or "did not return a prompt_id" in error_str:
            return f"{error_str} (The ComfyUI workflow may be invalid or needs the FLUX/GTA nodes)"
        elif "ComfyUI error" in error_str:
            return f"{error_str} (The checkpoint may be missing. Add a checkpoint to ComfyUI/models/checkpoints/)"
        elif "ComfyUI generation timed out" in error_str:
            return "ComfyUI generation timed out (The checkpoint is taking too long. Try lowering steps or using a smaller model)"
        elif "429" in error_str:
            return "HTTP 429 (Rate Limited: Too many requests. Staggered queue will auto-retry)"
        elif "400" in error_str:
            return "HTTP 400 (Bad Request: The prompt formatting is invalid)"
        elif any(code in error_str for code in ["500", "502", "503", "504"]):
            return f"{error_str} (Server Error: The generation server is overloaded. Retrying...)"
        elif "ClientConnectorCertificateError" in error_str or "SSLCertVerificationError" in error_str:
            return "SSL Certificate verification failed (Your Windows root certificates are out of sync. Bypassing SSL...)"
        elif "ClientConnectorError" in error_str or "ServerDisconnectedError" in error_str:
            return "Connection Failed (Could not establish connection. Please check your internet connection/firewall)"
        elif "TimeoutError" in error_str:
            return "Timeout Error (The generation server took too long. Retrying...)"
        else:
            return f"Unexpected Error ({error_str})"

if __name__ == "__main__":
    root = tk.Tk()
    app = FMGeneratorApp(root)
    root.mainloop()
