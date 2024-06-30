import tkinter as tk
from tkinter import ttk
from detectorFace import start_detection as start_face_detection, stop_detection as stop_face_detection
from detectorNose import start_detection as start_nose_detection, stop_detection as stop_nose_detection
from detectorEyes import start_detection as start_eyes_detection, stop_detection as stop_eyes_detection
import cv2

camera_source = None
delay_value = 1  # Valor padrão

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
    global delay_value, current_detection_mode
    delay_value = float(selected_delay.get())
    detection_mode = selected_detection_mode.get()
    current_detection_mode = detection_mode
    if detection_mode == 'Nariz':
        start_nose_detection(camera_source, delay_value)
    elif detection_mode == 'Olhos':
        start_eyes_detection(camera_source, delay_value)
    elif detection_mode == 'Rosto':
        start_face_detection(camera_source, delay_value)
    else:
        start_face_detection(camera_source, delay_value)

def stop_detection_wrapper():
    detection_mode = current_detection_mode
    if detection_mode == 'Nariz':
        stop_nose_detection()
    elif detection_mode == 'Olhos':
        stop_eyes_detection()
    elif detection_mode == 'Rosto':
        stop_face_detection()

def validate_delay_input(P):
    if P.isdigit() or (P == '' or P == '.' or (P.startswith('-') and P[1:].isdigit())):
        return True
    else:
        return False

def create_widgets(root):
    global delay_entry  # Definindo delay_entry como global para ser acessível fora da função

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

    delay_label = ttk.Label(root, text="Digite os frames de parada (0 sem parada):")
    delay_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')

    vcmd = root.register(validate_delay_input)
    delay_entry = ttk.Entry(root, textvariable=selected_delay, validate="key", validatecommand=(vcmd, '%P'))
    delay_entry.grid(row=3, column=1, padx=10, pady=10, sticky='e')

    confirm_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
    start_button.grid(row=5, column=0, padx=10, pady=10)
    stop_button.grid(row=5, column=1, padx=10, pady=10)

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

# Opções de delay
delay_options = ['0', '0.5', '1', '2', '3', '4']
selected_delay = tk.StringVar(root)
selected_delay.set(delay_options[1])  # Seleciona '0.5' como padrão

confirm_button = ttk.Button(root, text="Confirmar", command=confirm_link)
start_button = ttk.Button(root, text="Iniciar", command=start_detection_wrapper)
start_button.config(state=tk.DISABLED)
stop_button = ttk.Button(root, text="Parar", command=stop_detection_wrapper)

# Variável para armazenar o modo de detecção atual
current_detection_mode = None

# Criação e posicionamento dos widgets
create_widgets(root)

root.mainloop()
