import os
import sys
import json
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText
try:
    from PIL import Image, ImageTk
    HAS_PIL_TK = True
except ImportError:
    try:
        from PIL import Image
    except ImportError:
        Image = None
    HAS_PIL_TK = False
    ImageTk = None


class FMGeneratorUI:
    def __init__(self, root, start_callback, stop_callback, save_config_callback,
                 run_now_callback, check_provider_callback=None,
                 maintenance_callback=None, face_style_callback=None,
                 fm26_callback=None, cancel_callback=None,
                 test_face_callback=None, log_path=None):
        self.root = root
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.save_config_callback = save_config_callback
        self.run_now_callback = run_now_callback
        self.check_provider_callback = check_provider_callback
        self.maintenance_callback = maintenance_callback
        self.face_style_callback = face_style_callback
        self.fm26_callback = fm26_callback
        self.cancel_callback = cancel_callback
        self.test_face_callback = test_face_callback
        self.log_path = log_path

        # Window Settings (DESKTOP-APP.md Archetype)
        self.root.title("FM AI Newgen Generator")
        self.root.geometry("980x760")
        self.root.minsize(920, 680)

        # Design Tokens (DESIGN.md specification)
        self.bg_dark = "#121214"
        self.bg_panel = "#1a1a1e"
        self.bg_elevated = "#222228"
        self.bg_input = "#26262b"
        self.border_subtle = "#2e2e38"
        self.border_focus = "#6c5ce7"
        self.fg_light = "#f1f1f5"
        self.fg_muted = "#a5a5b5"
        self.fg_dim = "#636375"
        self.color_accent = "#6c5ce7"
        self.color_accent_hover = "#5b4bc4"
        self.color_success = "#00b894"
        self.color_warning = "#fdcb6e"
        self.color_error = "#d63031"
        self.color_active = "#00cec9"

        # Fonts Hierarchy
        self.font_title = ("Segoe UI", 13, "bold")
        self.font_subtitle = ("Segoe UI", 8, "normal")
        self.font_header = ("Segoe UI", 10, "bold")
        self.font_body = ("Segoe UI", 9, "normal")
        self.font_body_bold = ("Segoe UI", 9, "bold")
        self.font_small = ("Segoe UI", 8, "normal")
        self.font_small_bold = ("Segoe UI", 8, "bold")
        self.font_mono = ("Consolas", 8, "normal")
        self.font_stat_val = ("Segoe UI", 15, "bold")

        self.root.configure(bg=self.bg_dark)

        # Reactive State Variables
        self.watch_path_var = tk.StringVar(value="./exports")
        self.graphics_path_var = tk.StringVar(value="./graphics/AI Newgen Faces")
        self.auto_reload_var = tk.BooleanVar(value=False)
        self.provider_var = tk.StringVar(value="Local ComfyUI (SDXL)")
        self.comfy_url_var = tk.StringVar(value="http://127.0.0.1:8188")
        self.steps_var = tk.IntVar(value=25)
        self.cfg_var = tk.DoubleVar(value=6.0)
        self.sampler_var = tk.StringVar(value="euler_a")
        self.scheduler_var = tk.StringVar(value="karras")
        self.width_var = tk.IntVar(value=896)
        self.height_var = tk.IntVar(value=1152)
        self.concurrency_var = tk.IntVar(value=1)
        self.show_advanced_var = tk.BooleanVar(value=False)

        self.provider_keys = {"Local ComfyUI (SDXL)": "comfyui"}
        self.provider_labels = {"comfyui": "Local ComfyUI (SDXL)"}

        self.watcher_running = False
        self.is_generating = False
        self.current_preview_path = None
        self._preview_image_ref = None

        self._setup_styles()
        self._create_widgets()
        self._bind_shortcuts()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Custom Progressbar
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor=self.bg_input,
                        background=self.color_accent,
                        darkcolor=self.color_accent,
                        lightcolor=self.color_accent,
                        bordercolor=self.border_subtle,
                        thickness=12)

        # Custom Combobox
        style.configure("Custom.TCombobox",
                        fieldbackground=self.bg_input,
                        background=self.bg_panel,
                        foreground=self.fg_light,
                        darkcolor=self.border_subtle,
                        lightcolor=self.border_subtle,
                        arrowcolor=self.fg_light,
                        insertcolor=self.fg_light,
                        padding=5)
        style.map("Custom.TCombobox",
                  fieldbackground=[("readonly", self.bg_input)],
                  foreground=[("readonly", self.fg_light)],
                  selectbackground=[("readonly", self.bg_elevated)],
                  selectforeground=[("readonly", self.fg_light)])

        # Custom Notebook (Tabs)
        style.configure("Custom.TNotebook",
                        background=self.bg_dark,
                        borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                        background=self.bg_panel,
                        foreground=self.fg_muted,
                        padding=[14, 6],
                        font=self.font_body_bold,
                        borderwidth=0)
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", self.bg_elevated)],
                  foreground=[("selected", self.fg_light)])

    def _create_widgets(self):
        # Master grid container
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)  # Workspace area stretches

        # ---------------------------------------------------------------------
        # 1. TOP HEADER BAR
        # ---------------------------------------------------------------------
        header_frame = tk.Frame(self.root, bg=self.bg_panel, height=56,
                                highlightthickness=1, highlightbackground=self.border_subtle)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.columnconfigure(0, weight=1)

        # Brand / Title
        brand_box = tk.Frame(header_frame, bg=self.bg_panel)
        brand_box.pack(side="left", padx=16, pady=10)

        title_lbl = tk.Label(brand_box, text="⚽ FM AI NEWGEN GENERATOR",
                             font=self.font_title, fg=self.fg_light, bg=self.bg_panel)
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(brand_box, text="Real-time SDXL Face Generation & XML Mapping",
                                font=self.font_subtitle, fg=self.fg_muted, bg=self.bg_panel)
        subtitle_lbl.pack(anchor="w")

        # Top Action / Status Controls
        top_actions = tk.Frame(header_frame, bg=self.bg_panel)
        top_actions.pack(side="right", padx=16, pady=10)

        # Provider Status Pill (Clickable)
        self.provider_pill = tk.Button(
            top_actions, text="● ComfyUI Connecting...", font=self.font_small_bold,
            bg=self.bg_input, fg=self.color_warning, activebackground=self.bg_elevated,
            activeforeground=self.fg_light, bd=1, relief="solid",
            highlightthickness=0, padx=10, pady=4, cursor="hand2",
            command=self._check_provider
        )
        self.provider_pill.pack(side="left", padx=(0, 10))

        # Quick Navigation Buttons
        self.btn_tuning = tk.Button(
            top_actions, text="⚙️ Tuning & Prompts", font=self.font_body,
            bg=self.bg_input, fg=self.fg_light, activebackground=self.bg_elevated,
            activeforeground=self.fg_light, bd=0, padx=12, pady=4, cursor="hand2",
            command=self._open_tuning_dialog
        )
        self.btn_tuning.pack(side="left", padx=(0, 6))

        self.btn_maint = tk.Button(
            top_actions, text="🔧 Maintenance", font=self.font_body,
            bg=self.bg_input, fg=self.fg_light, activebackground=self.bg_elevated,
            activeforeground=self.fg_light, bd=0, padx=10, pady=4, cursor="hand2",
            command=self._open_maintenance
        )
        self.btn_maint.pack(side="left", padx=(0, 6))

        self.btn_fm26 = tk.Button(
            top_actions, text="❓ FM26 Guide", font=self.font_body,
            bg=self.bg_input, fg=self.fg_light, activebackground=self.bg_elevated,
            activeforeground=self.fg_light, bd=0, padx=10, pady=4, cursor="hand2",
            command=self._open_fm26_setup
        )
        self.btn_fm26.pack(side="left")

        # ---------------------------------------------------------------------
        # 2. SPLIT WORKSPACE AREA (Left: Batch Hub | Right: Live Inspector)
        # ---------------------------------------------------------------------
        workspace = tk.Frame(self.root, bg=self.bg_dark)
        workspace.grid(row=1, column=0, sticky="nsew", padx=16, pady=12)
        workspace.columnconfigure(0, weight=6, minsize=480)  # Left column (60%)
        workspace.columnconfigure(1, weight=4, minsize=360)  # Right column (40%)
        workspace.rowconfigure(0, weight=1)

        # =====================================================================
        # LEFT COLUMN: PATHS, ACTION CONTROLS & BATCH PROGRESS
        # =====================================================================
        left_col = tk.Frame(workspace, bg=self.bg_dark)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        left_col.columnconfigure(0, weight=1)

        # Card A: Directories & Paths
        paths_card = self._create_card(left_col, "📁 DIRECTORY CONFIGURATION")
        paths_card.pack(fill="x", pady=(0, 10))

        # Watch Directory Row
        tk.Label(paths_card, text="Watch Directory (FM Exports):", font=self.font_body,
                 fg=self.fg_muted, bg=self.bg_panel).pack(anchor="w", padx=12, pady=(8, 2))
        w_row = tk.Frame(paths_card, bg=self.bg_panel)
        w_row.pack(fill="x", padx=12, pady=(0, 8))
        w_row.columnconfigure(0, weight=1)

        self.watch_entry = tk.Entry(w_row, textvariable=self.watch_path_var, font=self.font_body,
                                    bg=self.bg_input, fg=self.fg_light, insertbackground=self.fg_light,
                                    bd=0, highlightthickness=1, highlightbackground=self.border_subtle,
                                    highlightcolor=self.border_focus)
        self.watch_entry.grid(row=0, column=0, sticky="ew", ipady=4)

        tk.Button(w_row, text="📂 Browse", font=self.font_body, bg=self.bg_elevated,
                  fg=self.fg_light, activebackground=self.color_accent, activeforeground=self.fg_light,
                  bd=0, padx=12, pady=4, cursor="hand2", command=self._browse_watch_dir
                  ).grid(row=0, column=1, padx=(6, 0))

        # Graphics Directory Row
        tk.Label(paths_card, text="Graphics Directory (FM Faces Destination):", font=self.font_body,
                 fg=self.fg_muted, bg=self.bg_panel).pack(anchor="w", padx=12, pady=(0, 2))
        g_row = tk.Frame(paths_card, bg=self.bg_panel)
        g_row.pack(fill="x", padx=12, pady=(0, 12))
        g_row.columnconfigure(0, weight=1)

        self.graphics_entry = tk.Entry(g_row, textvariable=self.graphics_path_var, font=self.font_body,
                                       bg=self.bg_input, fg=self.fg_light, insertbackground=self.fg_light,
                                       bd=0, highlightthickness=1, highlightbackground=self.border_subtle,
                                       highlightcolor=self.border_focus)
        self.graphics_entry.grid(row=0, column=0, sticky="ew", ipady=4)

        tk.Button(g_row, text="📂 Browse", font=self.font_body, bg=self.bg_elevated,
                  fg=self.fg_light, activebackground=self.color_accent, activeforeground=self.fg_light,
                  bd=0, padx=12, pady=4, cursor="hand2", command=self._browse_graphics_dir
                  ).grid(row=0, column=1, padx=(6, 0))

        tk.Button(g_row, text="Reveal", font=self.font_small, bg=self.bg_input,
                  fg=self.fg_muted, activebackground=self.bg_elevated, activeforeground=self.fg_light,
                  bd=0, padx=8, pady=4, cursor="hand2", command=self._open_graphics_folder
                  ).grid(row=0, column=2, padx=(4, 0))

        # Card B: Generation & Automation Hub
        action_card = self._create_card(left_col, "⚡ GENERATION & AUTOMATION")
        action_card.pack(fill="x", pady=(0, 10))

        act_inner = tk.Frame(action_card, bg=self.bg_panel)
        act_inner.pack(fill="x", padx=12, pady=12)
        act_inner.columnconfigure(0, weight=1)
        act_inner.columnconfigure(1, weight=1)

        # Big Auto-Watcher Toggle
        self.btn_watcher = tk.Button(
            act_inner, text="⚡ Auto-Watcher: OFF\n(Click to Enable)",
            font=self.font_body_bold, bg=self.bg_input, fg=self.fg_muted,
            activebackground=self.bg_elevated, activeforeground=self.fg_light,
            bd=1, relief="solid", highlightthickness=0, padx=12, pady=10,
            cursor="hand2", command=self._toggle_watcher
        )
        self.btn_watcher.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # Big Run Manual Batch Button
        self.btn_generate = tk.Button(
            act_inner, text="▶ Generate Batch\n(Process Existing)",
            font=self.font_body_bold, bg=self.color_accent, fg=self.fg_light,
            activebackground=self.color_accent_hover, activeforeground=self.fg_light,
            bd=0, padx=12, pady=10, cursor="hand2", command=self._run_now
        )
        self.btn_generate.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # Cancel Batch Button
        self.btn_cancel = tk.Button(
            act_inner, text="⏹ Cancel Running Batch", font=self.font_small_bold,
            bg=self.bg_input, fg=self.color_error, activebackground=self.bg_elevated,
            activeforeground=self.color_error, bd=1, relief="solid",
            highlightthickness=0, padx=10, pady=4, state="disabled",
            cursor="hand2", command=self._cancel_batch
        )
        self.btn_cancel.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        # Card C: Batch Progress & Live Metrics
        metrics_card = self._create_card(left_col, "📊 BATCH PROGRESS & METRICS")
        metrics_card.pack(fill="both", expand=True)

        m_inner = tk.Frame(metrics_card, bg=self.bg_panel)
        m_inner.pack(fill="both", expand=True, padx=12, pady=12)

        # Progress Bar & ETA
        prog_header = tk.Frame(m_inner, bg=self.bg_panel)
        prog_header.pack(fill="x", pady=(0, 4))
        self.lbl_prog_title = tk.Label(prog_header, text="Status: Ready", font=self.font_body_bold,
                                       fg=self.fg_light, bg=self.bg_panel)
        self.lbl_prog_title.pack(side="left")

        self.lbl_eta = tk.Label(prog_header, text="", font=self.font_small,
                                fg=self.color_active, bg=self.bg_panel)
        self.lbl_eta.pack(side="right")

        self.progress_bar = ttk.Progressbar(m_inner, style="Custom.Horizontal.TProgressbar",
                                            mode="determinate", length=300)
        self.progress_bar.pack(fill="x", pady=(0, 12))

        # 3 Metrics Display Cards
        stat_grid = tk.Frame(m_inner, bg=self.bg_panel)
        stat_grid.pack(fill="x")
        stat_grid.columnconfigure(0, weight=1)
        stat_grid.columnconfigure(1, weight=1)
        stat_grid.columnconfigure(2, weight=1)

        self.stat_box_mapped = self._create_stat_box(stat_grid, 0, "FACES MAPPED", "0", self.color_success)
        self.stat_box_queued = self._create_stat_box(stat_grid, 1, "IN RETRY QUEUE", "0", self.color_warning)
        self.stat_box_state = self._create_stat_box(stat_grid, 2, "ENGINE STATE", "Idle", self.fg_muted)

        # =====================================================================
        # RIGHT COLUMN: LIVE FACE INSPECTOR & PREVIEW CARD
        # =====================================================================
        right_col = tk.Frame(workspace, bg=self.bg_dark)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        right_col.columnconfigure(0, weight=1)
        right_col.rowconfigure(0, weight=1)

        preview_card = self._create_card(right_col, "🖼️ LATEST GENERATED FACE")
        preview_card.pack(fill="both", expand=True)

        prev_inner = tk.Frame(preview_card, bg=self.bg_panel)
        prev_inner.pack(fill="both", expand=True, padx=12, pady=12)

        # Portrait Image Canvas / Container
        self.image_container = tk.Frame(prev_inner, bg=self.bg_input,
                                        width=220, height=290,
                                        highlightthickness=1, highlightbackground=self.border_subtle)
        self.image_container.pack(pady=(4, 10))
        self.image_container.pack_propagate(False)

        self.preview_lbl = tk.Label(self.image_container,
                                    text="[ No face generated yet ]\n\nRun a batch or generate\na test face to preview.",
                                    font=self.font_small, fg=self.fg_dim, bg=self.bg_input, justify="center")
        self.preview_lbl.pack(expand=True, fill="both")

        # Player Metadata Details
        self.meta_frame = tk.Frame(prev_inner, bg=self.bg_panel)
        self.meta_frame.pack(fill="x", pady=(0, 10))

        self.lbl_player_name = tk.Label(self.meta_frame, text="Player: None",
                                        font=self.font_body_bold, fg=self.fg_light, bg=self.bg_panel)
        self.lbl_player_name.pack(anchor="w")

        self.lbl_player_sub = tk.Label(self.meta_frame, text="UID: — | Age: — | Nat: —",
                                       font=self.font_small, fg=self.fg_muted, bg=self.bg_panel)
        self.lbl_player_sub.pack(anchor="w")

        # Quick Actions Below Preview
        prev_actions = tk.Frame(prev_inner, bg=self.bg_panel)
        prev_actions.pack(fill="x", pady=(4, 0))
        prev_actions.columnconfigure(0, weight=1)
        prev_actions.columnconfigure(1, weight=1)

        self.btn_view_full = tk.Button(
            prev_actions, text="🔍 Full Image", font=self.font_small_bold,
            bg=self.bg_input, fg=self.fg_light, activebackground=self.bg_elevated,
            activeforeground=self.fg_light, bd=0, padx=8, pady=6,
            cursor="hand2", state="disabled", command=self._view_full_preview
        )
        self.btn_view_full.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_test_face = tk.Button(
            prev_actions, text="⚡ Test Face", font=self.font_small_bold,
            bg=self.bg_elevated, fg=self.color_active, activebackground=self.color_accent,
            activeforeground=self.fg_light, bd=0, padx=8, pady=6,
            cursor="hand2", command=self._generate_test_face
        )
        self.btn_test_face.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # ---------------------------------------------------------------------
        # 3. BOTTOM COLLAPSIBLE DIAGNOSTIC LOG CONSOLE
        # ---------------------------------------------------------------------
        log_frame = tk.Frame(self.root, bg=self.bg_panel,
                             highlightthickness=1, highlightbackground=self.border_subtle)
        log_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))

        # Log Header
        log_hdr = tk.Frame(log_frame, bg=self.bg_panel)
        log_hdr.pack(fill="x", padx=12, pady=(6, 4))

        tk.Label(log_hdr, text="📋 ACTIVITY & DIAGNOSTIC CONSOLE",
                 font=self.font_small_bold, fg=self.fg_muted, bg=self.bg_panel).pack(side="left")

        tk.Button(log_hdr, text="Copy Log", font=self.font_small,
                  bg=self.bg_input, fg=self.fg_muted, activebackground=self.bg_elevated,
                  activeforeground=self.fg_light, bd=0, padx=8, pady=2,
                  cursor="hand2", command=self._copy_log).pack(side="right", padx=(6, 0))

        tk.Button(log_hdr, text="Clear", font=self.font_small,
                  bg=self.bg_input, fg=self.fg_muted, activebackground=self.bg_elevated,
                  activeforeground=self.fg_light, bd=0, padx=8, pady=2,
                  cursor="hand2", command=self._clear_log).pack(side="right")

        # ScrolledText Console with Syntax Color Tags
        self.console = ScrolledText(log_frame, height=6, wrap="word",
                                    font=self.font_mono, bg=self.bg_input, fg=self.fg_light,
                                    insertbackground=self.fg_light, bd=0,
                                    highlightthickness=0, padx=8, pady=6)
        self.console.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        # Configure Syntax Highlight Tags
        self.console.tag_config("info", foreground=self.fg_muted)
        self.console.tag_config("success", foreground=self.color_success, font=("Consolas", 8, "bold"))
        self.console.tag_config("warning", foreground=self.color_warning, font=("Consolas", 8, "bold"))
        self.console.tag_config("error", foreground=self.color_error, font=("Consolas", 8, "bold"))
        self.console.tag_config("cancel", foreground="#e17055", font=("Consolas", 8, "bold"))
        self.console.tag_config("provider", foreground=self.color_active)
        self.console.tag_config("testface", foreground="#a29bfe")
        self.console.tag_config("aging", foreground="#74b9ff")

    # -------------------------------------------------------------------------
    # WIDGET BUILDER HELPERS
    # -------------------------------------------------------------------------
    def _create_card(self, parent, title):
        card = tk.Frame(parent, bg=self.bg_panel,
                        highlightthickness=1, highlightbackground=self.border_subtle)
        hdr = tk.Frame(card, bg=self.bg_elevated, height=26)
        hdr.pack(fill="x", side="top")
        tk.Label(hdr, text=title, font=self.font_small_bold,
                 fg=self.fg_light, bg=self.bg_elevated).pack(anchor="w", padx=10, pady=4)
        return card

    def _create_stat_box(self, parent, col, title, initial_val, color):
        box = tk.Frame(parent, bg=self.bg_input, padx=8, pady=8,
                       highlightthickness=1, highlightbackground=self.border_subtle)
        box.grid(row=0, column=col, sticky="nsew", padx=4)
        tk.Label(box, text=title, font=self.font_subtitle, fg=self.fg_muted, bg=self.bg_input).pack(anchor="w")
        val_lbl = tk.Label(box, text=initial_val, font=self.font_stat_val, fg=color, bg=self.bg_input)
        val_lbl.pack(anchor="w", pady=(2, 0))
        return val_lbl

    def _bind_shortcuts(self):
        """Keyboard interaction rules (DESKTOP-APP.md Archetype)"""
        self.root.bind("<Control-g>", lambda e: self._run_now())
        self.root.bind("<F5>", lambda e: self._run_now())
        self.root.bind("<Control-w>", lambda e: self._toggle_watcher())
        self.root.bind("<Control-t>", lambda e: self._generate_test_face())
        self.root.bind("<Control-s>", lambda e: self._save_settings())
        self.root.bind("<Control-e>", lambda e: self._open_tuning_dialog())
        self.root.bind("<Control-l>", lambda e: self._clear_log())
        self.root.bind("<Escape>", lambda e: self._cancel_batch())

    # -------------------------------------------------------------------------
    # WORKSPACE DIRECTORY & FILE HANDLERS
    # -------------------------------------------------------------------------
    def _browse_watch_dir(self):
        d = filedialog.askdirectory(initialdir=self.watch_path_var.get() or ".",
                                   title="Select FM Export Watch Directory")
        if d:
            self.watch_path_var.set(d)
            self._save_settings()

    def _browse_graphics_dir(self):
        d = filedialog.askdirectory(initialdir=self.graphics_path_var.get() or ".",
                                   title="Select Graphics Faces Directory")
        if d:
            self.graphics_path_var.set(d)
            self._save_settings()

    def _open_graphics_folder(self):
        g_dir = self.graphics_path_var.get()
        if os.path.isdir(g_dir):
            if sys.platform.startswith("win"):
                os.startfile(g_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", g_dir])
            else:
                subprocess.Popen(["xdg-open", g_dir])
        else:
            self.log(f"[Warning] Directory does not exist yet: {g_dir}")

    # -------------------------------------------------------------------------
    # STATE UPDATE METHODS (Thread-safe Tk callbacks)
    # -------------------------------------------------------------------------
    def log(self, message):
        self.root.after(0, self._safe_log, message)

    def _safe_log(self, message):
        tag = "info"
        lower = message.lower()
        if "[success]" in lower:
            tag = "success"
        elif "[warning]" in lower:
            tag = "warning"
        elif "[error]" in lower:
            tag = "error"
        elif "[cancel]" in lower:
            tag = "cancel"
        elif "[provider]" in lower:
            tag = "provider"
        elif "[test face]" in lower:
            tag = "testface"
        elif "[aging]" in lower:
            tag = "aging"

        self.console.insert("end", message + "\n", tag)
        self.console.see("end")

    def update_stats(self, generated_count, queued_count=0):
        self.root.after(0, self._safe_update_stats, generated_count, queued_count)

    def _safe_update_stats(self, generated_count, queued_count):
        self.stat_box_mapped.config(text=str(generated_count))
        self.stat_box_queued.config(text=str(queued_count))

    def update_progress(self, current, total, text=""):
        self.root.after(0, self._safe_update_progress, current, total, text)

    def _safe_update_progress(self, current, total, text):
        if total > 0:
            pct = (current / total) * 100
            self.progress_bar.configure(value=pct)
            self.lbl_prog_title.configure(text=f"Batch: {current}/{total} ({int(pct)}%)")
        else:
            self.progress_bar.configure(value=0)
            self.lbl_prog_title.configure(text=text if text else "Status: Ready")

        # Update ETA if present in text string
        if "left" in text:
            self.lbl_eta.configure(text=text)
        else:
            self.lbl_eta.configure(text="")

    def set_generating(self, generating):
        self.is_generating = generating
        self.root.after(0, self._safe_set_generating, generating)

    def _safe_set_generating(self, generating):
        if generating:
            self.btn_generate.configure(state="disabled", text="⏳ Generating Faces...", bg=self.bg_elevated)
            self.btn_cancel.configure(state="normal")
            self.stat_box_state.configure(text="Generating", fg=self.color_accent)
        else:
            self.btn_generate.configure(state="normal", text="▶ Generate Batch\n(Process Existing)", bg=self.color_accent)
            self.btn_cancel.configure(state="disabled")
            state_txt = "Watching" if self.watcher_running else "Idle"
            state_col = self.color_active if self.watcher_running else self.fg_muted
            self.stat_box_state.configure(text=state_txt, fg=state_col)

    def set_provider_status(self, text, color=None):
        self.root.after(0, self._safe_set_provider_status, text, color)

    def _safe_set_provider_status(self, text, color):
        c = color or (self.color_success if "connect" in text.lower() else self.color_error)
        self.provider_pill.configure(text=f"● ComfyUI {text}", fg=c)

    def set_watch_directory(self, path):
        self.watch_path_var.set(path)
        self._save_settings()

    def show_latest_face(self, image_path, player_dict=None):
        """Displays the newly generated face in the Live Preview card."""
        self.root.after(0, self._safe_show_latest_face, image_path, player_dict)

    def _safe_show_latest_face(self, image_path, player_dict):
        if not image_path or not os.path.isfile(image_path):
            return
        try:
            self.current_preview_path = image_path
            photo = None
            if HAS_PIL_TK and ImageTk is not None and Image is not None:
                im = Image.open(image_path)
                im.thumbnail((210, 270), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(im)
            else:
                photo = tk.PhotoImage(file=image_path)

            if photo:
                self._preview_image_ref = photo
                self.preview_lbl.configure(image=photo, text="")
                self.btn_view_full.configure(state="normal")

            if player_dict:
                name = player_dict.get("name", "Unknown Player")
                uid = player_dict.get("uid", "—")
                age = player_dict.get("age", "—")
                nat = player_dict.get("nat", "—")
                self.lbl_player_name.configure(text=f"Player: {name}")
                self.lbl_player_sub.configure(text=f"UID: {uid} | Age: {age} | Nat: {nat}")
            else:
                uid_cand = os.path.splitext(os.path.basename(image_path))[0].replace("r-", "")
                self.lbl_player_name.configure(text=f"Player UID: {uid_cand}")
                self.lbl_player_sub.configure(text=f"File: {os.path.basename(image_path)}")
        except Exception as e:
            self.log(f"[Warning] Could not render live preview: {e}")

    # -------------------------------------------------------------------------
    # ACTION CONTROLS & EVENT TRIGGERS
    # -------------------------------------------------------------------------
    def _toggle_watcher(self):
        if self.watcher_running:
            if self.stop_callback:
                self.stop_callback()
            self.watcher_running = False
            self.btn_watcher.configure(
                text="⚡ Auto-Watcher: OFF\n(Click to Enable)",
                bg=self.bg_input, fg=self.fg_muted, highlightbackground=self.border_subtle
            )
            self.stat_box_state.configure(text="Idle", fg=self.fg_muted)
            self.log("[Watcher] Auto-watcher stopped.")
        else:
            if self.start_callback:
                self.start_callback(self.watch_path_var.get(), self.graphics_path_var.get())
            self.watcher_running = True
            self.btn_watcher.configure(
                text="⚡ Auto-Watcher: ACTIVE\n(Watching for Exports)",
                bg=self.bg_elevated, fg=self.color_active, highlightbackground=self.color_active
            )
            self.stat_box_state.configure(text="Watching", fg=self.color_active)
            self.log("[Watcher] Auto-watcher active.")

    def _run_now(self):
        if self.is_generating:
            return
        watch_dir = self.watch_path_var.get()
        graphics_dir = self.graphics_path_var.get()
        if not os.path.exists(watch_dir):
            messagebox.showerror("Error", f"Watch directory does not exist:\n{watch_dir}")
            return
        threading.Thread(target=self._execute_run_now, args=(watch_dir, graphics_dir), daemon=True).start()

    def _execute_run_now(self, watch_dir, graphics_dir):
        if self.run_now_callback:
            self.run_now_callback(watch_dir, graphics_dir)

    def _cancel_batch(self):
        if self.cancel_callback:
            self.cancel_callback()
        self.btn_cancel.configure(state="disabled", text="Cancelling...")

    def _generate_test_face(self):
        if not self.test_face_callback:
            self.log("[Info] Test face generator is not available.")
            return

        self.btn_test_face.configure(state="disabled", text="⏳ Generating...")
        self.log("[Test Face] Generating sample test newgen portrait...")

        def _work():
            path, err = self.test_face_callback(self.graphics_path_var.get())
            self.root.after(0, _done, path, err)

        def _done(path, err):
            self.btn_test_face.configure(state="normal", text="⚡ Test Face")
            if err:
                self.log(f"[Error] Test face generation failed: {err}")
                messagebox.showerror("Test Face Failed", f"Could not generate test face:\n{err}")
                return
            if path and os.path.exists(path):
                self.show_latest_face(path, {
                    "name": "Sample Test Newgen",
                    "uid": "2100000001",
                    "age": "18",
                    "nat": "FRA"
                })
                self._show_test_face_preview(path)

        threading.Thread(target=_work, daemon=True).start()

    def _show_test_face_preview(self, path):
        win = tk.Toplevel(self.root)
        win.title("Generated Face Preview")
        win.configure(bg=self.bg_dark)
        win.geometry("440x560")
        win.resizable(False, False)

        tk.Label(win, text="Generated Newgen Face", font=self.font_header,
                 fg=self.fg_light, bg=self.bg_dark).pack(pady=(14, 4))

        try:
            photo = None
            if HAS_PIL_TK and ImageTk is not None and Image is not None:
                im = Image.open(path)
                im.thumbnail((360, 460), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(im)
            else:
                photo = tk.PhotoImage(file=path)
            if photo:
                img_lbl = tk.Label(win, image=photo, bg=self.bg_dark)
                img_lbl.image = photo
                img_lbl.pack(pady=10)
        except Exception:
            tk.Label(win, text=f"[Preview Available: {path}]", fg=self.fg_muted, bg=self.bg_dark).pack(pady=40)

        btn_row = tk.Frame(win, bg=self.bg_dark)
        btn_row.pack(fill="x", padx=20, pady=10)

        def _open_folder():
            f_dir = os.path.dirname(path)
            if sys.platform.startswith("win"):
                os.startfile(f_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", f_dir])
            else:
                subprocess.Popen(["xdg-open", f_dir])

        tk.Button(btn_row, text="Open in Folder", font=self.font_body_bold,
                  bg=self.color_accent, fg=self.fg_light, bd=0, padx=14, pady=6,
                  cursor="hand2", command=_open_folder).pack(side="left")

        tk.Button(btn_row, text="Close", font=self.font_body,
                  bg=self.bg_input, fg=self.fg_muted, bd=0, padx=14, pady=6,
                  cursor="hand2", command=win.destroy).pack(side="right")

    def _view_full_preview(self):
        if self.current_preview_path and os.path.exists(self.current_preview_path):
            self._show_test_face_preview(self.current_preview_path)

    def _check_provider(self):
        if self.check_provider_callback:
            self.provider_pill.configure(text="● Checking...", fg=self.color_warning)
            threading.Thread(target=self.check_provider_callback, daemon=True).start()

    def _clear_log(self):
        self.console.delete("1.0", "end")

    def _copy_log(self):
        content = self.console.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.log("[Action] Console log copied to clipboard.")

    # -------------------------------------------------------------------------
    # TUNING & FACE STYLE DIALOG (DESKTOP-APP.md Inspector)
    # -------------------------------------------------------------------------
    def _open_tuning_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Generation Settings & Face Style Prompts")
        win.configure(bg=self.bg_dark)
        win.geometry("740x620")
        win.minsize(680, 560)

        # Tabbed Notebook
        tabs = ttk.Notebook(win, style="Custom.TNotebook")
        tabs.pack(fill="both", expand=True, padx=16, pady=(16, 10))

        # Tab 1: Prompts & Face Style
        tab_prompts = tk.Frame(tabs, bg=self.bg_dark)
        tabs.add(tab_prompts, text="🎨 Face Style Prompts")

        pos_prompt = ""
        neg_prompt = ""
        def_pos = ""
        def_neg = ""
        if self.face_style_callback:
            data = self.face_style_callback("get")
            if data:
                pos_prompt, neg_prompt, def_pos, def_neg = data

        tk.Label(tab_prompts, text="Positive Prompt Template", font=self.font_header,
                 fg=self.fg_light, bg=self.bg_dark).pack(anchor="w", padx=12, pady=(12, 2))
        tk.Label(tab_prompts, text="Dynamic tokens: [AGE], [NATIONALITY], and [PERSONALITY] are replaced for each player automatically.",
                 font=self.font_small, fg=self.fg_muted, bg=self.bg_dark).pack(anchor="w", padx=12, pady=(0, 6))

        txt_pos = tk.Text(tab_prompts, height=7, wrap="word", font=self.font_mono,
                          bg=self.bg_input, fg=self.fg_light, insertbackground=self.fg_light,
                          bd=0, highlightthickness=1, highlightbackground=self.border_subtle,
                          highlightcolor=self.border_focus, padx=8, pady=6)
        txt_pos.pack(fill="x", padx=12)
        txt_pos.insert("1.0", pos_prompt)

        tk.Label(tab_prompts, text="Negative Prompt (Artifacts to Avoid)", font=self.font_header,
                 fg=self.fg_light, bg=self.bg_dark).pack(anchor="w", padx=12, pady=(12, 2))
        txt_neg = tk.Text(tab_prompts, height=5, wrap="word", font=self.font_mono,
                          bg=self.bg_input, fg=self.fg_light, insertbackground=self.fg_light,
                          bd=0, highlightthickness=1, highlightbackground=self.border_subtle,
                          highlightcolor=self.border_focus, padx=8, pady=6)
        txt_neg.pack(fill="x", padx=12)
        txt_neg.insert("1.0", neg_prompt)

        # Tab 2: ComfyUI Engine Tuning
        tab_engine = tk.Frame(tabs, bg=self.bg_dark)
        tabs.add(tab_engine, text="⚙️ SDXL Engine Tuning")

        grid_f = tk.Frame(tab_engine, bg=self.bg_dark)
        grid_f.pack(fill="x", padx=12, pady=16)

        def _param_row(parent, row, label, var, widget_type="spin", values=None, from_=1, to_=100, inc=1):
            tk.Label(parent, text=label, font=self.font_body, fg=self.fg_muted, bg=self.bg_dark).grid(row=row, column=0, sticky="w", pady=6)
            if widget_type == "spin":
                w = tk.Spinbox(parent, from_=from_, to=to_, increment=inc, textvariable=var, width=12,
                               font=self.font_body, bg=self.bg_input, fg=self.fg_light,
                               insertbackground=self.fg_light, bd=0, highlightthickness=1,
                               highlightbackground=self.border_subtle, highlightcolor=self.border_focus)
            elif widget_type == "combo":
                w = ttk.Combobox(parent, textvariable=var, values=values, state="readonly", width=14,
                                 style="Custom.TCombobox", font=self.font_body)
            elif widget_type == "entry":
                w = tk.Entry(parent, textvariable=var, width=28, font=self.font_body,
                             bg=self.bg_input, fg=self.fg_light, insertbackground=self.fg_light,
                             bd=0, highlightthickness=1, highlightbackground=self.border_subtle,
                             highlightcolor=self.border_focus)
            w.grid(row=row, column=1, sticky="w", padx=(12, 0), pady=6)
            return w

        _param_row(grid_f, 0, "ComfyUI Server URL:", self.comfy_url_var, widget_type="entry")
        _param_row(grid_f, 1, "Sampling Steps (Quality):", self.steps_var, from_=10, to_=60, inc=1)
        _param_row(grid_f, 2, "CFG Guidance Scale:", self.cfg_var, from_=1.0, to_=20.0, inc=0.5)
        _param_row(grid_f, 3, "Sampler Algorithm:", self.sampler_var, widget_type="combo",
                   values=["euler_a", "euler", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_sde", "lms", "heun", "ddim"])
        _param_row(grid_f, 4, "Scheduler:", self.scheduler_var, widget_type="combo",
                   values=["karras", "normal", "simple", "ddim_uniform", "sgm_uniform", "beta"])
        _param_row(grid_f, 5, "Resolution Width (px):", self.width_var, from_=512, to_=1536, inc=64)
        _param_row(grid_f, 6, "Resolution Height (px):", self.height_var, from_=512, to_=1536, inc=64)
        _param_row(grid_f, 7, "Max Concurrency (Batches):", self.concurrency_var, from_=1, to_=4, inc=1)

        # Action Buttons Row
        btn_bar = tk.Frame(win, bg=self.bg_dark)
        btn_bar.pack(fill="x", padx=16, pady=12)

        def _save_all():
            if self.face_style_callback:
                p = txt_pos.get("1.0", "end-1c").strip()
                n = txt_neg.get("1.0", "end-1c").strip()
                if not p:
                    messagebox.showwarning("Empty Style", "The positive prompt cannot be empty.")
                    return
                self.face_style_callback("save", p, n)
            self._save_settings()
            win.destroy()
            self.log("[Info] Tuning parameters and face style saved successfully.")

        def _reset_prompts():
            txt_pos.delete("1.0", "end")
            txt_pos.insert("1.0", def_pos)
            txt_neg.delete("1.0", "end")
            txt_neg.insert("1.0", def_neg)

        tk.Button(btn_bar, text="💾 Save Configuration", font=self.font_body_bold,
                  bg=self.color_accent, fg=self.fg_light, activebackground=self.color_accent_hover,
                  activeforeground=self.fg_light, bd=0, padx=16, pady=6,
                  cursor="hand2", command=_save_all).pack(side="left")

        tk.Button(btn_bar, text="Reset Prompts", font=self.font_body,
                  bg=self.bg_input, fg=self.fg_muted, activebackground=self.bg_elevated,
                  activeforeground=self.fg_light, bd=0, padx=12, pady=6,
                  cursor="hand2", command=_reset_prompts).pack(side="left", padx=(10, 0))

        tk.Button(btn_bar, text="Close", font=self.font_body,
                  bg=self.bg_input, fg=self.fg_muted, activebackground=self.bg_elevated,
                  activeforeground=self.fg_light, bd=0, padx=14, pady=6,
                  cursor="hand2", command=win.destroy).pack(side="right")

    # -------------------------------------------------------------------------
    # DIALOGS: MAINTENANCE & FM26 HELPERS
    # -------------------------------------------------------------------------
    def _open_maintenance(self):
        if self.maintenance_callback:
            self.maintenance_callback()
        else:
            self.log("[Info] Maintenance is only available in the packaged app.")

    def _open_fm26_setup(self):
        if not self.fm26_callback:
            self.log("[Info] FM26 setup helper is not available in this build.")
            return

        win = tk.Toplevel(self.root)
        win.title("FM26 Support (free export plugin)")
        win.configure(bg=self.bg_dark)
        win.geometry("660x480")
        win.minsize(600, 440)

        tk.Label(win, text="Playing Football Manager 2026?", font=self.font_header,
                 fg=self.fg_light, bg=self.bg_dark).pack(anchor="w", padx=20, pady=(16, 4))
        tk.Label(win, text="FM26 removed the classic 'To text file' export. The free "
                           "FM26 Player Export plugin (by vinteset) restores it — the app "
                           "reads its CSV/HTML output directly, so everything else works "
                           "exactly like FM24.",
                 font=self.font_body, fg=self.fg_muted, bg=self.bg_dark, justify="left",
                 wraplength=600).pack(anchor="w", padx=20, pady=(0, 10))

        steps = (
            "1. Install BepInEx 6 (Unity IL2CPP) into the FM26 game folder first.\n"
            "2. Download the FM26 Player Export plugin from FM Scout.\n"
            "3. Copy FM26PlayerExport.dll into:  BepInEx\\plugins\\FM26PlayerExport\\\n"
            "4. Launch FM26, add the ID column to your Player Search view, press F9.\n"
            "5. Back here: set the Watch Directory to the plugin's output folder."
        )
        tk.Label(win, text=steps, font=self.font_mono, fg=self.fg_light, bg=self.bg_input,
                 justify="left", anchor="w", padx=14, pady=12).pack(fill="x", padx=20)

        btn_row = tk.Frame(win, bg=self.bg_dark)
        btn_row.pack(fill="x", padx=20, pady=16)
        tk.Button(btn_row, text="Open plugin page", font=self.font_body_bold,
                  bg=self.color_accent, fg=self.fg_light, bd=0, padx=16, pady=6,
                  cursor="hand2", command=lambda: self.fm26_callback("page")).pack(side="left")
        tk.Button(btn_row, text="Set Watch Directory to plugin output", font=self.font_body,
                  bg=self.bg_input, fg=self.fg_light, bd=0, padx=14, pady=6,
                  cursor="hand2", command=lambda: self.fm26_callback("watch")).pack(side="left", padx=(10, 0))
        tk.Button(btn_row, text="Close", font=self.font_body, bg=self.bg_input,
                  fg=self.fg_muted, bd=0, padx=14, pady=6, cursor="hand2", command=win.destroy).pack(side="right")

    # -------------------------------------------------------------------------
    # CONFIGURATION SERIALIZATION
    # -------------------------------------------------------------------------
    def _save_settings(self):
        if self.save_config_callback:
            tuning = {
                "steps": self.steps_var.get(),
                "cfg": self.cfg_var.get(),
                "sampler": self.sampler_var.get(),
                "scheduler": self.scheduler_var.get(),
                "width": self.width_var.get(),
                "height": self.height_var.get(),
                "concurrency": self.concurrency_var.get(),
            }
            self.save_config_callback(
                self.watch_path_var.get(),
                self.graphics_path_var.get(),
                self.auto_reload_var.get(),
                "comfyui",
                self.comfy_url_var.get(),
                tuning=tuning,
                show_advanced=self.show_advanced_var.get()
            )

    def load_config(self, watch_dir, graphics_dir, auto_reload, provider="comfyui",
                    comfyui_base_url="http://127.0.0.1:8188",
                    steps=25, cfg=6.0, sampler="euler_a", scheduler="karras",
                    width=896, height=1152, concurrency_limit=1,
                    show_advanced=False):
        self.watch_path_var.set(watch_dir or "./exports")
        self.graphics_path_var.set(graphics_dir or "./graphics/AI Newgen Faces")
        self.auto_reload_var.set(auto_reload or False)
        self.comfy_url_var.set(comfyui_base_url or "http://127.0.0.1:8188")
        self.steps_var.set(steps if steps else 25)
        self.cfg_var.set(cfg if cfg else 6.0)
        self.sampler_var.set(sampler if sampler else "euler_a")
        self.scheduler_var.set(scheduler if scheduler else "karras")
        self.width_var.set(width if width else 896)
        self.height_var.set(height if height else 1152)
        self.concurrency_var.set(concurrency_limit if concurrency_limit else 1)
        self.show_advanced_var.set(show_advanced or False)
