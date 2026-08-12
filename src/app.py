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
    "face_style": "professional headshot photo of a male [AGE]-year-old [NATIONALITY] football player, [PERSONALITY], athletic build, realistic face, highly detailed skin texture, professional sports photography, neutral background",
    "concurrency_limit": 5,
    "auto_reload_skin_hotkey": False,
    "provider": "comfyui",
    "comfyui_base_url": "http://127.0.0.1:8188",
    "comfyui_model": "",
    "comfyui_negative_prompt": "deformed, blurry, out of focus, low quality, bad anatomy, watermark, text, logo, cartoon, illustration, 3d render, painting, extra fingers, mutated hands, extra limbs, ugly, distorted face, oversaturated",
    "comfyui_steps": 25,
    "comfyui_cfg": 6.0,
    "comfyui_sampler": "euler_a",
    "comfyui_scheduler": "karras",
    "comfyui_size": 1024
}

class FMGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.config_path = "config.json"
        self.config = self._load_config()
        
        # Instantiate UI
        self.ui = FMGeneratorUI(
            root=root,
            start_callback=self.start_watcher,
            stop_callback=self.stop_watcher,
            save_config_callback=self.save_config,
            run_now_callback=self.run_now,
            check_provider_callback=self.check_provider
        )
        
        # Load configuration into UI
        self.ui.load_config(
            self.config["watch_directory"],
            self.config["graphics_directory"],
            self.config["auto_reload_skin_hotkey"],
            self.config.get("provider", "comfyui"),
            self.config.get("comfyui_base_url", "http://127.0.0.1:8188")
        )
        
        self.watcher = None
        self.processing_lock = threading.Lock()

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge keys to ensure compatibility
                    for k, v in DEFAULT_CONFIG.items():
                        if k not in data:
                            data[k] = v
                    return data
            except Exception as e:
                print(f"Error reading config: {e}. Loading defaults.")
        return DEFAULT_CONFIG.copy()

    def save_config(self, watch_dir, graphics_dir, auto_reload, provider=None, comfyui_base_url=None):
        self.config["watch_directory"] = watch_dir
        self.config["graphics_directory"] = graphics_dir
        self.config["auto_reload_skin_hotkey"] = auto_reload
        if provider:
            self.config["provider"] = provider
        if comfyui_base_url:
            self.config["comfyui_base_url"] = comfyui_base_url
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.ui.log(f"[Error] Failed to save config.json: {e}")

    def check_provider(self):
        """
        Pings the selected provider from a background thread and logs the result.
        """
        try:
            generator = FaceGenerator(
                self.config.get("graphics_directory", "./graphics/AI Newgen Faces"),
                concurrency_limit=1,
                api_key=self.config.get("api_key", None),
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

                api_key = self.config.get("api_key", None)
                provider = self.config.get("provider", "comfyui")
                generator = FaceGenerator(
                    graphics_dir,
                    self.config["concurrency_limit"],
                    api_key,
                    provider=provider,
                    comfyui_base_url=self.config.get("comfyui_base_url", "http://127.0.0.1:8188"),
                    comfyui_model=self.config.get("comfyui_model", ""),
                    negative_prompt=self.config.get("comfyui_negative_prompt", ""),
                    steps=self.config.get("comfyui_steps", 25),
                    cfg=self.config.get("comfyui_cfg", 6.0),
                    sampler=self.config.get("comfyui_sampler", "euler_a"),
                    scheduler=self.config.get("comfyui_scheduler", "karras"),
                    size=self.config.get("comfyui_size", 1024)
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
            return "HTTP 429 (Rate Limited: Pollinations.ai is busy. Staggered queue will auto-retry)"
        elif "400" in error_str:
            return "HTTP 400 (Bad Request: The prompt formatting is invalid)"
        elif any(code in error_str for code in ["500", "502", "503", "504"]):
            return f"{error_str} (Server Error: Pollinations.ai is currently overloaded. Retrying...)"
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
