import cv2
import mediapipe as mp
import pyautogui
import time
import threading
import tkinter as tk
from tkinter import ttk
from collections import deque

pyautogui.FAILSAFE = False

# Inicialização do mediapipe para detecção de pontos faciais
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

# Inicialização do classificador pré-treinado para detecção de faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Inicialização do classificador pré-treinado para detecção de olhos
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

tela_width, tela_height = pyautogui.size()

# Variáveis para detectar a duração da abertura da boca
mouth_open = False
mouth_open_time = 0
MOUTH_OPEN_THRESHOLD = 2  # tempo em segundos

# Variável para controle do loop principal
running = False
camera_source = None

# Suavização do movimento do mouse
mouse_positions = deque(maxlen=5)

# Estado para movimento vertical do mouse
look_up = False
look_down = False

def get_available_cameras():
    """Retorna uma lista de índices de câmeras disponíveis."""
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

def start_detection():
    global running, camera_source
    running = True
    threading.Thread(target=run_detection, args=(camera_source,)).start()

def stop_detection():
    global running
    running = False

def smooth_mouse_movement(x, y):
    mouse_positions.append((x, y))
    avg_x = sum(pos[0] for pos in mouse_positions) // len(mouse_positions)
    avg_y = sum(pos[1] for pos in mouse_positions) // len(mouse_positions)
    return avg_x, avg_y

def run_detection(camera_source):
    global mouth_open, mouth_open_time, running, look_up, look_down

    cam = cv2.VideoCapture(camera_source)

    while running:
        # Lê o próximo frame do vídeo
        ret, frame = cam.read()
        if not ret:
            continue

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)  # Rotação do frame para o modo paisagem
        frame = cv2.flip(frame, 1)  # Inverte a imagem horizontalmente
        frame_height, frame_width, _ = frame.shape

        # Reduz a resolução do frame para acelerar o processamento
        small_frame = cv2.resize(frame, (frame_width // 2, frame_height // 2))
        small_frame_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Processa o frame reduzido com mediapipe para detecção de pontos faciais
        results = face_mesh.process(small_frame_rgb)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                lip_bottom_y, lip_top_y = None, None
                nose_tip_y = None
                for i, landmark in enumerate(face_landmarks.landmark):
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)
                    if i == 10:  # Exemplo: usar o ponto 10 para mover o mouse horizontalmente
                        smooth_x, smooth_y = smooth_mouse_movement(x * tela_width // frame_width, y * tela_height // frame_height)
                        pyautogui.moveTo(smooth_x, smooth_y)
                    if i == 1:  # Ponto 1 é a ponta do nariz
                        nose_tip_y = y
                    # Ponto 13 é o lábio inferior e o ponto 14 é o lábio superior
                    if i == 13:
                        lip_bottom_y = y
                    if i == 14:
                        lip_top_y = y

                # Mover o mouse verticalmente com base na posição do nariz
                if nose_tip_y is not None:
                    if nose_tip_y < frame_height // 3:  # Cabeça para cima
                        if not look_up:
                            look_up = True
                            look_down = False
                            pyautogui.moveRel(0, -20)
                    elif nose_tip_y > 2 * frame_height // 3:  # Cabeça para baixo
                        if not look_down:
                            look_down = True
                            look_up = False
                            pyautogui.moveRel(0, 20)
                    else:
                        look_up = False
                        look_down = False

                # Verifica se a boca está aberta
                if lip_bottom_y is not None and lip_top_y is not None:
                    mouth_distance = lip_bottom_y - lip_top_y
                    if mouth_distance > 15:  # Threshold para detectar boca aberta (ajuste conforme necessário)
                        if not mouth_open:
                            mouth_open = True
                            mouth_open_time = time.time()
                            pyautogui.click()  # Clique único ao abrir a boca
                    else:
                        mouth_open = False

        # Comentando a exibição do frame para focar na interface
        # cv2.imshow('Detecção de Faces, Olhos e Pontos Faciais', frame)

        # Sai do loop se a tecla 'q' for pressionada
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

# Interface gráfica
root = tk.Tk()
root.title("Detecção de Rosto e Controle do Mouse")

# Lista de câmeras disponíveis
available_cameras = get_available_cameras()
if available_cameras:
    selected_camera = tk.StringVar(root)
    selected_camera.set(available_cameras[0])  # Seleciona a primeira câmera por padrão

    camera_label = tk.Label(root, text="Selecione a Webcam:")
    camera_label.pack(pady=10)

    camera_menu = ttk.OptionMenu(root, selected_camera, *available_cameras)
    camera_menu.pack(pady=10)
    
    # Ativa o botão de confirmar
    confirm_button = tk.Button(root, text="Confirmar", command=confirm_link)
    confirm_button.pack(pady=10)
else:
    selected_camera = tk.StringVar(root)
    selected_camera.set("Nenhuma webcam encontrada")

    camera_label = tk.Label(root, text="Selecione a Webcam:")
    camera_label.pack(pady=10)

    camera_menu = ttk.OptionMenu(root, selected_camera, "Nenhuma webcam encontrada")
    camera_menu.pack(pady=10)

link_label = tk.Label(root, text="Ou insira o link da câmera:")
link_label.pack(pady=10)

link_entry = tk.Entry(root)
link_entry.pack(pady=10)

confirm_button = tk.Button(root, text="Confirmar", command=confirm_link)
confirm_button.pack(pady=10)

start_button = tk.Button(root, text="Iniciar", command=start_detection)
start_button.pack(pady=10)
start_button.config(state=tk.DISABLED)

stop_button = tk.Button(root, text="Parar", command=stop_detection)
stop_button.pack(pady=10)

root.mainloop()
