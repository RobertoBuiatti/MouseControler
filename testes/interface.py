import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Entry, Combobox, Button, Label, OptionMenu
from detectorFace import (
    start_detection as start_face_detection,
    stop_detection as stop_face_detection,
)
from detectorNose import (
    start_detection as start_nose_detection,
    stop_detection as stop_nose_detection,
)
from detectorEyes import (
    start_detection as start_eyes_detection,
    stop_detection as stop_eyes_detection,
)
import cv2
from PIL import Image, ImageTk
import os

camera_source = None
delay_value = 1  # Valor padrão
rotation_value = 0  # Valor padrão de rotação

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
    global selected_camera_source
    if link_entry.get():
        camera_source = link_entry.get()
    else:
        selected_camera_source = selected_camera.get()
        if selected_camera_source != "Nenhuma webcam encontrada":
            camera_source = int(selected_camera_source)
    start_button.config(state=tk.NORMAL if camera_source or selected_camera_source else tk.DISABLED)

def start_detection_wrapper():
    global delay_value, current_detection_mode
    delay_value = float(selected_delay.get())
    detection_mode = selected_detection_mode.get()
    current_detection_mode = detection_mode
    if detection_mode == "Nariz":
        start_nose_detection(camera_source, delay_value, rotation_value)
    elif detection_mode == "Olhos":
        start_eyes_detection(camera_source, delay_value, rotation_value)
    elif detection_mode == "Rosto":
        start_face_detection(camera_source, delay_value, rotation_value)
    else:
        start_face_detection(camera_source, delay_value, rotation_value)

def stop_detection_wrapper():
    detection_mode = current_detection_mode
    if detection_mode == "Nariz":
        stop_nose_detection()
    elif detection_mode == "Olhos":
        stop_eyes_detection()
    elif detection_mode == "Rosto":
        stop_face_detection()

def validate_delay_input(P):
    if P.isdigit() or (P == "" or P == "." or (P.startswith("-") and P[1:].isdigit())):
        return True
    else:
        return False

def toggle_theme():
    global current_theme, icon_label
    if current_theme == "dark":
        style.theme_use("flatly")
        icon_label.config(image=sun_icon)
        current_theme = "light"
        root.configure(bg="white")
    else:
        style.theme_use("cosmo")
        icon_label.config(image=moon_icon)
        current_theme = "dark"
        root.configure(bg="black")
    update_widget_colors()

def update_icon_background():
    if current_theme == "dark":
        icon_label.config(bg="black")
    else:
        icon_label.config(bg="white")

def update_widget_colors():
    fg_color = "white" if current_theme == "dark" else "black"
    bg_color = "black" if current_theme == "dark" else "white"
    camera_label.config(foreground=fg_color, background=bg_color)
    link_label.config(foreground=fg_color, background=bg_color)
    detection_mode_label.config(foreground=fg_color, background=bg_color)
    delay_label.config(foreground=fg_color, background=bg_color)
    update_icon_background()

def create_widgets(root):
    global delay_entry, icon_label, camera_label, link_label, detection_mode_label, delay_label  # Definindo widgets como global para serem acessíveis fora da função

    icon_label = tk.Label(root, image=moon_icon, bg="black")
    icon_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
    icon_label.bind("<Button-1>", lambda e: toggle_theme())

    camera_label = Label(
        root, text="Selecione a Webcam:", background="black", foreground="white"
    )
    camera_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    camera_menu = OptionMenu(root, selected_camera, *available_cameras, style="info")
    camera_menu.grid(row=1, column=1, padx=10, pady=10, sticky="e")

    link_label = Label(
        root, text="Ou insira o link da câmera:", background="black", foreground="white"
    )
    link_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    link_entry.grid(row=2, column=1, padx=10, pady=10, sticky="e")

    detection_mode_label = Label(
        root,
        text="Selecione o modo de detecção:",
        background="black",
        foreground="white",
    )
    detection_mode_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    detection_mode_menu = Combobox(
        root,
        textvariable=selected_detection_mode,
        values=detection_modes,
        state="readonly",
        style="info",
    )
    detection_mode_menu.grid(row=3, column=1, padx=10, pady=10, sticky="e")

    delay_label = Label(
        root,
        text="Digite os frames de parada (0 sem parada):",
        background="black",
        foreground="white",
    )
    delay_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

    vcmd = root.register(validate_delay_input)
    delay_entry = Entry(
        root,
        textvariable=selected_delay,
        validate="key",
        validatecommand=(vcmd, "%P"),
        style="info",
    )
    delay_entry.grid(row=4, column=1, padx=10, pady=10, sticky="e")

    confirm_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
    rotate_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
    start_button.grid(row=7, column=0, padx=10, pady=10)
    stop_button.grid(row=7, column=1, padx=10, pady=10)

def rotate_image():
    global rotation_value
    if rotation_value == 0:
        rotation_value = 90
    elif rotation_value == 90:
        rotation_value = 180
    elif rotation_value == 180:
        rotation_value = 270
    elif rotation_value == 270:
        rotation_value = 0
    else:
        rotation_value = 0  # Valor padrão caso um valor inválido seja passado



# Interface gráfica
root = tk.Tk()
root.title("Detecção de Rosto e Controle do Mouse")

# Aplicar o estilo moderno usando ttkbootstrap
style = Style(theme="cosmo")

# Definindo o fundo preto para o root
root.configure(bg="black")

# Carregar ícones PNG
icon_path = os.path.join(os.path.dirname(__file__), 'icon')

# Redimensionar ícones para 32x32 pixels
moon_icon_image = Image.open(os.path.join(icon_path, 'night.png')).resize((32, 32), Image.Resampling.LANCZOS)
moon_icon = ImageTk.PhotoImage(moon_icon_image)
sun_icon_image = Image.open(os.path.join(icon_path, 'sun.png')).resize((32, 32), Image.Resampling.LANCZOS)
sun_icon = ImageTk.PhotoImage(sun_icon_image)

# Lista de câmeras disponíveis
available_cameras = get_available_cameras()
if available_cameras:
    selected_camera = tk.StringVar(root)
    selected_camera.set(available_cameras[0])  # Seleciona a primeira câmera por padrão
else:
    selected_camera = tk.StringVar(root)
    selected_camera.set("Nenhuma webcam encontrada")

link_entry = Entry(root, style="info")

# Modos de detecção
detection_modes = ["Nariz", "Olhos", "Rosto"]
selected_detection_mode = tk.StringVar(root)
selected_detection_mode.set(detection_modes[2])  # Seleciona o primeiro modo por padrão

# Opções de delay
delay_options = ["0", "1", "2", "3", "4"]
selected_delay = tk.StringVar(root)
selected_delay.set(delay_options[1])  # Seleciona '1' como padrão

confirm_button = Button(
    root, text="Confirmar", command=confirm_link, style="primary.TButton"
)
start_button = Button(
    root, text="Iniciar", command=start_detection_wrapper, style="success.TButton"
)
start_button.config(state=tk.DISABLED)
stop_button = Button(
    root, text="Parar", command=stop_detection_wrapper, style="danger.TButton"
)
rotate_button = Button(
    root, text="Rodar Camera", command=rotate_image, style="warning.TButton"
)

# Variável para armazenar o modo de detecção atual
current_detection_mode = None

# Variável para armazenar o tema atual
current_theme = "dark"

# Função para alternar tema

# Criação dos widgets
create_widgets(root)

# Iniciar o loop principal do Tkinter
root.mainloop()
