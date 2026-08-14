# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the FM AI Newgen Generator Windows EXE.

Build (on Windows):
    pip install pyinstaller
    pyinstaller --clean build/FMNewgenGenerator.spec
"""

import glob
import os

# PyInstaller exposes the spec file path as the `SPEC` global.
_SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
ROOT = os.path.abspath(os.path.join(_SPEC_DIR, ".."))

ICON = os.path.join(_SPEC_DIR, "icon.ico")

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    binaries=[],
    datas=[
        (os.path.join(ROOT, "config.example.json"), "."),
    ],
    hiddenimports=[
        "aiohttp",
        "aiohttp.web",
        "watchdog.observers",
        "striprtf.striprtf",
        "requests",
        "PIL.Image",
        "py7zr",
        "src.app",
        "src.ui",
        "src.watcher",
        "src.parser",
        "src.generator",
        "src.xml_manager",
        "src.setup_wizard",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter.test"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FMNewgenGenerator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # GUI app (no console window)
    icon=ICON,
)
