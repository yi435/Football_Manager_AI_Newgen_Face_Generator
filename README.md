# Football Manager AI Newgen Face Generator

A performance-friendly Windows tool designed to automatically generate high-quality, photorealistic AI portraits for your generated youth academy players (newgens/regens) in **Football Manager**.

It watches your player search exports, parses player profiles (age, nationality, and personality), generates unique faces locally using **ComfyUI (SDXL)**, and automatically creates the game-compatible `config.xml` facepack mappings.

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

### 3. Application Setup
1.  Copy `config.example.json` to `config.json`.
2.  Open your command prompt in this folder and install dependencies:
    ```cmd
    pip install -r requirements.txt
    ```
3.  Double-click `run_all.bat` to launch the application.

---

## ⚽ Setting Up Football Manager

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