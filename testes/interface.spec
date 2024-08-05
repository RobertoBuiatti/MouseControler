# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['interface.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('detectorEyes.py', '.'),
        ('detectorFace.py', '.'),
        ('detectorNose.py', '.'),
        ('icon/night.png', 'icon'),
        ('icon/sun.png', 'icon'),
        ('computermouse_78940.ico', '.'),
        # Incluir o diretório dos modelos do MediaPipe
        (r'C:\path\to\mediapipe\modules\face_landmark', 'mediapipe/modules/face_landmark'),
        # Adicione outros diretórios ou arquivos necessários
    ],
    hiddenimports=['numpy', 'cv2', 'mediapipe', 'pyautogui', 'threading', 'ttkbootstrap', 'collections', 'time', 'tkinter'],
    hookspath=[],
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
    name='Controlador Mouse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Use False para aplicações GUI
    icon='computermouse_78940.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Controlador Mouse',
)
