# -*- mode: python ; coding: utf-8 -*-
import glob

a = Analysis(
    ['app_ui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('AppUI\\Assets', 'AppUI\\Assets'),
        ('Clients\\Assets', 'Clients\\Assets')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

a.datas += [("AppUI\\Assets\\Audio\\r2\\"+file.split("\\")[-1], file, "DATA") for file in glob.glob("AppUI\\Assets\\Audio\\r2\\*")]

pyz = PYZ(a.pure)

exe = EXE(
   pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='R4-MG',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico',
)
