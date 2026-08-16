import os
import sys
import json
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText

class FMGeneratorUI:
    def __init__(self, root, start_callback, stop_callback, save_config_callback, run_now_callback, check_provider_callback=None, maintenance_callback=None, face_style_callback=None):
        self.root = root
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.save_config_callback = save_config_callback
        self.run_now_callback = run_now_callback
        self.check_provider_callback = check_provider_callback
        self.maintenance_callback = maintenance_callback
        self.face_style_callback = face_style_callback
        
        # Window settings
        self.root.title("FM AI Newgen Generator")
        self.root.geometry("880x700")
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
        
        # Combobox style (dark theme)
        style.configure("Custom.TCombobox",
                        fieldbackground=self.bg_input,
                        background=self.bg_input,
                        foreground=self.fg_light,
                        arrowcolor=self.fg_light,
                        bordercolor=self.bg_input,
                        lightcolor=self.bg_input,
                        darkcolor=self.bg_input)
        style.map("Custom.TCombobox",
                  fieldbackground=[("readonly", self.bg_input)],
                  foreground=[("readonly", self.fg_light)],
                  selectbackground=[("readonly", self.color_accent)],
                  selectforeground=[("readonly", self.fg_light)])

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

        # Provider selection row
        provider_row = tk.Frame(path_frame, bg=self.bg_panel)
        provider_row.grid(row=3, column=0, columnspan=3, sticky="w", pady=(5, 0))

        tk.Label(provider_row, text="Face Provider:", font=("Segoe UI", 9, "bold"),
                 fg=self.fg_light, bg=self.bg_panel).pack(side="left")

        self.provider_labels = {
            "comfyui": "Local ComfyUI (SDXL)"
        }
        self.provider_rev = {v: k for k, v in self.provider_labels.items()}
        self.provider_var = tk.StringVar(value=self.provider_labels["comfyui"])
        provider_cb = ttk.Combobox(provider_row, textvariable=self.provider_var,
                                   values=list(self.provider_labels.values()),
                                   state="readonly", width=24, font=("Segoe UI", 9),
                                   style="Custom.TCombobox")
        provider_cb.pack(side="left", padx=(8, 15))
        provider_cb.bind("<<ComboboxSelected>>", lambda e: self._on_provider_change())

        self.check_btn = tk.Button(provider_row, text="Test Connection", font=("Segoe UI", 9, "bold"),
                                   bg=self.color_active, fg=self.bg_dark, activebackground="#00b8b8",
                                   activeforeground=self.bg_dark, bd=0, padx=12, pady=2,
                                   command=self._check_provider)
        self.check_btn.pack(side="left", padx=(0, 15))

        self.maintenance_btn = tk.Button(provider_row, text="Maintenance", font=("Segoe UI", 9, "bold"),
                                         bg=self.bg_input, fg=self.fg_light, activebackground="#3a3a44",
                                         activeforeground=self.fg_light, bd=0, padx=10, pady=2,
                                         command=self._open_maintenance)
        self.maintenance_btn.pack(side="left", padx=(0, 15))

        self.style_btn = tk.Button(provider_row, text="Edit Face Style…", font=("Segoe UI", 9, "bold"),
                                   bg=self.bg_input, fg=self.fg_light, activebackground="#3a3a44",
                                   activeforeground=self.fg_light, bd=0, padx=10, pady=2,
                                   command=self._open_face_style)
        self.style_btn.pack(side="left", padx=(0, 15))

        self.comfy_url_lbl = tk.Label(provider_row, text="ComfyUI URL:", font=("Segoe UI", 9, "bold"),
                                      fg=self.fg_light, bg=self.bg_panel)
        self.comfy_url_lbl.pack(side="left")
        self.comfy_url_var = tk.StringVar(value="http://127.0.0.1:8188")
        self.comfy_url_entry = tk.Entry(provider_row, textvariable=self.comfy_url_var, width=24,
                                        font=("Segoe UI", 9), bg=self.bg_input, fg=self.fg_light,
                                        insertbackground=self.fg_light, bd=0, highlightthickness=1,
                                        highlightbackground=self.bg_input, highlightcolor=self.color_accent)
        self.comfy_url_entry.pack(side="left", padx=(6, 0))
        self.comfy_url_entry.bind("<KeyRelease>", lambda e: self._save_settings())

        self.provider_status_lbl = tk.Label(provider_row, text="", font=("Segoe UI", 8),
                                            fg=self.fg_muted, bg=self.bg_panel)
        self.provider_status_lbl.pack(side="left", padx=(10, 0))

        # Generation tuning row
        tuning_frame = tk.LabelFrame(path_frame, text=" Generation Settings (ComfyUI) ",
                                     font=("Segoe UI", 9, "bold"), fg=self.color_accent,
                                     bg=self.bg_panel, bd=1, relief="solid")
        tuning_frame.grid(row=4, column=0, columnspan=3, sticky="we", pady=(12, 0))
        tuning_frame.grid_columnconfigure(0, weight=1)
        tuning_frame.grid_columnconfigure(1, weight=1)

        self.steps_var = tk.StringVar()
        self.cfg_var = tk.StringVar()
        self.sampler_var = tk.StringVar()
        self.scheduler_var = tk.StringVar()
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.concurrency_var = tk.StringVar()
        self.advanced_var = tk.BooleanVar(value=False)
        self._tune_rows = {}

        def _tune_field(parent, col, row, label, widget):
            lbl = tk.Label(parent, text=label, font=("Segoe UI", 8, "bold"),
                           fg=self.fg_muted, bg=self.bg_panel)
            lbl.grid(row=row, column=col * 2, sticky="w", padx=(10, 4), pady=(6, 0))
            widget.grid(row=row, column=col * 2 + 1, sticky="w", padx=(0, 10), pady=(6, 0))
            self._tune_rows.setdefault(row, []).extend([lbl, widget])
            return widget

        steps_spin = tk.Spinbox(tuning_frame, from_=1, to=150, width=6, textvariable=self.steps_var,
                                font=("Segoe UI", 9), bg=self.bg_input, fg=self.fg_light,
                                insertbackground=self.fg_light, bd=0, highlightthickness=1,
                                highlightbackground=self.bg_input, highlightcolor=self.color_accent,
                                buttonbackground=self.bg_input, buttoncursor="hand2")
        cfg_spin = tk.Spinbox(tuning_frame, from_=0.5, to=30.0, increment=0.5, width=6, textvariable=self.cfg_var,
                              font=("Segoe UI", 9), bg=self.bg_input, fg=self.fg_light,
                              insertbackground=self.fg_light, bd=0, highlightthickness=1,
                              highlightbackground=self.bg_input, highlightcolor=self.color_accent,
                              buttonbackground=self.bg_input, buttoncursor="hand2")
        sampler_cb = ttk.Combobox(tuning_frame, textvariable=self.sampler_var, state="readonly", width=14,
                                  values=["euler", "normal", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_sde", "lms", "sde", "heun", "ddim"],
                                  font=("Segoe UI", 9), style="Custom.TCombobox")
        scheduler_cb = ttk.Combobox(tuning_frame, textvariable=self.scheduler_var, state="readonly", width=14,
                                    values=["karras", "normal", "simple", "ddim_uniform", "sgm_uniform", "beta"],
                                    font=("Segoe UI", 9), style="Custom.TCombobox")
        width_spin = tk.Spinbox(tuning_frame, from_=512, to=2048, increment=64, width=6, textvariable=self.width_var,
                                font=("Segoe UI", 9), bg=self.bg_input, fg=self.fg_light,
                                insertbackground=self.fg_light, bd=0, highlightthickness=1,
                                highlightbackground=self.bg_input, highlightcolor=self.color_accent,
                                buttonbackground=self.bg_input, buttoncursor="hand2")
        height_spin = tk.Spinbox(tuning_frame, from_=512, to=2048, increment=64, width=6, textvariable=self.height_var,
                                 font=("Segoe UI", 9), bg=self.bg_input, fg=self.fg_light,
                                 insertbackground=self.fg_light, bd=0, highlightthickness=1,
                                 highlightbackground=self.bg_input, highlightcolor=self.color_accent,
                                 buttonbackground=self.bg_input, buttoncursor="hand2")
        concurrency_spin = tk.Spinbox(tuning_frame, from_=1, to=8, width=6, textvariable=self.concurrency_var,
                                      font=("Segoe UI", 9), bg=self.bg_input, fg=self.fg_light,
                                      insertbackground=self.fg_light, bd=0, highlightthickness=1,
                                      highlightbackground=self.bg_input, highlightcolor=self.color_accent,
                                      buttonbackground=self.bg_input, buttoncursor="hand2")

        _tune_field(tuning_frame, 0, 0, "Steps (1-150):", steps_spin)
        _tune_field(tuning_frame, 1, 0, "CFG (0.5-30):", cfg_spin)
        _tune_field(tuning_frame, 0, 1, "Sampler:", sampler_cb)
        _tune_field(tuning_frame, 1, 1, "Scheduler:", scheduler_cb)
        _tune_field(tuning_frame, 0, 2, "Width (px):", width_spin)
        _tune_field(tuning_frame, 1, 2, "Height (px):", height_spin)
        _tune_field(tuning_frame, 0, 3, "Concurrency (1-8):", concurrency_spin)
        tk.Label(tuning_frame, text="", font=("Segoe UI", 9),
                 fg=self.fg_muted, bg=self.bg_panel).grid(row=1, column=1, sticky="w")

        for w in (steps_spin, cfg_spin, width_spin, height_spin, concurrency_spin):
            w.bind("<KeyRelease>", lambda e: self._save_settings())
            w.bind("<<Increment>>", lambda e: self._save_settings())
            w.bind("<<Decrement>>", lambda e: self._save_settings())
        for cb in (sampler_cb, scheduler_cb):
            cb.bind("<<ComboboxSelected>>", lambda e: self._save_settings())

        self.advanced_chk = tk.Checkbutton(
            tuning_frame, text="Show advanced settings (steps, CFG, sampler, concurrency)",
            variable=self.advanced_var, command=self._toggle_advanced,
            bg=self.bg_panel, fg=self.fg_muted, selectcolor=self.bg_input,
            activebackground=self.bg_panel, activeforeground=self.fg_light,
            font=("Segoe UI", 8))
        self.advanced_chk.grid(row=4, column=0, columnspan=2, sticky="w",
                               padx=10, pady=(4, 0))
        # Start in casual mode: hide the technical rows (steps/CFG, sampler/
        # scheduler, concurrency) and keep only width & height visible.
        self._apply_advanced(False)

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

    def _tuning_values(self):
        def _float(var):
            try:
                return float(var.get())
            except (ValueError, tk.TclError):
                return None
        steps = _float(self.steps_var)
        cfg = _float(self.cfg_var)
        width = _float(self.width_var)
        height = _float(self.height_var)
        concurrency = _float(self.concurrency_var)
        return {
            "comfyui_steps": int(steps) if steps is not None else None,
            "comfyui_cfg": cfg,
            "comfyui_sampler": self.sampler_var.get().strip() or None,
            "comfyui_scheduler": self.scheduler_var.get().strip() or None,
            "comfyui_width": int(width) if width is not None else None,
            "comfyui_height": int(height) if height is not None else None,
            "concurrency_limit": int(concurrency) if concurrency is not None else None,
            "show_advanced_settings": self.advanced_var.get(),
        }

    def _apply_advanced(self, show):
        """Shows/hides the technical tuning rows without saving anything."""
        for row in (0, 1, 3):  # steps/CFG, sampler/scheduler, concurrency
            for w in self._tune_rows.get(row, []):
                if show:
                    w.grid()
                else:
                    w.grid_remove()

    def _toggle_advanced(self):
        self._apply_advanced(self.advanced_var.get())
        self._save_settings()

    def set_provider_status(self, text, color=None):
        """Thread-safe status text next to the Test Connection button."""
        self.root.after(0, lambda: self.provider_status_lbl.configure(
            text=text, fg=color or self.fg_muted))

    def _save_settings(self):
        self.save_config_callback(
            self.watch_path_var.get(),
            self.graphics_path_var.get(),
            self.auto_reload_var.get(),
            self.get_provider(),
            self.comfy_url_var.get().strip(),
            self._tuning_values()
        )

    def get_provider(self):
        """Returns the config provider key matching the current dropdown selection."""
        return self.provider_rev.get(self.provider_var.get(), "comfyui")

    def _on_provider_change(self):
        # Enable/disable the ComfyUI URL field depending on the selected provider
        is_comfy = self.get_provider() == "comfyui"
        state = "normal" if is_comfy else "disabled"
        self.comfy_url_entry.configure(state=state)
        self.provider_status_lbl.configure(text="")
        self._save_settings()

    def _open_maintenance(self):
        if self.maintenance_callback:
            self.maintenance_callback()
        else:
            self.log("[Info] Maintenance is only available in the packaged app.")

    def _open_face_style(self):
        if not self.face_style_callback:
            self.log("[Info] Face style editor is not available in this build.")
            return
        data = self.face_style_callback("get")
        if not data:
            return
        positive, negative, default_pos, default_neg = data

        win = tk.Toplevel(self.root)
        win.title("Face Style & Prompt Editor")
        win.configure(bg=self.bg_dark)
        win.geometry("700x580")
        win.minsize(620, 520)

        tk.Label(win, text="Face Style (positive prompt)", font=("Segoe UI", 10, "bold"),
                 fg=self.fg_light, bg=self.bg_dark).pack(anchor="w", padx=20, pady=(16, 4))
        tk.Label(win, text="This text describes every player photo. [AGE], [NATIONALITY] and "
                           "[PERSONALITY] are filled in automatically.",
                 font=("Segoe UI", 8), fg=self.fg_muted, bg=self.bg_dark).pack(anchor="w", padx=20, pady=(0, 6))
        pos_text = tk.Text(win, height=8, wrap="word", font=("Segoe UI", 9),
                           bg=self.bg_input, fg=self.fg_light, insertbackground=self.fg_light,
                           bd=0, highlightthickness=1, highlightbackground=self.bg_input,
                           highlightcolor=self.color_accent, padx=8, pady=6)
        pos_text.pack(fill="x", padx=20)
        pos_text.insert("1.0", positive)

        tk.Label(win, text="Negative prompt (things to avoid)", font=("Segoe UI", 10, "bold"),
                 fg=self.fg_light, bg=self.bg_dark).pack(anchor="w", padx=20, pady=(14, 4))
        tk.Label(win, text="Everything listed here is discouraged: bad backgrounds, logos, "
                           "AI-looking skin, wrong poses…",
                 font=("Segoe UI", 8), fg=self.fg_muted, bg=self.bg_dark).pack(anchor="w", padx=20, pady=(0, 6))
        neg_text = tk.Text(win, height=7, wrap="word", font=("Segoe UI", 9),
                           bg=self.bg_input, fg=self.fg_light, insertbackground=self.fg_light,
                           bd=0, highlightthickness=1, highlightbackground=self.bg_input,
                           highlightcolor=self.color_accent, padx=8, pady=6)
        neg_text.pack(fill="x", padx=20)
        neg_text.insert("1.0", negative)

        tk.Label(win, text="Tip: players under 20 are automatically described as teenagers with "
                           "smooth, youthful features — no need to add that yourself.",
                 font=("Segoe UI", 8), fg=self.color_warning, bg=self.bg_dark).pack(anchor="w", padx=20, pady=(10, 0))

        def _save():
            p = pos_text.get("1.0", "end-1c").strip()
            n = neg_text.get("1.0", "end-1c").strip()
            if not p:
                messagebox.showwarning("Empty style", "The positive prompt cannot be empty.")
                return
            self.face_style_callback("save", p, n)
            win.destroy()

        def _reset():
            pos_text.delete("1.0", "end")
            pos_text.insert("1.0", default_pos)
            neg_text.delete("1.0", "end")
            neg_text.insert("1.0", default_neg)

        btn_row = tk.Frame(win, bg=self.bg_dark)
        btn_row.pack(fill="x", padx=20, pady=16)
        tk.Button(btn_row, text="Save & Close", font=("Segoe UI", 10, "bold"), bg=self.color_accent,
                  fg=self.fg_light, activebackground="#5848c2", activeforeground=self.fg_light,
                  bd=0, padx=18, pady=6, command=_save).pack(side="left")
        tk.Button(btn_row, text="Reset to Defaults", font=("Segoe UI", 9, "bold"), bg=self.bg_input,
                  fg=self.fg_light, activebackground="#3a3a44", activeforeground=self.fg_light,
                  bd=0, padx=14, pady=6, command=_reset).pack(side="left", padx=(10, 0))
        tk.Button(btn_row, text="Cancel", font=("Segoe UI", 9), bg=self.bg_input,
                  fg=self.fg_muted, activebackground="#3a3a44", activeforeground=self.fg_light,
                  bd=0, padx=14, pady=6, command=win.destroy).pack(side="right")

    def _check_provider(self):
        if not self.check_provider_callback:
            self.log("[Info] No provider check available.")
            return
        self.check_btn.configure(state="disabled")
        self.provider_status_lbl.configure(text="Checking...")
        threading.Thread(target=self._execute_check_provider, daemon=True).start()

    def _execute_check_provider(self):
        try:
            ok = self.check_provider_callback()
            label = "Connected" if ok else "FAILED - see log for details"
            color = self.color_success if ok else self.color_error
            self.root.after(0, lambda: self.provider_status_lbl.configure(text=label, fg=color))
        except Exception as e:
            self.root.after(0, lambda: self.provider_status_lbl.configure(text="Error during check", fg=self.color_error))
            self.log(f"[Error] Provider check failed: {e}")
        finally:
            self.root.after(0, lambda: self.check_btn.configure(state="normal"))
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
    def load_config(self, watch_dir, graphics_dir, auto_reload, provider="comfyui",
                    comfyui_base_url="http://127.0.0.1:8188",
                    steps=25, cfg=6.0, sampler="euler", scheduler="karras",
                    width=896, height=1152, concurrency_limit=1,
                    show_advanced=False):
        self.watch_path_var.set(watch_dir)
        self.graphics_path_var.set(graphics_dir)
        self.auto_reload_var.set(auto_reload)
        if provider in self.provider_labels:
            self.provider_var.set(self.provider_labels[provider])
        self.comfy_url_var.set(comfyui_base_url)
        is_comfy = (provider in (None, "", "comfyui"))
        self.comfy_url_entry.configure(state="normal" if is_comfy else "disabled")
        self.steps_var.set(steps)
        self.cfg_var.set(cfg)
        self.sampler_var.set(sampler)
        self.scheduler_var.set(scheduler)
        self.width_var.set(width)
        self.height_var.set(height)
        self.concurrency_var.set(concurrency_limit)
        self.advanced_var.set(bool(show_advanced))
        self._apply_advanced(bool(show_advanced))
        self.log("[Info] Settings loaded successfully.")
