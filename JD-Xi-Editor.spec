# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

from jdxi_editor.bundle_imports import COLLECT_ALL, HIDDEN_IMPORTS

datas, binaries, hiddenimports = collect_all('PySide6')
for package in COLLECT_ALL:
    extra_datas, extra_binaries, extra_hidden = collect_all(package)
    datas += extra_datas
    binaries += extra_binaries
    hiddenimports += extra_hidden

# Add this manually:
hiddenimports += ['PySide6.QtDBus', *HIDDEN_IMPORTS]
dbus_binaries = collect_dynamic_libs('PySide6.QtDBus')
binaries += dbus_binaries

block_cipher = None


a = Analysis(
    ['jdxi_editor/main.py'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    pathex=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JD-Xi-Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='jdxi_editor.icns'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JD-Xi-Editor',
)
