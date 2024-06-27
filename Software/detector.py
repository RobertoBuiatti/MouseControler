import cv2
import mediapipe as mp
import pyautogui
import threading
from collections import deque
import time

pyautogui.FAILSAFE = False

# Inicialização do mediapipe para detecção de pontos faciais
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

tela_width, tela_height = pyautogui.size()

# Variáveis para detectar a duração da abertura da boca
mouth_open = False
mouth_open_start_time = None
last_click_time = 0
MOUTH_OPEN_THRESHOLD = 0.5  # tempo em segundos para duplo clique
MOUTH_DISTANCE_THRESHOLD = 15  # Threshold para detectar boca aberta

# Suavização do movimento do mouse
mouse_positions = deque(maxlen=5)
nose_positions = deque(maxlen=5)

# Estado para controle do loop principal
running = False
acceleration_factor = 0.5
acceleration_step = 0.1
acceleration_limit = 5.0

def smooth_mouse_movement(x, y):
    mouse_positions.append((x, y))
    avg_x = sum(pos[0] for pos in mouse_positions) // len(mouse_positions)
    avg_y = sum(pos[1] for pos in mouse_positions) // len(mouse_positions)
    return avg_x, avg_y

def run_detection(camera_source):
    global mouth_open, mouth_open_start_time, last_click_time, running, acceleration_factor

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
                nose_tip_x, nose_tip_y = None, None
                for i, landmark in enumerate(face_landmarks.landmark):
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)
                    if i == 1:  # Ponto 1 é a ponta do nariz
                        nose_tip_x = x
                        nose_tip_y = y
                    # Ponto 13 é o lábio inferior e o ponto 14 é o lábio superior
                    if i == 13:
                        lip_bottom_y = y
                    if i == 14:
                        lip_top_y = y

                if nose_tip_x is not None and nose_tip_y is not None:
                    nose_positions.append((nose_tip_x, nose_tip_y))
                    if len(nose_positions) > 1:
                        prev_x, prev_y = nose_positions[-2]
                        delta_x = abs(nose_tip_x - prev_x)
                        delta_y = abs(nose_tip_y - prev_y)

                        # Verifica se o movimento é significativo
                        if delta_x > 2 or delta_y > 2:
                            # Incrementa o fator de aceleração até o limite
                            if acceleration_factor < acceleration_limit:
                                acceleration_factor += acceleration_step
                            sensitivity_x = acceleration_factor  # Ajustar a sensibilidade horizontal
                            sensitivity_y = acceleration_factor  # Ajustar a sensibilidade vertical
                            move_x = int((nose_tip_x - frame_width // 2) * sensitivity_x)
                            move_y = int((nose_tip_y - frame_height // 2) * sensitivity_y)
                            smooth_x, smooth_y = smooth_mouse_movement(pyautogui.position().x + move_x, pyautogui.position().y + move_y)
                            pyautogui.moveTo(smooth_x, smooth_y)
                            nose_color = (0, 0, 255)  # Vermelho para movimento
                        else:
                            # Reseta o fator de aceleração quando o movimento para
                            acceleration_factor = 0.5
                            nose_color = (0, 255, 0)  # Verde para sem movimento

                # Verifica se a boca está aberta
                if lip_bottom_y is not None and lip_top_y is not None:
                    mouth_distance = lip_top_y - lip_bottom_y #pega a distancia dos pontos da boca
                    current_time = time.time()
                    print(f"mouth_distance: {mouth_distance}")  # Print para depuração
                    if mouth_distance > MOUTH_DISTANCE_THRESHOLD:
                        if not mouth_open:
                            mouth_open = True
                            mouth_open_start_time = current_time
                            print("Mouth opened - Single click")  # Print para depuração
                            pyautogui.click()  # Clique único ao abrir a boca
                            click_color = (0, 0, 255)  # Vermelho para clique
                        elif current_time - mouth_open_start_time > MOUTH_OPEN_THRESHOLD:
                            print("Mouth open long enough - Double click")  # Print para depuração
                            pyautogui.doubleClick()  # Duplo clique se a boca estiver aberta por um tempo suficiente
                            click_color = (0, 255, 255)  # Amarelo para duplo clique
                            mouth_open_start_time = current_time  # Reseta o tempo de início para evitar múltiplos duplos cliques
                    else:
                        mouth_open = False
                        click_color = (0, 255, 0)  # Verde quando a boca não está aberta

                # Desenha pontos na imagem
                for idx, landmark in enumerate(face_landmarks.landmark):
                    if idx == 1:  # Desenhar ponto do nariz
                        x = int(landmark.x * frame_width)
                        y = int(landmark.y * frame_height)
                        cv2.circle(frame, (x, y), 2, nose_color, -1)
                    elif idx in {13, 14}:  # Desenhar pontos dos lábios
                        x = int(landmark.x * frame_width)
                        y = int(landmark.y * frame_height)
                        cv2.circle(frame, (x, y), 2, click_color, -1)

        # Mostra a imagem
        cv2.imshow('Face Mesh', frame)

        # Sai do loop se a tecla 'q' for pressionada
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

def start_detection(camera_source):
    global running
    running = True
    threading.Thread(target=run_detection, args=(camera_source,)).start()

def stop_detection():
    global running
    running = False

# Exemplo de como iniciar e parar a detecção
# start_detection(0)  # Para iniciar a detecção
# stop_detection()  # Para parar a detecção
