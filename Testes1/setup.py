import sys
from cx_Freeze import setup, Executable
import os

# Opções para o build
build_exe_options = {
    "packages": [
        "numpy",
        "cv2",
        "mediapipe",
        "pyautogui",
        "threading",
        "ttkbootstrap",
        "collections",
        "time",
        "tkinter",
    ],
    "excludes": [],
    "include_files": [
        ("interface.py", "."),  # Inclui o arquivo 'interface.py' no diretório atual
        (
            "detectorEyes.py",
            ".",
        ),  # Inclui o arquivo 'detectorEyes.py' no diretório atual
        (
            "detectorFace.py",
            ".",
        ),  # Inclui o arquivo 'detectorFace.py' no diretório atual
        (
            "detectorNose.py",
            ".",
        ),  # Inclui o arquivo 'detectorNose.py' no diretório atual
        ("icon/night.png", "icon/"),  # Inclui o arquivo 'night.png' no diretório 'icon'
        ("icon/sun.png", "icon/"),  # Inclui o arquivo 'sun.png' no diretório 'icon'
        (
            "computermouse_78940.ico",
            ".",
        ),  # Inclui o arquivo 'computermouse_78940.ico' no diretório atual
        # Corrigindo o caminho para incluir o arquivo binarypb
        (
            os.path.join(
                "Testes1",
                ".venv",
                "Lib",
                "site-packages",
                "mediapipe",
                "modules",
                "face_landmark",
                "face_landmark_front_cpu.binarypb",
            ),
            os.path.join("mediapipe", "modules", "face_landmark"),
        ),  # Inclui o arquivo binarypb necessário para o MediaPipe
    ],
    "build_exe": os.path.join(
        os.getcwd(), "build"
    ),  # Caminho de build alterado para o diretório atual
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use "Win32GUI" para ocultar a janela de console no Windows

# Lista de executáveis a serem criados
executables = [
    Executable(
        "interface.py", base=base, icon="computermouse_78940.ico"
    )  # Certifique-se de que o caminho do ícone está correto
]

setup(
    name="Controlador Mouse",
    version="0.1",
    description="Descrição do projeto",
    options={"build_exe": build_exe_options},
    executables=executables,
)
