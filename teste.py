import cv2
import mediapipe as mp
import pyautogui

pyautogui.FAILSAFE = False

# Inicialização do mediapipe para detecção de pontos faciais
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Inicia a captura de vídeo
cam = cv2.VideoCapture("http://192.168.1.6:4747/video")

tela_width, tela_height = pyautogui.size()

while True:
    # Lê o próximo frame do vídeo
    _, frame = cam.read()
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE) # Rotação do frame para o modo paisagem
    frame = cv2.flip(frame, 1)  # Inverte a imagem horizontalmente
    frame_height, frame_width, _ = frame.shape

    # Processa o frame com mediapipe para detecção de pontos faciais
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for landmark in face_landmarks.landmark:
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)  # Desenha um ponto verde para cada landmark
                
                # Move o mouse com base no ponto 10
                if landmark == face_landmarks.landmark[10]:  
                    pyautogui.moveTo(x * tela_width // frame_width, y * tela_height // frame_height)

    # Mostra o frame com os pontos faciais detectados
    cv2.imshow('Detecção de Pontos Faciais', frame)

    # Sai do loop se a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a captura de vídeo e fecha todas as janelas
cam.release()
cv2.destroyAllWindows()
