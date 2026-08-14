# Football Manager 2024 AI Newgen Face Generator

A performance-friendly, cross-platform Desktop GUI tool designed to automatically generate high-quality, photorealistic AI portraits for your generated youth players (newgens/regens) in **Football Manager 2024**.

> **For most Windows users:** grab the **FMNewgenGenerator.exe** installer from the [website](https://github.com/yi435/fm) / GitHub Releases. On first run it auto-downloads local ComfyUI (~2 GB) and the RealVisXL realism model (~7 GB) with a progress bar, then sets everything up for you — free, unlimited and offline.

**Face generation is powered by your local GPU:**

| Provider | Cost | Quality | Requirements |
|----------|------|---------|--------------|
| **Local ComfyUI (SDXL)** ⭐ | Free, unlimited, offline | Excellent & fully offline | ComfyUI + a realism checkpoint (~7GB), 6-8GB VRAM GPU |

> A "Test Connection" button verifies your local ComfyUI server is reachable.

---

## 📦 Installing from the EXE (Windows, recommended)

1. Download `FMNewgenGenerator.exe` from the [releases page](https://github.com/yi435/fm/releases).
2. Run it. A **Setup Wizard** opens: it checks your system, downloads the AI engine + model (resumable, with a progress bar), installs them under `%LOCALAPPDATA%\FM Newgen Generator\`, writes a ready-to-use `config.json` beside the EXE, then launches the app.
3. In the app, point **Watch Directory** and **Graphics Directory** at your FM folders (see *Setting Up Football Manager 2024* below), then **Start Watcher**.

> The EXE is a self-contained GUI. On later launches it skips the wizard and auto-starts the embedded ComfyUI server for you.

---

## 🚀 One-Click Launcher (Windows)

We have provided a unified script [run_all.bat](file:///home/zakariae/Documents/zed%20projet/run_all.bat) in the project directory that:
1. Automatically starts your **ComfyUI Server** in a minimized background window.
2. Waits 5 seconds for it to boot.
3. Automatically launches the **FM AI Newgen Generator App**.

> [!TIP]
> Just double-click **`run_all.bat`** in your project folder to start everything instantly! *(If you ever move your ComfyUI installation, you can open `run_all.bat` in Notepad and update the folder path).*

---

## ⚡ Quick Start — Local ComfyUI (Recommended, Free)

This generates unlimited photorealistic faces, offline, on your own GPU. No API keys, no credits, no rate limits.

> [!IMPORTANT]
> **CRITICAL: ComfyUI Portable Folder Structure**
> If you are using the **ComfyUI Windows Portable** package, your directories are nested:
> 1. You have a parent folder (e.g., `%USERPROFILE%\ComfyUI\`) containing your startup scripts (`run_nvidia_gpu.bat`).
> 2. Inside it, there is a nested folder also called `ComfyUI` (e.g., `%USERPROFILE%\ComfyUI\ComfyUI\`).
> 3. Your checkpoints **MUST** be placed in the **inner nested folder**:
>    `%USERPROFILE%\ComfyUI\ComfyUI\models\checkpoints\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors`
> 
> *(If you place models in the outer `%USERPROFILE%\ComfyUI\models\checkpoints\` directory, ComfyUI will not see them, and your face generation will fail with an empty `[]` list error).*

### 1. Install ComfyUI (Windows, one time, ~2GB)

1. Install **Python 3.10+** and **Git** if you don't have them.
2. Open Command Prompt or PowerShell and follow the [official ComfyUI install guide](https://docs.comfy.org/):
   ```cmd
   git clone https://github.com/comfyanonymous/ComfyUI.git
   cd ComfyUI
   python -m venv venv
   venv\Scripts\activate.bat
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   pip install -r requirements.txt
   ```

### 2. Download a realistic face checkpoint (~7GB, one time)

Place the model file in `ComfyUI\models\checkpoints\`. Recommended SDXL realism models for faces:

- **Juggernaut XL (v9)** — `https://huggingface.co/RunDiffusion/Juggernaut-XL-v9` (best overall photo realism)
- **RealVisXL V4 / V5** — `https://huggingface.co/SG161222/RealVisXL_V4.0`
- Or **DreamShaper XL** — `https://huggingface.co/Lykon/dreamshaper-xl-v2-turbo`

The app auto-detects installed checkpoints. If you have several, set your favourite in `config.json`:
```json
"comfyui_model": "Juggernaut-XL-v9.safetensors"
```

### 3. Start ComfyUI

```cmd
venv\Scripts\activate.bat
python main.py
```

You should see `Starting server... To see the GUI go to: http://127.0.0.1:8188`. **Keep this window open** while generating faces. (The GUI tab is optional; the app only needs the API — no need to build a workflow yourself.)

### 4. Run this app

```cmd
python -m src.app
```

Select the **Local ComfyUI (SDXL)** provider, click **Test Connection** (should turn green), then press **Process Existing Files** or **Start Watcher**.

> **Tuning:** steps, CFG, sampler, scheduler, output size and concurrency are editable **in the app** under *Generation Settings* (they save to `config.json` automatically). Fewer steps (e.g. 12-15 with DreamShaper Turbo) = faster but slightly lower quality.

---

## Key Features

1. **Unlimited Offline Generation:** Local SDXL on your GPU — free forever, no quotas, no API keys, no credits.
2. **Milestone-Based Player Aging:** Unique ID seeds the generator so facial structure stays consistent, while hair length, stubble, and mature features update at age milestones **16, 20, 24, 28**.
3. **Visual Personality Mapping:** Player personalities map into the AI prompt (Model Citizen ≈ clean-shaven & neat; Temperamental ≈ stern with possible scar; Jovial ≈ warm smile, etc.).
4. **Weighted Demographics:** Multi-ethnic countries (France, England, Brazil, USA…) use demographic weight profiles to reflect real-life ratios.
5. **Real-Player Preservation:** Faces write to their own graphics directory and `config.xml`, leaving your real-player facepacks untouched.
6. **Auto Reload Skin:** On Windows, optionally triggers FM's skin reload hotkey (`Shift + R`) automatically.
7. **Install Maintenance:** The **Maintenance** button re-checks the AI engine and re-downloads any missing/corrupt pieces ("Repair") or removes the whole install ("Uninstall") — also available via `main.py --repair` / `main.py --uninstall`.

---

## Folder Structure

```
fm-newgen-generator/
├── main.py                # Unified entry point (wizard-or-app; --repair / --uninstall)
├── config.json            # Tool settings (paths, prompts, provider + ComfyUI tuning)
├── config.example.json    # Example configuration template (copy to config.json)
├── requirements.txt       # Python dependencies (watchdog, striprtf, aiohttp, pillow, py7zr)
├── README.md              # This guide
├── commit.sh / commit.bat # One-click GitHub commit helpers
├── build.bat              # Windows: build the EXE with PyInstaller
├── deploy.bat             # Deploy the website to Netlify
├── netlify.toml           # Netlify site config + /latest release redirect
├── build/
│   └── FMNewgenGenerator.spec  # PyInstaller build spec
├── .github/workflows/     # CI: build the EXE on Windows on every release tag
├── site/                  # Static landing + download page
├── verify_tool.py         # End-to-end mock verification (uses configured provider)
└── src/
    ├── app.py             # App orchestrator + hotkey triggers + provider check + ComfyUI autostart + maintenance
    ├── ui.py              # Dark-themed Tkinter GUI (provider selector included)
    ├── setup_wizard.py    # First-run installer (downloads ComfyUI + model, writes config)
    ├── watcher.py         # Background directory watcher
    ├── parser.py          # RTF/HTML player parser & demographic builder
    ├── generator.py       # Asynchronous face generator (ComfyUI backend)
    └── xml_manager.py     # config.xml reader/writer
```

---

## Installation & Running

### Prerequisites
- **Python 3.10+**
- For local quality: **ComfyUI** installed & running (see Quick Start) and a GPU with 6-8GB VRAM.

### 1. On Windows (Where you play the game)
```cmd
pip install -r requirements.txt
python -m src.app
```

### 2. On Linux (Fedora - Development)
```bash
pip install -r requirements.txt
python3 -m src.app
```

---

## 🛠️ Building the EXE (developers)

1. Install PyInstaller: `pip install pyinstaller`.
2. Windows: run `build.bat` (or `python -m PyInstaller --clean build/FMNewgenGenerator.spec`). The EXE icon (`build/icon.ico`) is embedded automatically; regenerate it with `python build/make_icon.py` if you redesign it.
3. Output: `dist/FMNewgenGenerator.exe`.
4. CI: pushing a `v*` tag triggers `.github/workflows/build-exe.yml`, which builds the EXE on a Windows runner and attaches it to a GitHub Release.
5. Website: `deploy.bat` copies the EXE into the site and deploys to Netlify (`netlify.toml`). The Download button then serves the EXE directly from the site — works even with the repo private. (`/latest` in `netlify.toml` covers the repo going public later.)

---

## Setting Up Football Manager 2024

> [!IMPORTANT]
> **CRITICAL: Football Manager Graphics Setup**
> For FM to recognize the generated faces, configure these game preferences:
> 1. **Preferences > Interface >** untick *"Use caching to decrease page loading times"*.
> 2. Tick *"Reload skin when confirming changes in Preferences"*.
> 3. Click **Clear Cache**, then **Reload Skin**.

### A. View & Filter Configuration
1. Obtain the custom view file (`SCRIPT FACES player search.fmf`) and filter file (`is newgen search filter.fmf`) — standard community files (e.g. from NewGAN Manager).
2. Place the view file in:
   - Windows: `Documents\Sports Interactive\Football Manager 2024\views\`
   - Linux: `~/.steam/steam/steamapps/compatdata/2252600/pfx/drive_c/users/steamuser/Documents/Sports Interactive/Football Manager 2024/views/`
3. Place the filter in the `filters/` folder in the same FM directory.

### B. Daily Gameplay Workflow
1. In the app UI, set your **Watch Directory** (e.g. a folder named `exports`) and **Graphics Directory** (e.g. `Documents\Sports Interactive\Football Manager 2024\graphics\AI Newgen Faces`).
2. Click **Start Watcher**.
3. In Football Manager: **Scouting > Player Search** → load the custom view & filter.
4. Select all players (`Ctrl + A`), press **`Ctrl + P`** → **To text file or web page**, save into your watch directory.
5. **The app takes over:** parses UIDs, generates faces for new/aged players (via your chosen provider), updates `config.xml`, and reloads the skin.
6. Press **`Shift + R`** manually in FM if auto-reload is off.

---

## Troubleshooting

### ComfyUI
- **"ComfyUI server NOT reachable"** → ComfyUI isn't running, or the URL in the UI/config differs from the server's port. Keep the ComfyUI terminal open while generating.
- **"Checkpoint may be missing"** → no checkpoint found. Download a model into `ComfyUI\models\checkpoints\`, or set `comfyui_model` in `config.json`.
- **Slow generation** → lower `comfyui_steps` (e.g. 15) or use DreamShaper Turbo. The RTX 2060 SUPER (8GB) generates SDXL faces in ~5-15s each.
- **Faces look different when aging** → the seed is bound to the UID. Do NOT touch the seed logic in `generator.py`, and keep the same checkpoint + settings.

### General
- **No faces generated:** Ensure the search view contains the **Unique ID (UID)** column. Players without a UID starting with `2` are skipped.
- **Skin doesn't reload:** In FM Preferences untick caching and tick "Reload skin when confirming changes" (see Critical setup above).