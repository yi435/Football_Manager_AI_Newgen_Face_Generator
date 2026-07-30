import os
import sys
import json
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText

class FMGeneratorUI:
    def __init__(self, root, start_callback, stop_callback, save_config_callback, run_now_callback):
        self.root = root
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.save_config_callback = save_config_callback
        self.run_now_callback = run_now_callback
        
        # Window settings
        self.root.title("FM AI Newgen Generator")
        self.root.geometry("780x580")
        self.root.resizable(True, True)
        
        # Color Theme (Premium Dark Mode)
        self.bg_dark = "#121214"
        self.bg_panel = "#1a1a1e"
        self.bg_input = "#26262b"
        self.fg_light = "#f1f1f5"
        self.fg_muted = "#a5a5b5"
        self.color_accent = "#6c5ce7"  # Deep Purple
        self.color_success = "#00b894" # Teal/Green
        self.color_error = "#d63031"   # Red
        self.color_warning = "#fdcb6e" # Yellow
        self.color_active = "#00cec9"  # Cyan/Teal
        
        self.root.configure(bg=self.bg_dark)
        self._setup_styles()
        self._create_widgets()
        self.watcher_running = False

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Progress Bar style
        style.configure("Custom.Horizontal.TProgressbar", 
                        troughcolor=self.bg_input, 
                        background=self.color_accent, 
                        thickness=15)
        
        # Scrollbar style
        style.configure("Vertical.TScrollbar", 
                        gripcount=0, 
                        background=self.bg_panel, 
                        troughcolor=self.bg_dark)

    def _create_widgets(self):
        # Header Label
        header_frame = tk.Frame(self.root, bg=self.bg_dark)
        header_frame.pack(fill="x", padx=20, pady=15)
        
        title_lbl = tk.Label(header_frame, text="Football Manager AI Newgen Generator", 
                             font=("Segoe UI", 16, "bold"), fg=self.fg_light, bg=self.bg_dark)
        title_lbl.pack(anchor="w")
        
        subtitle_lbl = tk.Label(header_frame, text="Generate unique realistic AI faces dynamically based on age, nationality and personality", 
                                font=("Segoe UI", 9), fg=self.fg_muted, bg=self.bg_dark)
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Main Layout: Top Panel (Paths) & Bottom Panel (Console & Control)
        main_container = tk.Frame(self.root, bg=self.bg_dark)
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 1. Config/Paths Panel
        path_frame = tk.LabelFrame(main_container, text=" Configuration & Paths ", 
                                   font=("Segoe UI", 10, "bold"), fg=self.color_accent, 
                                   bg=self.bg_panel, bd=1, relief="solid", padx=15, pady=15)
        path_frame.pack(fill="x", pady=(0, 15))

        # Watch Directory Row
        tk.Label(path_frame, text="Watch Directory (Exports):", font=("Segoe UI", 9, "bold"), 
                 fg=self.fg_light, bg=self.bg_panel).grid(row=0, column=0, sticky="w", pady=5)
        self.watch_path_var = tk.StringVar()
        self.watch_path_entry = tk.Entry(path_frame, textvariable=self.watch_path_var, width=55, 
                                         font=("Segoe UI", 9), bg=self.bg_input, fg=self.fg_light, 
                                         insertbackground=self.fg_light, bd=0, highlightthickness=1,
                                         highlightbackground=self.bg_input, highlightcolor=self.color_accent)
        self.watch_path_entry.grid(row=0, column=1, padx=(10, 5), pady=5)
        
        watch_btn = tk.Button(path_frame, text="Browse", font=("Segoe UI", 9), bg=self.color_accent, 
                              fg=self.fg_light, activebackground="#5848c2", activeforeground=self.fg_light,
                              bd=0, padx=12, pady=2, command=self._browse_watch_dir)
        watch_btn.grid(row=0, column=2, padx=5, pady=5)

        # Graphics Directory Row
        tk.Label(path_frame, text="Graphics Directory (Faces):", font=("Segoe UI", 9, "bold"), 
                 fg=self.fg_light, bg=self.bg_panel).grid(row=1, column=0, sticky="w", pady=5)
        self.graphics_path_var = tk.StringVar()
        self.graphics_path_entry = tk.Entry(path_frame, textvariable=self.graphics_path_var, width=55, 
                                            font=("Segoe UI", 9), bg=self.bg_input, fg=self.fg_light, 
                                            insertbackground=self.fg_light, bd=0, highlightthickness=1,
                                            highlightbackground=self.bg_input, highlightcolor=self.color_accent)
        self.graphics_path_entry.grid(row=1, column=1, padx=(10, 5), pady=5)
        
        graphics_btn = tk.Button(path_frame, text="Browse", font=("Segoe UI", 9), bg=self.color_accent, 
                                 fg=self.fg_light, activebackground="#5848c2", activeforeground=self.fg_light,
                                 bd=0, padx=12, pady=2, command=self._browse_graphics_dir)
        graphics_btn.grid(row=1, column=2, padx=5, pady=5)

        # Settings checklist row
        settings_frame = tk.Frame(path_frame, bg=self.bg_panel)
        settings_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.auto_reload_var = tk.BooleanVar()
        auto_reload_chk = tk.Checkbutton(settings_frame, text="Auto Reload Skin (Shift + R) after generation", 
                                         variable=self.auto_reload_var, onvalue=True, offvalue=False,
                                         bg=self.bg_panel, fg=self.fg_light, selectcolor=self.bg_input,
                                         activebackground=self.bg_panel, activeforeground=self.fg_light, 
                                         font=("Segoe UI", 9), command=self._save_settings)
        auto_reload_chk.pack(side="left", padx=(0, 20))

        # Status and Controls Row
        control_status_frame = tk.Frame(main_container, bg=self.bg_dark)
        control_status_frame.pack(fill="x", pady=(0, 15))

        # Status Panel (Left)
        status_card = tk.Frame(control_status_frame, bg=self.bg_panel, bd=1, relief="solid")
        status_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.status_title_lbl = tk.Label(status_card, text="Watcher Status: STOPPED", font=("Segoe UI", 10, "bold"), 
                                         fg=self.color_error, bg=self.bg_panel, padx=15, pady=8)
        self.status_title_lbl.pack(anchor="w")

        # Stats sublabels
        self.stats_lbl = tk.Label(status_card, text="Faces Generated: 0 | Queued: 0", font=("Segoe UI", 9),
                                  fg=self.fg_muted, bg=self.bg_panel, padx=15)
        self.stats_lbl.pack(anchor="w", pady=(0, 8))

        # Action Buttons (Right)
        btn_frame = tk.Frame(control_status_frame, bg=self.bg_dark)
        btn_frame.pack(side="right")

        self.toggle_btn = tk.Button(btn_frame, text="Start Watcher", font=("Segoe UI", 10, "bold"), 
                                    bg=self.color_success, fg=self.fg_light, activebackground="#009477", 
                                    activeforeground=self.fg_light, bd=0, padx=20, pady=8, command=self._toggle_watcher)
        self.toggle_btn.pack(side="left", padx=5)

        self.run_now_btn = tk.Button(btn_frame, text="Process Existing Files", font=("Segoe UI", 10, "bold"), 
                                     bg=self.color_accent, fg=self.fg_light, activebackground="#5848c2", 
                                     activeforeground=self.fg_light, bd=0, padx=20, pady=8, command=self._run_now)
        self.run_now_btn.pack(side="left", padx=5)

        # 2. Console / Logs Panel
        console_frame = tk.LabelFrame(main_container, text=" Live Console Logs ", 
                                      font=("Segoe UI", 10, "bold"), fg=self.color_accent, 
                                      bg=self.bg_panel, bd=1, relief="solid", padx=10, pady=10)
        console_frame.pack(fill="both", expand=True)

        self.console = ScrolledText(console_frame, bg=self.bg_dark, fg=self.fg_light, 
                                    insertbackground=self.fg_light, font=("Consolas", 9), bd=0)
        self.console.pack(fill="both", expand=True)
        self.console.configure(state="disabled")

        # 3. Progress Bar (At the bottom)
        progress_container = tk.Frame(self.root, bg=self.bg_dark)
        progress_container.pack(fill="x", side="bottom", padx=20, pady=(0, 15))
        
        self.progress_lbl = tk.Label(progress_container, text="Ready", font=("Segoe UI", 9), 
                                     fg=self.fg_muted, bg=self.bg_dark)
        self.progress_lbl.pack(anchor="w", pady=(0, 4))
        
        self.progress_bar = ttk.Progressbar(progress_container, orient="horizontal", mode="determinate", 
                                            style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x")

    def _browse_watch_dir(self):
        dir_path = filedialog.askdirectory(title="Select Folder to Watch for Exports")
        if dir_path:
            # Normalize path slashes
            dir_path = os.path.normpath(dir_path)
            self.watch_path_var.set(dir_path)
            self._save_settings()

    def _browse_graphics_dir(self):
        dir_path = filedialog.askdirectory(title="Select FM graphics/AI Newgen Faces Folder")
        if dir_path:
            dir_path = os.path.normpath(dir_path)
            self.graphics_path_var.set(dir_path)
            self._save_settings()

    def _save_settings(self):
        self.save_config_callback(
            self.watch_path_var.get(),
            self.graphics_path_var.get(),
            self.auto_reload_var.get()
        )

    def _toggle_watcher(self):
        if self.watcher_running:
            self.stop_callback()
            self.toggle_btn.configure(text="Start Watcher", bg=self.color_success, activebackground="#009477")
            self.status_title_lbl.configure(text="Watcher Status: STOPPED", fg=self.color_error)
            self.watcher_running = False
            self.log("[Info] Watcher background service stopped.")
        else:
            # Validate directories before starting
            watch_dir = self.watch_path_var.get()
            graphics_dir = self.graphics_path_var.get()
            if not watch_dir or not graphics_dir:
                messagebox.showerror("Error", "Please set both Watch and Graphics directories before starting the watcher.")
                return

            if self.start_callback(watch_dir, graphics_dir):
                self.toggle_btn.configure(text="Stop Watcher", bg=self.color_error, activebackground="#b22021")
                self.status_title_lbl.configure(text="Watcher Status: RUNNING (Active)", fg=self.color_active)
                self.watcher_running = True
                self.log(f"[Info] Watcher service started. Monitoring: {watch_dir}")
                self.log(f"[Info] Target faces output directory: {graphics_dir}")

    def _run_now(self):
        watch_dir = self.watch_path_var.get()
        graphics_dir = self.graphics_path_var.get()
        if not watch_dir or not graphics_dir:
            messagebox.showerror("Error", "Please configure both Watch and Graphics directories first.")
            return
        
        self.run_now_btn.configure(state="disabled")
        # Run in thread to keep GUI responsive
        threading.Thread(target=self._execute_run_now, args=(watch_dir, graphics_dir), daemon=True).start()

    def _execute_run_now(self, watch_dir, graphics_dir):
        try:
            self.log("[Info] Scanning watcher directory manually for existing export files...")
            count = self.run_now_callback(watch_dir, graphics_dir)
            self.log(f"[Info] Manual scan completed. Processed {count} export file(s).")
        except Exception as e:
            self.log(f"[Error] Manual scan failed: {e}")
        finally:
            self.root.after(0, lambda: self.run_now_btn.configure(state="normal"))

    # Thread-Safe log function
    def log(self, message):
        self.root.after(0, self._safe_log, message)

    def _safe_log(self, message):
        self.console.configure(state="normal")
        self.console.insert("end", f"{message}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    # Thread-Safe stats update
    def update_stats(self, generated_count, queued_count=0):
        self.root.after(0, self._safe_update_stats, generated_count, queued_count)

    def _safe_update_stats(self, generated_count, queued_count):
        self.stats_lbl.configure(text=f"Faces Generated: {generated_count} | Queued: {queued_count}")

    # Thread-Safe progress updates
    def update_progress(self, current, total, text=""):
        self.root.after(0, self._safe_update_progress, current, total, text)

    def _safe_update_progress(self, current, total, text):
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar["value"] = percentage
            self.progress_lbl.configure(text=f"{text} ({percentage}%) - {current}/{total}")
        else:
            self.progress_bar["value"] = 0
            self.progress_lbl.configure(text=text if text else "Ready")

    # Load config file settings into UI variables
    def load_config(self, watch_dir, graphics_dir, auto_reload):
        self.watch_path_var.set(watch_dir)
        self.graphics_path_var.set(graphics_dir)
        self.auto_reload_var.set(auto_reload)
        self.log("[Info] Settings loaded successfully.")
