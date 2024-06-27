import cv2
import mediapipe as mp
import pyautogui
import time
import threading
import tkinter as tk
from tkinter import ttk

pyautogui.FAILSAFE = False

# Inicialização do mediapipe para detecção de pontos faciais
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

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

def get_available_cameras():
    """Retorna uma lista de índices de câmeras disponíveis."""
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr

def confirm_link():
    global camera_source
    camera_source = link_entry.get()
    start_button.config(state=tk.NORMAL if camera_source else tk.DISABLED)

def start_detection():
    global running
    running = True
    threading.Thread(target=run_detection).start()

def stop_detection():
    global running
    running = False

def run_detection():
    global mouth_open, mouth_open_time, running

    cam = cv2.VideoCapture(camera_source)

    while running:
        # Lê o próximo frame do vídeo
        _, frame = cam.read()
        if frame is None:
            continue

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)  # Rotação do frame para o modo paisagem
        frame = cv2.flip(frame, 1)  # Inverte a imagem horizontalmente
        frame_height, frame_width, _ = frame.shape

        # Converte o frame para escala de cinza (necessário para a detecção de faces)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detecta as faces no frame usando o classificador Haar
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(90, 90))

        # Para cada face detectada
        for (x, y, w, h) in faces:
            # Desenha um retângulo ao redor da face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Obtém a região de interesse (ROI) para a face
            roi_gray = gray_frame[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            # Detecta olhos na ROI usando o classificador Haar
            eyes = eye_cascade.detectMultiScale(roi_gray)

            # Para cada olho detectado
            for (ex, ey, ew, eh) in eyes:
                # Desenha um retângulo ao redor do olho
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

        # Processa o frame com mediapipe para detecção de pontos faciais
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for i, landmark in enumerate(face_landmarks.landmark):
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)
                    if i == 10:  # Exemplo: usar o ponto 10 para mover o mouse
                        pyautogui.moveTo(x * tela_width // frame_width, y * tela_height // frame_height)
                    # Ponto 13 é o lábio inferior e o ponto 14 é o lábio superior
                    if i == 13:
                        lip_bottom_y = y
                    if i == 14:
                        lip_top_y = y

                # Verifica se a boca está aberta
                if 'lip_bottom_y' in locals() and 'lip_top_y' in locals():
                    mouth_distance = lip_bottom_y - lip_top_y
                    if mouth_distance > 15:  # Threshold para detectar boca aberta (ajuste conforme necessário)
                        if not mouth_open:
                            mouth_open = True
                            mouth_open_time = time.time()
                            pyautogui.click()  # Clique único ao abrir a boca
                        elif time.time() - mouth_open_time > MOUTH_OPEN_THRESHOLD:
                            pyautogui.doubleClick()  # Duplo clique se a boca ficar aberta por mais de MOUTH_OPEN_THRESHOLD segundos
                            mouth_open = False  # Redefine o estado para evitar cliques contínuos
                    else:
                        mouth_open = False

        # Mostra o frame com as faces, olhos e pontos faciais detectados
        cv2.imshow('Detecção de Faces, Olhos e Pontos Faciais', frame)

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

if not available_cameras:
    stop_button.config(state=tk.DISABLED)

root.mainloop()
