# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['interface.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\\\Users\\\\rober\\\\Desktop\\\\projeto\\\\icon', 'icon'), ('C:\\\\Users\\\\rober\\\\Desktop\\\\projeto\\\\detectorFace', 'detectorFace'), ('C:\\\\Users\\\\rober\\\\Desktop\\\\projeto\\\\detectorNose', 'detectorNose'), ('C:\\\\Users\\\\rober\\\\Desktop\\\\projeto\\\\detectorEyes', 'detectorEyes')],
    hiddenimports=['tkinter', 'ttkbootstrap', 'cv2', 'PIL', 'mediapipe', 'pyautogui'],
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
    name='mouse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
