# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Collect all PyQt6 dependencies and resources
pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all("PyQt6")

a = Analysis(
    ['main.py'],  # Your main script
    pathex=[],
    binaries=[] + pyqt6_binaries,  # Include PyQt6 binaries
    datas=[
        ('assets', 'assets'),  # Include your assets folder
    ] + pyqt6_datas,  # Include PyQt6 data files
    hiddenimports=[
        'keyboard',
        'plyer.platforms.win.notification',  # Specific to plyer notifications on Windows
        'pynput',
        'PyQt6',
    ] + pyqt6_hiddenimports,  # Add PyQt6 hidden imports
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='bot.Click',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see the console window for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
