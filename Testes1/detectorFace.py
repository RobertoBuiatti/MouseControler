import cv2
import mediapipe as mp
import pyautogui
import threading
from collections import deque
import time

pyautogui.FAILSAFE = False

# Inicialização do mediapipe para detecção de pontos faciais
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

# Tamanho da tela para referência do movimento do mouse
tela_width, tela_height = pyautogui.size()

# Variáveis para detectar a duração da abertura da boca
mouth_open = False
mouth_open_start_time = None
MOUTH_OPEN_THRESHOLD = 0.5  # tempo em segundos para duplo clique
MOUTH_DISTANCE_THRESHOLD = 15  # Threshold para detectar boca aberta

# Suavização do movimento do mouse
mouse_positions = deque(maxlen=10)  # Aumentando o histórico para maior suavização
face_positions = deque(maxlen=10)

# Estado para controle do loop principal
running = False
acceleration_factor = 1.5
acceleration_step = 0.2
acceleration_limit = 25.0

# Valor padrão para a sensibilidade de movimento
default_sensitivity = 0.5

# Variável global para cor do rosto
face_color = (0, 255, 0)  # Cor padrão


def smooth_mouse_movement(x, y):
    mouse_positions.append((x, y))

    if len(mouse_positions) > 1:
        smooth_x = int(sum(pos[0] for pos in mouse_positions) / len(mouse_positions))
        smooth_y = int(sum(pos[1] for pos in mouse_positions) / len(mouse_positions))

        current_x, current_y = pyautogui.position()
        interp_x = current_x + (smooth_x - current_x) // 2
        interp_y = current_y + (smooth_y - current_y) // 2

        return interp_x, interp_y
    else:
        return x, y


def run_detection(camera_source, delay_value, rotation_value):
    global mouth_open, mouth_open_start_time, running, acceleration_factor, face_color

    cam = cv2.VideoCapture(camera_source)

    frame_count = 0

    while cam.isOpened() and running:
        ret, frame = cam.read()
        if not ret:
            continue

        frame_count += 1
        if (
            frame_count % 2 != 0
        ):  # Processa apenas cada segundo frame para reduzir a carga
            continue

        if rotation_value == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif rotation_value == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif rotation_value == 270:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif rotation_value == 0:
            # Não faz nada, a imagem permanece como está
            pass
        else:
            # Caso um valor inesperado seja passado, por segurança, não rotaciona o frame
            pass

        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape

        small_frame = cv2.resize(frame, (frame_width // 2, frame_height // 2))
        small_frame_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(small_frame_rgb)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Calcular o centroide (média) dos pontos faciais
                face_x_sum = 0
                face_y_sum = 0
                num_landmarks = 0

                for landmark in face_landmarks.landmark:
                    face_x_sum += landmark.x * frame_width
                    face_y_sum += landmark.y * frame_height
                    num_landmarks += 1

                if num_landmarks > 0:
                    face_x_avg = int(face_x_sum / num_landmarks)
                    face_y_avg = int(face_y_sum / num_landmarks)

                    face_positions.append((face_x_avg, face_y_avg))
                    if len(face_positions) > 1:
                        prev_x, prev_y = face_positions[-2]
                        delta_x = face_x_avg - prev_x
                        delta_y = face_y_avg - prev_y

                        # Ajuste do valor do delta para maior suavização
                        sensitivity = acceleration_factor
                        if abs(delta_x) > delay_value or abs(delta_y) > delay_value:
                            if acceleration_factor < acceleration_limit:
                                acceleration_factor += acceleration_step
                            move_x = int(delta_x * sensitivity * 4)
                            move_y = int(delta_y * sensitivity * 8)
                            smooth_x, smooth_y = smooth_mouse_movement(
                                pyautogui.position().x + move_x,
                                pyautogui.position().y + move_y,
                            )
                            pyautogui.moveTo(smooth_x, smooth_y)
                            face_color = (0, 0, 255)
                        else:
                            acceleration_factor = default_sensitivity
                            face_color = (0, 255, 0)
                lip_bottom_y, lip_top_y = None, None
                for i, landmark in enumerate(face_landmarks.landmark):
                    if i == 13:
                        lip_bottom_y = int(landmark.y * frame_height)
                    if i == 14:
                        lip_top_y = int(landmark.y * frame_height)

                if lip_bottom_y is not None and lip_top_y is not None:
                    mouth_distance = lip_top_y - lip_bottom_y
                    current_time = time.time()
                    if mouth_distance > MOUTH_DISTANCE_THRESHOLD:
                        if not mouth_open:
                            mouth_open = True
                            mouth_open_start_time = current_time
                            pyautogui.click()
                    else:
                        mouth_open = False

        cv2.imshow("Face Mesh", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()


def start_detection(camera_source, delay_value, rotation_value):
    global running
    running = True
    threading.Thread(target=run_detection, args=(camera_source, delay_value, rotation_value)).start()


def stop_detection():
    global running
    running = False
    while threading.active_count() > 1:
        time.sleep(0.1)
    cv2.destroyAllWindows()
