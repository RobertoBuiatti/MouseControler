import sys
from cx_Freeze import setup, Executable

# Dependências adicionais que você pode precisar
build_exe_options = {
    "packages": ["cv2", "mediapipe", "pyautogui", "threading", "collections", "time", "tkinter"],
    "excludes": [],
    "include_files": ['./interface.py', './detectorEyes.py', './detectorFace.py', './detectorNose.py'],  # Inclua aqui quaisquer outros arquivos necessários
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use "Win32GUI" se desejar ocultar a janela de console no Windows

# Lista de executáveis a serem criados
executables = [
    Executable("interface.py", base=base, icon="./computermouse_78940.ico")  # Substitua pelo caminho do seu ícone .ico
]

setup(
    name="Controlador Mouse",
    version="0.1",
    description="Descrição do projeto",
    options={"build_exe": build_exe_options},
    executables=executables
)
