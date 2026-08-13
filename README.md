# Football Manager AI Newgen Face Generator

A performance-friendly desktop application designed to automatically generate high-quality, photorealistic AI portraits for your generated youth players (newgens/regens) in **Football Manager**.

It watches your player export files, parses player profiles (age, nationality, personality), generates unique faces locally using **ComfyUI (SDXL)**, and automatically creates the game-compatible `config.xml` facepack mappings.

---

## 🚀 One-Click Launcher (Windows)
We have provided a unified launch script: **`run_all.bat`**. 
When you double-click it, it will automatically:
1. Start your local **ComfyUI Server** in a minimized background window.
2. Wait 5 seconds for it to boot.
3. Launch the **FM AI Newgen Generator** application.

> [!NOTE]
> By default, the script looks for ComfyUI at `%USERPROFILE%\ComfyUI\` (where portable ComfyUI is commonly installed). If you installed ComfyUI elsewhere, open `run_all.bat` in a text editor like Notepad and update the folder path.

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
*   **Python 3.10+** (Make sure to check *"Add Python to PATH"* during installation).
*   **ComfyUI** (Local installation with an SDXL model).

### 2. ComfyUI Setup
To generate high-quality faces, you need a photorealistic SDXL checkpoint:
1.  Download **Juggernaut XL (v9)** (or a similar photorealistic SDXL model) from Hugging Face or CivitAI.
2.  Place the model file inside your ComfyUI checkpoints folder:
    `ComfyUI\models\checkpoints\`
3.  **Start ComfyUI** manually once to verify it launches on `http://127.0.0.1:8188`.

> [!IMPORTANT]
> **CRITICAL: ComfyUI Portable Folder Structure**
> If you are using the **ComfyUI Windows Portable** package, your folders are nested:
> *   The startup scripts (like `run_nvidia_gpu.bat`) reside in the parent folder (e.g. `%USERPROFILE%\ComfyUI\`).
> *   The actual model directories reside in the nested folder (e.g. `%USERPROFILE%\ComfyUI\ComfyUI\`).
> *   Your checkpoints **MUST** be placed in the **inner nested folder**:
>     `%USERPROFILE%\ComfyUI\ComfyUI\models\checkpoints\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors`
> 
> *(If placed in the outer parent directory, ComfyUI will show an empty checkpoint list `[]` and reject generations).*

### 3. Application Setup
1.  Copy `config.example.json` to `config.json`.
2.  Open the terminal/command prompt in this folder and install dependencies:
    ```cmd
    pip install -r requirements.txt
    ```
3.  Double-click `run_all.bat` to launch the application.

---

## ⚽ Setting Up Football Manager

> [!IMPORTANT]
> **Mandatory Game Preferences Setup**
> For FM to display the new generated faces:
> 1. Go to **Preferences > Interface** in Football Manager.
> 2. **Untick** *"Use caching to decrease page loading times"*.
> 3. **Tick** *"Reload skin when confirming changes in Preferences"*.
> 4. Click the **Clear Cache** button.
> 5. Click the **Reload Skin** button.

### A. View & Filter Configuration
1.  Copy a custom scout search view file (`SCRIPT FACES player search.fmf`) and filter file (`is newgen search filter.fmf`) from the community (e.g. from NewGAN Manager).
2.  Place the view file in your FM user directory:
    *   Windows: `Documents\Sports Interactive\Football Manager 2024\views\`
3.  Place the filter file in the `filters/` folder in the same directory.

### B. Usage Workflow
1.  Open the application, configure your **Watch Directory** (e.g., an `exports` folder in this project) and your game's **Graphics Directory** (e.g., `Documents\Sports Interactive\Football Manager 2024\graphics\AI Newgen Faces`).
2.  Click **Start Watcher**.
3.  In Football Manager, go to **Scouting > Player Search**:
    *   Load the custom view and filter.
    *   Select all players (`Ctrl + A`), press **`Ctrl + P`** (Print), and select **To text file**. Save it inside your configured watch directory.
4.  **The App takes over:** It parses the player list, generates faces for any newly detected UIDs, saves them to disk, updates the `config.xml` mapping file, and reloads your skin in-game automatically!

---

## 🛠️ Configuration & Customization
All options can be customized in the UI or directly in `config.json`:
*   `comfyui_model`: Exact filename of your SDXL model. If left empty, the app auto-detects the first model in your checkpoints directory.
*   `comfyui_steps` (25) & `comfyui_cfg` (6.0): Control generation speed and style.
*   `face_style`: The prompt template used to guide SDXL. The default snapshot-style prompt generates natural, raw smartphone camera portraits.
*   `auto_reload_skin_hotkey` (false): Enable if you want the app to automatically trigger the `Shift + R` reload shortcut in Windows.