# Football Manager AI Newgen Face Generator

A performance-friendly Windows tool designed to automatically generate high-quality, photorealistic AI portraits for your generated youth academy players (newgens/regens) in **Football Manager**.

> **For most Windows users:** grab the **FMNewgenGenerator.exe** installer from the [website](https://fm-face-generator.netlify.app) / GitHub Releases. On first run it auto-downloads local ComfyUI (~2 GB) and the RealVisXL realism model (~7 GB) with a progress bar, then sets everything up for you — free, unlimited and offline.

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
We have provided a unified launch script: **`run_all.bat`**. 
When you double-click it, it will automatically:
1. Start your local **ComfyUI Server** in a minimized background window.
2. Wait 5 seconds for it to boot.
3. Launch the **FM AI Newgen Generator** application.

> [!NOTE]
> By default, the script looks for ComfyUI at `C:\Users\YOUR_USERNAME\ComfyUI\` (where portable ComfyUI is commonly installed). If you installed ComfyUI elsewhere, open `run_all.bat` in a text editor like Notepad and update the folder path.

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
*   **Python 3.10+** (A free scripting language. Download the installer from python.org. Make sure to check the box for **"Add Python to PATH"** during installation).
*   **ComfyUI** (A local tool to run AI models on your graphics card).

### 2. ComfyUI Setup
To generate high-quality faces, you need a photorealistic model:
1.  Download **Juggernaut XL (v9)** (or any other photorealistic SDXL model) from CivitAI or Hugging Face.
2.  Place the model file inside your ComfyUI checkpoints folder:
    `ComfyUI\models\checkpoints\`
3.  **Start ComfyUI** manually once to verify it launches on `http://127.0.0.1:8188`.

> [!IMPORTANT]
> **CRITICAL: ComfyUI Portable Folder Structure**
> If you are using the **ComfyUI Windows Portable** package, your folders are nested:
> *   The startup scripts (like `run_nvidia_gpu.bat`) reside in the parent folder (e.g., `C:\Users\YOUR_USERNAME\ComfyUI\`).
> *   The actual model directories reside in the nested folder (e.g., `C:\Users\YOUR_USERNAME\ComfyUI\ComfyUI\`).
> *   Your checkpoints **MUST** be placed in the **inner nested folder**:
>     `C:\Users\YOUR_USERNAME\ComfyUI\ComfyUI\models\checkpoints\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors`
> 
> *(If placed in the outer parent directory, ComfyUI will show an empty checkpoint list `[]` and reject generations).*

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
> **Mandatory Game Preferences Setup**
> For FM to display the new generated faces, you **MUST** configure these settings in your preferences:
> 1. Go to **Preferences > Interface** in Football Manager.
> 2. **Untick** *"Use caching to decrease page loading times"*.
> 3. **Tick** *"Reload skin when confirming changes in Preferences"*.
> 4. Click the **Clear Cache** button.
> 5. Click the **Reload Skin** button.

### A. View & Filter Configuration
1.  Obtain a custom search view file (`SCRIPT FACES player search.fmf`) and filter file (`is newgen search filter.fmf`) from the community (these are standard files, such as those provided by NewGAN Manager).
2.  Place the view file in your FM views directory:
    `Documents\Sports Interactive\Football Manager 2024\views\`
3.  Place the filter file in the `filters/` folder in the same directory:
    `Documents\Sports Interactive\Football Manager 2024\filters\`

### B. Usage Workflow
1.  Open the application, set your **Watch Directory** (e.g., an `exports` folder in this project) and your game's **Graphics Directory** (e.g., `Documents\Sports Interactive\Football Manager 2024\graphics\AI Newgen Faces`).
2.  Click **Start Watcher**.
3.  In Football Manager, go to **Scouting > Player Search**:
    *   Load the custom view and filter.
    *   Select all players (`Ctrl + A`), press **`Ctrl + P`** (Print), and select **To text file**. Save it inside your configured watch directory.
4.  **The App takes over:** It parses the player list, generates faces for any newly detected UIDs, saves them to disk, updates the `config.xml` mapping file, and reloads your skin in-game automatically!

---

## 📅 How Automatic Player Aging Works
Unlike other facepacks where players look the same forever, **this tool simulates players growing older automatically as your save progresses**:
*   Every time you export your player search list (e.g., once a season), the app parses player profiles and saves their generation age to `metadata.json`.
*   When a player crosses a key age milestone (**20, 24, and 28 years old**), the app detects the change.
*   It automatically triggers a new generation using the player's ID as the visual seed. This ensures their underlying facial features (bone structure, eyes) remain consistent, but updates their styling, hair length, and mature features (like stubble or beards) to match their older age.
*   The game's XML mappings are updated, and the new face is loaded. **The entire process is fully automatic — you only need to export your list occasionally!**