# Project Walkthrough - FM24 AI Newgen Face Generator

We have successfully set up the entire project folder and initialized Git! All Python source files, settings, and commit scripts have been written, compiled, and verified for syntax correctness.

---

## What Was Created

Here is a summary of the files now in your project folder ([zed projet](file:///home/zakariae/Documents/zed%20projet)):

1. **Project Infrastructure:**
   - [.gitignore](file:///home/zakariae/Documents/zed%20projet/.gitignore): Excludes Python caches, temporary raw exports, and the downloaded faces from your GitHub repository.
   - [requirements.txt](file:///home/zakariae/Documents/zed%20projet/requirements.txt): Lists necessary libraries (`watchdog`, `striprtf`, `aiohttp`, `pillow`).
   - [config.json](file:///home/zakariae/Documents/zed%20projet/config.json): Default parameters for prompts, folders, and concurrency.
   - [README.md](file:///home/zakariae/Documents/zed%20projet/README.md): Step-by-step user guide for setting up and playing in the game.
   - [commit.sh](file:///home/zakariae/Documents/zed%20projet/commit.sh) & [commit.bat](file:///home/zakariae/Documents/zed%20projet/commit.bat): Quick double-click script to stage, commit, and push changes to GitHub.

2. **Source Code (`src/`):**
   - [xml_manager.py](file:///home/zakariae/Documents/zed%20projet/src/xml_manager.py): Reads and writes FM's `config.xml` mapping.
   - [parser.py](file:///home/zakariae/Documents/zed%20projet/src/parser.py): Parses RTF and HTML player tables, resolves ancestry/dual-nationalities, and builds prompts.
   - [generator.py](file:///home/zakariae/Documents/zed%20projet/src/generator.py): Downloads faces in parallel using asynchronous client calls to Pollinations.ai with seed-consistent aging.
   - [watcher.py](file:///home/zakariae/Documents/zed%20projet/src/watcher.py): Monitors the watch folder for new exports.
   - [ui.py](file:///home/zakariae/Documents/zed%20projet/src/ui.py): Dark-themed Tkinter GUI.
   - [app.py](file:///home/zakariae/Documents/zed%20projet/src/app.py): App controller, milestone-aging engine, and ctypes-based `Shift + R` Windows keyboard simulator.

3. **Validation & Sandbox:**
   - [verify_tool.py](file:///home/zakariae/Documents/zed%20projet/verify_tool.py): Sandbox verification script that mock-tests the entire logic.

---

## How to Test the Project on Windows

Once you are on the Windows PC where you play Football Manager 2024, follow these steps to test:

1. **Setup Git & GitHub Connection:**
   - Open Command Prompt/PowerShell in your project folder:
     ```cmd
     git init
     ```
   - Connect it to your GitHub account (replace with your repository link):
     ```cmd
     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
     git branch -M main
     git push -u origin main
     ```
   - In the future, you can double-click **`commit.bat`** to push code changes automatically!

2. **Install Requirements:**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Run a Verification Test:**
   - Run the validation script to verify that the parser, prompt builder, API downloader, and XML manager work correctly on Windows:
     ```cmd
     python verify_tool.py
     ```
   - Check the folder `graphics/AI Newgen Faces/`. You should see `2001000001.png` (a generated photorealistic face of a Japanese player), a clean `config.xml`, and a `metadata.json` showing they are mapped at age milestone 16.

4. **Launch the GUI Application:**
   ```cmd
   python src/app.py
   ```
   - Set the watch directory to the `exports` folder.
   - Set the graphics directory to your Football Manager `graphics/AI Newgen Faces` folder.
   - Toggle **Start Watcher**.
   - Play the game, export your player search to `exports`, and watch the GUI log your face generations in real-time!
