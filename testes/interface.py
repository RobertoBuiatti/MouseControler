import tkinter as tk
from tkinter import ttk
from detectorFace import start_detection as start_face_detection, stop_detection
from detectorNose import start_detection as start_nose_detection
from detectorEyes import start_detection as start_eyes_detection
import cv2

camera_source = None

def get_available_cameras():
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(str(index))
        cap.release()
        index += 1
    return arr

def confirm_link():
    global camera_source
    if link_entry.get():
        camera_source = link_entry.get()
    else:
        selected_camera_source = selected_camera.get()
        if selected_camera_source != "Nenhuma webcam encontrada":
            camera_source = int(selected_camera_source)
    start_button.config(state=tk.NORMAL if camera_source else tk.DISABLED)

def start_detection_wrapper():
    detection_mode = selected_detection_mode.get()
    if detection_mode == 'Nariz':
        start_nose_detection(camera_source)
    elif detection_mode == 'Olhos':
        start_eyes_detection(camera_source)
    elif detection_mode == 'Rosto':
        start_face_detection(camera_source)
    else:
        start_face_detection(camera_source)

def create_widgets(root):
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TLabel', font=('Helvetica', 12))
    style.configure('TButton', font=('Helvetica', 12))
    style.configure('TEntry', font=('Helvetica', 12))
    style.configure('TOptionMenu', font=('Helvetica', 12))
    style.configure('TCombobox', font=('Helvetica', 12))

    camera_label = ttk.Label(root, text="Selecione a Webcam:")
    camera_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

    camera_menu = ttk.OptionMenu(root, selected_camera, *available_cameras)
    camera_menu.grid(row=0, column=1, padx=10, pady=10, sticky='e')

    link_label = ttk.Label(root, text="Ou insira o link da câmera:")
    link_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

    link_entry.grid(row=1, column=1, padx=10, pady=10, sticky='e')

    detection_mode_label = ttk.Label(root, text="Selecione o modo de detecção:")
    detection_mode_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')

    detection_mode_menu = ttk.Combobox(root, textvariable=selected_detection_mode, values=detection_modes, state='readonly')
    detection_mode_menu.grid(row=2, column=1, padx=10, pady=10, sticky='e')

    confirm_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    start_button.grid(row=4, column=0, padx=10, pady=10)
    stop_button.grid(row=4, column=1, padx=10, pady=10)

# Interface gráfica
root = tk.Tk()
root.title("Detecção de Rosto e Controle do Mouse")

# Lista de câmeras disponíveis
available_cameras = get_available_cameras()
if available_cameras:
    selected_camera = tk.StringVar(root)
    selected_camera.set(available_cameras[0])  # Seleciona a primeira câmera por padrão
else:
    selected_camera = tk.StringVar(root)
    selected_camera.set("Nenhuma webcam encontrada")

link_entry = ttk.Entry(root)

# Modos de detecção
detection_modes = ['Nariz', 'Olhos', 'Rosto']
selected_detection_mode = tk.StringVar(root)
selected_detection_mode.set(detection_modes[0])  # Seleciona o primeiro modo por padrão

confirm_button = ttk.Button(root, text="Confirmar", command=confirm_link)
start_button = ttk.Button(root, text="Iniciar", command=start_detection_wrapper)
start_button.config(state=tk.DISABLED)
stop_button = ttk.Button(root, text="Parar", command=stop_detection)

# Criação e posicionamento dos widgets
create_widgets(root)

root.mainloop()
