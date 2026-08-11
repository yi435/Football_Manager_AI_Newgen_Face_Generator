# Football Manager 2024 AI Newgen Face Generator

A performance-friendly, cross-platform Desktop GUI tool designed to automatically generate high-quality, photorealistic AI portraits for your generated youth players (newgens/regens) in **Football Manager 2024**.

---

> [!IMPORTANT]
> **CRITICAL: Football Manager Graphics Setup**
> For the game to recognize and display the generated faces, you **MUST** configure these settings in your game preferences (otherwise, the game will ignore the new images and the `config.xml`):
> 1. In Football Manager, go to **Preferences > Interface**.
> 2. **Untick** the checkbox for *"Use caching to decrease page loading times"*.
> 3. **Tick** the checkbox for *"Reload skin when confirming changes in Preferences"*.
> 4. Click the **Clear Cache** button (essential: this forces the game to wipe its old graphics index and find our new `config.xml`).
> 5. Click the **Reload Skin** button.
> 
> ---

## Key Features

1. **Zero Local Overhead:** Uses **Pollinations.ai**'s remote servers to generate face portraits. Consumes **0% of your local GPU and RAM**, leaving all your system resources for running the game.
2. **Milestone-Based Player Aging:** To simulate players growing older, the generator uses their Unique ID as a random seed. This ensures that their underlying facial structure remains consistent, but their visual attributes (like hair length, stubble, and mature features) update when they cross key milestones: **16, 20, 24, and 28 years old**.
3. **Visual Personality Mapping:** Player personalities (from the exported list) are mapped directly into the AI prompt:
   - *Model Citizen / Professional:* Well-groomed hair, clean-shaven, polite smile, neat appearance.
   - *Temperamental / Confrontational:* Stern serious look, messy delinquent haircut, minor cosmetic scar.
   - *Jovial / Spirited:* Warm, happy smiling expression with friendly laughing eyes.
4. **Weighted Demographics for Multi-Ethnic Countries:** Multi-ethnic countries (such as France, England, Brazil, USA, Belgium) use demographic weight profiles (e.g., France has 70% European, 20% African, 10% North African probability) to ensure the generated newgen intake matches real-life ratios.
5. **Real-Player Preservation:** Creates a separate graphics directory mapping entries to its own `config.xml`. Your existing real-player facepacks (like DF11 or Cutouts) remain completely safe and untouched.
6. **Auto Reload Skin:** On Windows, the application automatically triggers the game's skin reload hotkey (`Shift + R`) once new faces are ready.

---

## Folder Structure

```
zed projet/
├── config.json            # Tool settings (graphics/watch paths, prompt styles)
├── requirements.txt       # Python dependencies (watchdog, striprtf, aiohttp)
├── README.md              # This guide
├── commit.sh              # Double-click script to commit changes to GitHub (Linux)
├── commit.bat             # Double-click script to commit changes to GitHub (Windows)
├── verify_tool.py         # Mock verification test suite
└── src/
    ├── __init__.py
    ├── app.py             # App orchestrator and hotkey triggers
    ├── ui.py              # Dark-themed Tkinter GUI interface
    ├── watcher.py         # Background directory watcher
    ├── parser.py          # RTF/HTML player parser & demographic builder
    ├── generator.py       # Asynchronous face image generator (Pollinations.ai)
    └── xml_manager.py     # config.xml reader/writer
```

---

## Installation & Running

### Prerequisites
You need **Python 3.10+** installed on your system.

### 1. On Windows (Where you play the game)
1. Open Command Prompt or PowerShell in this project folder.
2. Install the requirements:
   ```cmd
   pip install -r requirements.txt
   ```
3. Run the application:
   ```cmd
   python -m src.app
   ```
4. (Optional) Run the commit helper to save changes to your GitHub:
   ```cmd
   commit.bat
   ```

### 2. On Linux (Fedora - Development)
1. Open your terminal in this folder.
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python3 -m src.app
   ```
4. (Optional) Run the commit helper:
   ```bash
   ./commit.sh
   ```

---

## Setting Up Football Manager 2024

Since FM24 does not provide a developer API, we use a simple background file watcher. To use it, follow these steps:

### A. View & Filter Configuration
1. Obtain the custom view file (`SCRIPT FACES player search.fmf`) and filter file (`is newgen search filter.fmf`). You can use the standard files provided by the community (like NewGAN Manager).
2. Place the view file in your FM directory:
   - Windows: `Documents\Sports Interactive\Football Manager 2024\views\`
   - Linux: `~/.steam/steam/steamapps/compatdata/2252600/pfx/drive_c/users/steamuser/Documents/Sports Interactive/Football Manager 2024/views/`
3. Place the filter file in the `filters/` folder inside the same Football Manager directory.

### B. Daily Gameplay Workflow
1. In the app UI, select your **Watch Directory** (e.g., a folder named `exports` in this project folder) and your **Graphics Directory** (e.g., `Documents\Sports Interactive\Football Manager 2024\graphics\AI Newgen Faces`).
2. Click **Start Watcher**.
3. In Football Manager:
   - Go to **Scouting** > **Player Search**.
   - Load the Custom View: Click the dropdown (Overview) > **Custom** > **Import View** > select `SCRIPT FACES player search`.
   - Load the Filter: Click the cog icon (bottom left) > **Manage Filters** > **Import** > select `is newgen search filter`. Apply it.
   - Select all players in the list (`Ctrl + A`).
   - Press **`Ctrl + P`** (Print), select **To text file** or **To web page**, and save the file inside your configured watch directory.
4. **The App takes over:** The script detects the new file, parses the UIDs, generates faces dynamically for any new players or aged players, updates `config.xml`, and triggers a skin reload in Football Manager automatically!
5. In game, you can press **`Shift + R`** manually to reload the skin if auto-reload is turned off in settings.

---

## Troubleshooting

- **No faces generated:** Ensure the search view contains the **Unique ID (UID)** column. The parser filters out any rows that do not have a UID starting with `2`.
- **Faces look completely different as they age:** The generation seed is bound to the player's numeric UID. Make sure you do not change the prompt seed settings in `generator.py`.
- **Skin does not reload:** In FM preferences, go to **Preferences > Interface** and tick **"Reload skin when confirming changes in Preferences"** and uncheck **"Use caching to decrease page loading times"**.
