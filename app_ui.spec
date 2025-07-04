# -*- mode: python ; coding: utf-8 -*-
import glob

a = Analysis(
    ['app_ui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('AppUI\\Assets\\Text\\CHANGELOG.md', 'AppUI\\Assets\\Text'),
        ('AppUI\\Assets\\Text\\shortcuts.md', 'AppUI\\Assets\\Text'),

        ('AppUI\\Assets\\Data\\shd.json', 'AppUI\\Assets\\Data'),
        ('AppUI\\Assets\\Data\\sor.json', 'AppUI\\Assets\\Data'),
        ('AppUI\\Assets\\Data\\twi.json', 'AppUI\\Assets\\Data'),
        ('AppUI\\Assets\\Data\\jtl.json', 'AppUI\\Assets\\Data'),
        ('AppUI\\Assets\\Data\\lof.json', 'AppUI\\Assets\\Data'),
        ('AppUI\\Assets\\Data\\starwarsunlimited_com_filters.json', 'AppUI\\Assets\\Data'),

        ('AppUI\\Assets\\Images\\logo.png', 'AppUI\\Assets\\Images'),
        ('AppUI\\Assets\\Images\\SWH_Logo_Black_preview.png', 'AppUI\\Assets\\Images'),
        ('AppUI\\Assets\\Images\\cardback.png', 'AppUI\\Assets\\Images'),
        ('AppUI\\Assets\\Images\\r4-head.png', 'AppUI\\Assets\\Images'),
        ('AppUI\\Assets\\Images\\large_spark_of_rebellion_starfield_c4fdfaa6a7.png', 'AppUI\\Assets\\Images'),
        ('AppUI\\Assets\\Images\\set-identifier-example.png', 'AppUI\\Assets\\Images')
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
