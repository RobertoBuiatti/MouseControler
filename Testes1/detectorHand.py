import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import threading
from typing import Tuple, Optional

# Configuração para melhor performance do PyAutoGUI
pyautogui.FAILSAFE = False

class HandDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,  # Reduzido para melhor detecção
            min_tracking_confidence=0.5    # Reduzido para movimento mais suave
        )
        self.prev_hand_landmarks = None
        self.last_gesture = None
        self.last_gesture_time = 0
        self.double_click_start = 0
        self.is_dragging = False
        
        # Configurações de suavização
        self.smoothing = 0.5
        self.prev_x, self.prev_y = 0, 0
        
        # Configuração da zona morta
        self.dead_zone_size = 30
        
        # Obter dimensões da tela
        self.screen_width, self.screen_height = pyautogui.size()

    def detect_hand_landmarks(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], np.ndarray]:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0]
            h, w, _ = frame.shape
            return np.array([[lm.x * w, lm.y * h] for lm in landmarks.landmark]), frame
        return None, frame

    def get_gesture(self, landmarks: np.ndarray) -> str:
        """Identifica o gesto baseado nos landmarks da mão"""
        if landmarks is None:
            return "none"

        # Extrair pontos importantes
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        palm_center = landmarks[0]

        # Calcular distâncias entre dedos
        thumb_index_dist = np.linalg.norm(thumb_tip - index_tip)
        
        # Verificar dedos levantados
        finger_tips = [index_tip, middle_tip, ring_tip, pinky_tip]
        palm_ref = landmarks[0]
        fingers_up = sum([1 for tip in finger_tips if tip[1] < palm_ref[1]])

        # Identificar gestos
        if fingers_up == 0:
            return "closed"  # Clique esquerdo
        elif fingers_up == 1 and pinky_tip[1] < palm_ref[1]:
            return "pinky"  # Clique direito
        elif fingers_up == 2 and middle_tip[1] < palm_ref[1] and index_tip[1] < palm_ref[1]:
            return "peace"  # Copiar
        elif thumb_index_dist < 20 and fingers_up == 1:
            return "ok"  # Colar
        elif fingers_up == 2 and thumb_tip[1] < palm_ref[1] and index_tip[1] < palm_ref[1]:
            return "drag"  # Arrastar
        elif fingers_up == 3:
            return "alt_tab"  # Alt+Tab
        elif fingers_up >= 4:
            return "open"  # Movimento do mouse
        
        return "none"

    def handle_gestures(self, gesture: str, hand_center: Tuple[float, float]):
        """Processa os gestos identificados e executa as ações correspondentes"""
        current_time = time.time()
        
        # Suavizar movimento do mouse
        x, y = hand_center
        smooth_x = int(self.prev_x + (x - self.prev_x) * self.smoothing)
        smooth_y = int(self.prev_y + (y - self.prev_y) * self.smoothing)
        
        # Atualizar posição anterior
        self.prev_x, self.prev_y = smooth_x, smooth_y

        # Verificar zona morta
        if abs(x - self.prev_x) < self.dead_zone_size and abs(y - self.prev_y) < self.dead_zone_size:
            return

        # Processar gestos
        if gesture == "open":
            if not self.is_dragging:
                pyautogui.moveTo(smooth_x, smooth_y)
        
        elif gesture == "closed":
            if self.last_gesture == "closed" and (current_time - self.last_gesture_time) < 0.3:
                pyautogui.doubleClick()
                self.last_gesture = None
            else:
                pyautogui.click()
            
        elif gesture == "pinky":
            pyautogui.rightClick()
            
        elif gesture == "drag":
            if not self.is_dragging:
                pyautogui.mouseDown()
                self.is_dragging = True
                
        elif gesture == "peace":
            pyautogui.hotkey('ctrl', 'c')
            
        elif gesture == "ok":
            pyautogui.hotkey('ctrl', 'v')
            
        elif gesture == "alt_tab":
            pyautogui.hotkey('alt', 'tab')
        
        # Se não estamos mais arrastando e estávamos antes
        if gesture != "drag" and self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False

        self.last_gesture = gesture
        self.last_gesture_time = current_time

# Estado para controle do loop principal
running = False

def run_detection(camera_source, delay_value, rotation_value):
    """Função principal de detecção executada em uma thread"""
    global running
    
    cam = cv2.VideoCapture(camera_source)
    detector = HandDetector()
    
    while running:
        ret, frame = cam.read()
        if not ret:
            continue

        # Redimensionar frame para melhor performance
        frame_height, frame_width, _ = frame.shape
        frame = cv2.resize(frame, (frame_width // 2, frame_height // 2))
        
        # Espelhar o frame horizontalmente
        frame = cv2.flip(frame, 1)
        
        # Rotacionar frame se necessário
        if rotation_value != 0:
            if rotation_value == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif rotation_value == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif rotation_value == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        # Detectar landmarks da mão
        landmarks, frame = detector.detect_hand_landmarks(frame)
        
        if landmarks is not None:
            # Calcular centro da mão para movimento do mouse
            hand_center_x = np.mean(landmarks[:, 0])
            hand_center_y = np.mean(landmarks[:, 1])
            
            # Mapear coordenadas da câmera para coordenadas da tela
            screen_x = np.interp(hand_center_x, [0, frame.shape[1]], [0, detector.screen_width])
            screen_y = np.interp(hand_center_y, [0, frame.shape[0]], [0, detector.screen_height])
            
            # Identificar e processar gestos
            gesture = detector.get_gesture(landmarks)
            detector.handle_gestures(gesture, (screen_x, screen_y))
            
            # Desenhar landmarks para debug
            for lm in landmarks:
                cv2.circle(frame, (int(lm[0]), int(lm[1])), 5, (0, 255, 0), -1)
        
        cv2.imshow('Hand Tracking', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q') or not running:
            break
            
        time.sleep(delay_value)

    # Liberar recursos
    cam.release()
    cv2.destroyAllWindows()

def start_detection(camera_source, delay_value, rotation_value):
    """Inicia a detecção de mãos em uma thread separada"""
    global running
    running = True
    threading.Thread(target=run_detection, args=(camera_source, delay_value, rotation_value)).start()

def stop_detection():
    """Para a detecção de mãos"""
    global running
    running = False
    while threading.active_count() > 1:
        time.sleep(0.1)
    cv2.destroyAllWindows()
