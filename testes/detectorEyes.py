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
mouse_positions = deque(maxlen=10)  # Aumentando o histórico para maior suavização
eye_positions = deque(maxlen=10)

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

    frame_count = 0

    while running:
        ret, frame = cam.read()
        if not ret:
            continue

        frame_count += 1
        if frame_count % 2 != 0:  # Processa apenas cada segundo frame para reduzir a carga
            continue

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape

        small_frame = cv2.resize(frame, (frame_width // 2, frame_height // 2))
        small_frame_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(small_frame_rgb)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                left_eye_x, left_eye_y = None, None
                right_eye_x, right_eye_y = None, None
                lip_bottom_y, lip_top_y = None, None

                for i, landmark in enumerate(face_landmarks.landmark):
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)
                    if i == 33:
                        left_eye_x = x
                        left_eye_y = y
                    if i == 263:
                        right_eye_x = x
                        right_eye_y = y
                    if i == 13:
                        lip_bottom_y = y
                    if i == 14:
                        lip_top_y = y

                if left_eye_x is not None and left_eye_y is not None and right_eye_x is not None and right_eye_y is not None:
                    eye_center_x = (left_eye_x + right_eye_x) // 2
                    eye_center_y = (left_eye_y + right_eye_y) // 2

                    eye_positions.append((eye_center_x, eye_center_y))
                    if len(eye_positions) > 1:
                        prev_x, prev_y = eye_positions[-2]
                        delta_x = abs(eye_center_x - prev_x)
                        delta_y = abs(eye_center_y - prev_y)

                        if delta_x > 1 or delta_y > 1:
                            if acceleration_factor < acceleration_limit:
                                acceleration_factor += acceleration_step
                            sensitivity_x = acceleration_factor
                            sensitivity_y = acceleration_factor
                            move_x = int((eye_center_x - frame_width // 2) * sensitivity_x)
                            move_y = int((eye_center_y - frame_height // 2) * sensitivity_y)
                            smooth_x, smooth_y = smooth_mouse_movement(pyautogui.position().x + move_x, pyautogui.position().y + move_y)
                            pyautogui.moveTo(smooth_x, smooth_y)
                            eye_color = (0, 0, 255)
                        else:
                            acceleration_factor = 0.5
                            eye_color = (0, 255, 0)

                if lip_bottom_y is not None and lip_top_y is not None:
                    mouth_distance = lip_top_y - lip_bottom_y
                    current_time = time.time()
                    if mouth_distance > MOUTH_DISTANCE_THRESHOLD:
                        if not mouth_open:
                            mouth_open = True
                            mouth_open_start_time = current_time
                            pyautogui.click()
                            click_color = (0, 0, 255)
                        elif current_time - mouth_open_start_time > MOUTH_OPEN_THRESHOLD:
                            pyautogui.doubleClick()
                            click_color = (0, 255, 255)
                            mouth_open_start_time = current_time
                    else:
                        mouth_open = False
                        click_color = (0, 255, 0)

                for idx, landmark in enumerate(face_landmarks.landmark):
                    if idx in {33, 263}:
                        x = int(landmark.x * frame_width)
                        y = int(landmark.y * frame_height)
                        cv2.circle(frame, (x, y), 2, eye_color, -1)
                    elif idx in {13, 14}:
                        x = int(landmark.x * frame_width)
                        y = int(landmark.y * frame_height)
                        cv2.circle(frame, (x, y), 2, click_color, -1)

        cv2.imshow('Face Mesh', frame)
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
