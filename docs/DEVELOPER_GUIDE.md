# FM AI Newgen Generator — Developer & AI Agent Guide

This document is a complete technical guide and architectural blueprint for the Football Manager AI Newgen Generator project. It explains each phase of the application pipeline in enough detail that any developer (human or AI agent) can understand, maintain, or extend the codebase without prior context.

---

## 🏗️ System Overview & Pipeline

The application runs as a Python Tkinter desktop GUI that coordinates a background file-watching thread and an asynchronous generation loop. The core flow operates as follows:

```mermaid
graph TD
    A0[FMNewgenGenerator.exe / main.py] --> W{Embedded ComfyUI installed?}
    W -->|No (first run)| S[SetupWizard: src/setup_wizard.py]
    S -->|Downloads ComfyUI + RealVisXL, writes config.json| A
    W -->|Yes| A[Football Manager: Ctrl + P Print to text]
    A -->|Saves file in exports/| B[ExportWatcher: src/watcher.py]
    B -->|Triggers event on new .rtf| C[PlayerParser: src/parser.py]
    C -->|Extracts players list + prompts| D[FMGeneratorApp: src/app.py]
    D -->|Pre-flight connection check| E{ComfyUI Online?}
    E -->|Yes| F[FaceGenerator: src/generator.py]
    E -->|No| G[Queue failed to failed_downloads.json]
    F -->|Derives seed from UID & builds SDXL JSON| H[Local ComfyUI API :8188]
    H -->|Generates face at 896x1152| I[Save image to graphics folder]
    I -->|Update mappings| J[XMLManager: src/xml_manager.py]
    J -->|Generates config.xml| K[Football Manager reloads skin]
```

---

## 📁 Core Codebase Layout

*   `run_all.bat`: One-click launcher. Starts the local ComfyUI server, waits for `/system_stats` to respond, then launches the GUI.
*   `main.py`: **Unified entry point.** Runs the first-run Setup Wizard when no embedded ComfyUI install exists, otherwise opens the generator directly.
*   `src/app.py`: Main coordinator. Loads/saves `config.json`, wires watcher events into the generation loop, manages threads and the failure queue, and auto-starts an embedded ComfyUI if one was installed.
*   `src/ui.py`: Tkinter GUI. Dark-themed panels, logging scroller, stats trackers, provider dropdown, ComfyUI URL field, and a "Test Connection" button.
*   `src/setup_wizard.py`: **First-run installer.** Downloads portable ComfyUI (~2 GB) and the RealVisXL checkpoint (~7 GB) with a resumable progress UI, extracts them, writes `config.json`, and hands off to the app.
*   `src/watcher.py`: File monitoring wrapper using `watchdog` that alerts the pipeline when new exports are dropped.
*   `src/parser.py`: RTF/HTML data scraper and prompt-building engine (demographics presets + dynamic framing prompts).
*   `src/generator.py`: Talks to ComfyUI's JSON API — builds SDXL workflows, submits them, polls `/history`, downloads PNGs.
*   `src/xml_manager.py`: Regex-based parser and strict string-writer for Football Manager's `config.xml` format.
*   `config.json`: Runtime settings (gitignored).
*   `config.example.json`: Public template. Safe to commit; contains no secrets.
*   `verify_tool.py`: Standalone CLI smoke-test that uses the configured provider to generate one face end-to-end.
*   `build/FMNewgenGenerator.spec` + `build.bat`: PyInstaller build configuration + Windows build script.
*   `.github/workflows/build-exe.yml`: CI that builds the Windows EXE on every `v*` tag and attaches it to a GitHub Release.
*   `site/`: Static landing + download page.
*   `docs/DEVELOPER_GUIDE.md`: This document.

---

## 🛠️ Step-by-Step Pipeline Breakdown

### Phase 1: File Monitoring (`src/watcher.py`)

*   **Purpose:** Watches the configured `watch_directory` (default `./exports`) for files printed from Football Manager.
*   **Mechanism:** `watchdog.observers.Observer` schedules an `ExportFileHandler` (a `PatternMatchingEventHandler`).
*   **Rules:**
    1.  Patterns `*.rtf`, `*.html`, `*.htm`, `*.txt`; directories ignored.
    2.  `on_created` **and** `on_modified` both fire, giving robustness against how FM writes files.
    3.  De-duplication: files re-triggered within 2 seconds are ignored.
    4.  Debounce: sleeps 1.5 s before calling the callback so FM has finished writing the file (FM writes in chunks).

### Phase 2: Data Scraping & Demographics (`src/parser.py`)

*   **Purpose:** Turns the raw RTF export into a list of player dictionaries and later builds the AI prompt for each one.
*   **Mechanism:**
    1.  Detects type by extension; uses `striprtf` to strip RTF styling syntax.
    2.  Regex-scans rows, locates column indexes from headers (`ID`, `Age`, `Nat`, `Personality`).
    3.  Filters to UIDs starting with `2` — the standard prefix for FM generated players.
*   **Demographic Mapping:** `DEMOGRAPHIC_WEIGHTS` + `REGIONAL_PRESETS` roll a weighted ethnicity per nationality (e.g. France → 70% Western Europe / 20% African / 10% North African), so generated faces reflect each country's real academy demographics. The chosen preset feeds hair/skin descriptors into the prompt.

### Phase 3: Dynamic Prompt Building & Framing (`src/parser.py`)

*   **Purpose:** Builds SDXL-friendly natural-language prompts from the `face_style` template in `config.json`.
*   **Template placeholders:** `[AGE]`, `[NATIONALITY]`, `[PERSONALITY]` are substituted per player.
*   **Framing / zoom-out fix:** The template forces a **bust shot** with headroom so the player's head does not fill the whole frame in FM's UI (previously faces hid club kit numbers behind the portrait):
    > `"candid smartphone camera snapshot medium shot bust portrait of a [AGE]-year-old male [NATIONALITY] football player, [PERSONALITY], head and shoulders, showing upper chest, athletic training shirt, natural lighting, unpolished raw photo, visible skin texture, blurred background, real life photo"`
*   **Age milestones** (per-UID age progression; faces stay consistent because the UID seeds the image):
    *   *Under 20:* swaps `"male"` → `"teenage male"`, `"football player"` → `"youth academy soccer player"`, and appends `"soft youthful facial features, smooth skin"` to avoid adult-looking regens.
    *   *Milestone ~20:* high beard/stubble density for South American and Middle Eastern players.
    *   *Milestones 24 & 28:* fully developed beards / mature styling.

### Phase 4: Resolution, Framing & Aspect Ratio (recommended: **896×1152**)

*   **Why it matters:** Two independent levers control how big a player looks in the final portrait: (a) the **prompt framing** (Phase 3) and (b) the **output resolution / aspect ratio** (this phase). Resolution alone does NOT shrink the subject — aspect ratio and framing do.
*   **SDXL native buckets (SDXL was trained at ~1 megapixel).** Staying near 1 MP yields the cleanest, most stable images. Recommended presets:
    | Aspect | Size | Use case |
    |---|---|---|
    | 1:1 square | 1024×1024 | Default; neutral |
    | 2:3 portrait | 832×1216 | Classic vertical character portrait |
    | **7:9 portrait** | **896×1152** | **Best for bust / head-and-shoulders — extra shoulder room. This project's default.** |
    | 3:2 landscape | 1216×832 | Scenic / wide shots |
    *   Going much higher (e.g. 1536×1536+) needs 16 GB+ VRAM and often *degrades* quality. Avoid on the 8 GB RTX 2060 Super — do not chase bigger numbers; SDXL does not gain detail past ~1 MP.
*   **Why portrait matches FM:** community facepacks use vertical images (e.g. DF11 uses 260×310). FM scales images to the skin's portrait box, so a portrait aspect gives the subject less vertical dominance and keeps the kit number / surrounding UI visible.
*   **Where it's configured:** `config.json` → `comfyui_width` (896) and `comfyui_height` (1152). The GUI reads these into `FaceGenerator`, which writes them into the `EmptyLatentImage` node of the SDXL workflow (`src/generator.py` `build_sdxl_workflow`). A single `comfyui_size` value (square) is no longer used.

### Phase 5: Local ComfyUI API Execution (`src/generator.py`)

*   **Purpose:** Dispatches each prompt to a local ComfyUI server at `http://127.0.0.1:8188`.
*   **Mechanism:**
    1.  **Pre-flight ping:** GET `/system_stats` — if unreachable, the whole batch is aborted and players are queued in `failed_downloads.json` (rather than failing one-by-one).
    2.  **Checkpoint resolution:** if `comfyui_model` is empty, GET `/object_info/CheckpointLoaderSimple` and auto-pick the first checkpoint found. Resolved once per batch.
    3.  **Workflow construction:** minimal single-image SDXL graph — nodes `4` CheckpointLoaderSimple, `5` EmptyLatentImage (width/height from Phase 4), `6`/`7` CLIPTextEncode (pos/neg), `3` KSampler, `8` VAEDecode, `9` SaveImage. Seed = `UID % 2^32` so each player keeps a stable face across age milestones.
    4.  **Batch settings:** steps (25), cfg (6.0), sampler `euler_a`, scheduler `karras` — all tunable in `config.json`.
    5.  **Async submission:** POST `/prompt`, capture `prompt_id`.
    6.  **History polling:** GET `/history/{prompt_id}` every 2 s, up to 150 polls (5-minute cap) to guard against hung jobs.
    7.  **Download:** on `status_str == "success"`, collect the first image from the SaveImage output, fetch it from `/view?filename=...`, and save as `{UID}.png` in the graphics folder. `status_str == "error"` surfaces the ComfyUI diagnostic message.

### Phase 6: XML Graphics Bind (`src/xml_manager.py`)

*   **Purpose:** Links each saved `.png` to Football Manager's virtual graphics index.
*   **XML Rules:**
    1.  Each record must use the FM24-mandated `r-` prefix in the `to` target:
        `<record from="{filename}" to="graphics/pictures/person/r-{UID}/portrait"/>`
    2.  Output must use lowercase tags (`record`, `list`, `boolean`), the `preload=false` / `amap=false` header, and comment separators so the game parses it.
    3.  Regex-based reading of the existing `config.xml` preserves any previously existing facepack mappings instead of clobbering them.
    4.  When FM exports a new batch, only *missing* UIDs generate new faces; existing faces and their XML entries are kept.

---

## ⚙️ Provider Configuration

| Setting | Default | Meaning |
|---|---|---|
| `provider` | `comfyui` | The only provider (local SDXL) |
| `comfyui_base_url` | `http://127.0.0.1:8188` | Where ComfyUI listens |
| `comfyui_model` | `""` | Force a specific `.safetensors`; empty = auto-detect first checkpoint |
| `comfyui_negative_prompt` | (see config) | Negative prompt for SDXL |
| `comfyui_steps` | `25` | Sampling steps |
| `comfyui_cfg` | `6.0` | Classifier-free guidance scale |
| `comfyui_sampler` | `euler_a` | Sampler name |
| `comfyui_scheduler` | `karras` | Scheduler |
| `comfyui_width` / `comfyui_height` | `896` / `1152` | Output size (see Phase 4) |
| `comfyui_install_dir` | *(set by wizard)* | Path to the embedded ComfyUI portable folder, used for auto-start |

The GUI's **"Test Connection"** button runs the same pre-flight check the generator uses, from a background thread so the UI stays responsive.

---

## 🕹️ Instructions for Running & Testing

1.  **Install ComfyUI** with your SDXL checkpoint in:
    `ComfyUI\ComfyUI\models\checkpoints\{your-sdxl}.safetensors`
    (e.g. `Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors`).
2.  **Sync local config:** copy `config.example.json` → `config.json` and review settings (width/height, steps, negative prompt).
3.  **Launch:** double-click `run_all.bat`. It starts ComfyUI, waits for it to come online, then opens the GUI.
4.  **In-game:** open FM preferences → **disable image caching** (Advanced → Interface → Skin) → **Clear Cache** → **Reload Skin**.
5.  **Export faces:** in FM, the game's "print to text" action writes an `.rtf` into `exports/`; the watcher picks it up and the pipeline runs.
6.  **Smoke-test standalone:** `python verify_tool.py` uses the configured provider to generate one face and prints the result.

---

## 🧹 Troubleshooting

*   **"ComfyUI server NOT reachable"** → start ComfyUI / check `comfyui_base_url` / firewall for port 8188.
*   **"ComfyUI rejected request (HTTP 400)"** → workflow returned by the server contains the validation error; read the returned message. Common cause: no checkpoint installed.
*   **Generation timeout (>5 min)** → usually a hung job or extremely slow render. Lower steps, or reduce concurrency.
*   **Faces look mushy / duplicate faces** → resolution too far from an SDXL native bucket (keep near 1 MP), or far too high (1536+).
*   **Player still covers the kit number** → weaken the framing (Phase 3) and/or switch to a taller portrait bucket (Phase 4).
*   **VRAM pressure (8 GB RTX 2060 Super)** → single-image workflows at ~1 MP fit comfortably (~5–15 s/face). FM itself is CPU-bound, so concurrent generation won't hurt the game. If you hit OOM, reduce to 768×1024-equivalent and lower steps.
*   **Existing faces keep reappearing** → FM skin caching; re-disable cache and reload skin after each export.

---

## 🔐 Security & Licensing Notes

*   `config.json` is **gitignored** — never commit it.
*   `config.example.json` is the public-safe template and should contain only placeholders / empty values.
*   The git remote URL must not embed a personal access token (`https://TOKEN@github.com/...`). Use a clean HTTPS URL and let your credential manager/SSH authenticate.
*   RealVisXL V5.0 is licensed under **CreativeML Open RAIL++-M** (redistribution permitted with conditions). The wizard provisions it from the creator's official Hugging Face repo rather than shipping weights in the repo.
*   SDXL checkpoints are generally permissive for personal use — verify the license of any downloaded `.safetensors` if you plan to redistribute output.

---

## 🧩 Extending the System

*   **New provider:** add a `download_face_{provider}` method in `src/generator.py`, register it in `PROVIDER_NAMES`, and add config keys.
*   **New aspect bucket:** change `comfyui_width`/`comfyui_height` and validate against SDXL's native buckets (~1 MP total).
*   **New face style:** edit `face_style` in `config.json`; placeholders `[AGE]`, `[NATIONALITY]`, `[PERSONALITY]` are populated automatically.
*   **Upscaling (advanced):** for higher-resolution output, generate at a native bucket then run an external upscaler (e.g. ComfyUI's UpscaleModelLoader + ImageUpscaleWithModel) rather than raising the raw generation size.

---

## 📦 Distribution: EXE + Setup Wizard + Website

### Phase 7: First-Run Setup Wizard (`src/setup_wizard.py`)

*   **Purpose:** Makes the Windows EXE self-installing — a non-technical FM player downloads one small EXE and gets a working offline generator.
*   **Flow (runs from `main.py` only when no install exists):**
    1.  `setup_wizard_needed()`: true when there is no `config.json` with a valid `comfyui_install_dir`, no install marker, and this is not a source checkout (a `src/` folder beside the entry point counts as dev mode and skips the wizard).
    2.  **System check:** `detect_nvidia_gpu()` (via `nvidia-smi`) and `free_disk_gb()` (~25 GB required). Non-NVIDIA machines get a CPU-mode warning but may continue.
    3.  **ComfyUI portable download** from `Comfy-Org/ComfyUI` releases/latest (`ComfyUI_windows_portable_nvidia.7z`, ~2 GB), streamed by `_download_file_async()`.
    4.  **Extract** with `py7zr` into `%LOCALAPPDATA%\FM Newgen Generator\ComfyUI_windows_portable\`.
    5.  **Checkpoint download** — RealVisXL V5.0 fp16 (`RealVisXL_V5.0_fp16.safetensors`, ~7 GB) from Hugging Face, into the same root.
    6.  **Write `config.json`** next to the EXE with correct defaults (watch/graphics dirs under the user's Documents, `comfyui_model` set, size 896×1152).
    7.  **Finish** → app launches; `app.auto_start_comfyui()` boots the embedded server if it isn't already reachable.
*   **Resume safety:** downloads write to a `.part` file and resume via HTTP `Range`; a failed transfer can be re-run without re-downloading the whole file.
*   **Redistribution notes:** the wizard downloads RealVisXL from its official Hugging Face repo (OpenRAIL++-M license). It is *provisioned*, not embedded in the repo, so the project itself ships no model weights.

### Phase 8: Packaging (PyInstaller)

*   `build/FMNewgenGenerator.spec` builds a single-file, windowed (no console) EXE from `main.py`.
*   `build/icon.ico` (generated by `build/make_icon.py`, committed to the repo) supplies the EXE icon. On Windows the icon is embedded; Linux/macOS smoke builds ignore it (expected).
*   `build.bat` runs it locally on Windows; `.github/workflows/build-exe.yml` runs the same build on a `windows-latest` runner whenever a `v*` tag is pushed and attaches the result to the GitHub Release (note: GitHub caps release assets at 2 GB per file — the EXE is well under this).
*   Path handling: `app_root()` in `src/app.py` resolves `config.json` and relative `watch_directory`/`graphics_directory` paths to the EXE's folder when frozen, so the app never depends on the launch working directory.

### Phase 9: Website (`site/`, `netlify.toml`)

*   Static single-page dark-themed landing page: features, requirements, install steps, FAQ, and a Download button.
*   Because the repo is **private**, the site is hosted on Netlify (free static host) rather than GitHub Pages. Config lives in `netlify.toml` (`publish = "site"`).
*   **The EXE is hosted ON the site itself**: `deploy.bat` copies `dist\FMNewgenGenerator.exe` → `site\download\FMNewgenGenerator.exe` before deploying, and the page's CTA points at `/download/FMNewgenGenerator.exe`. This works while the repo stays private. (Netlify free tier caps a single file at 512 MB — fine for the ~50–150 MB EXE.)
*   `netlify.toml` also defines `/latest → https://github.com/yi435/fm/releases/latest/download/FMNewgenGenerator.exe` so the download URL works unchanged if the repo is later made public.
*   Deploy with `deploy.bat` (Netlify CLI: `npm i -g netlify-cli`, `netlify login`, then `deploy.bat`).