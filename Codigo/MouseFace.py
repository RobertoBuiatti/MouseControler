import cv2
import mediapipe as mp
import pyautogui

pyautogui.FAILSAFE = False

# Inicialização do mediapipe para detecção de pontos faciais
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Inicialização do classificador pré-treinado para detecção de faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Inicialização do classificador pré-treinado para detecção de olhos
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Inicia a captura de vídeo
cam = cv2.VideoCapture("http://192.168.1.6:4747/video")

tela_width, tela_height = pyautogui.size()

while True:
    # Lê o próximo frame do vídeo
    _, frame = cam.read()
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE) # Rotação do frame para o modo paisagem
    frame = cv2.flip(frame, 1)  # Inverte a imagem horizontalmente
    frame_height, frame_width, _ = frame.shape

    # Converte o frame para escala de cinza (necessário para a detecção de faces)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detecta as faces no frame usando o classificador Haar
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(90, 90))

    # Para cada face detectada
    for (x, y, w, h) in faces:
        # Desenha um retângulo ao redor da face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Obtém a região de interesse (ROI) para a face
        roi_gray = gray_frame[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        # Detecta olhos na ROI usando o classificador Haar
        eyes = eye_cascade.detectMultiScale(roi_gray)

        # Para cada olho detectado
        for (ex, ey, ew, eh) in eyes:
            # Desenha um retângulo ao redor do olho
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

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
                    break

    # Mostra o frame com as faces, olhos e pontos faciais detectados
    cv2.imshow('Detecção de Faces, Olhos e Pontos Faciais', frame)

    # Sai do loop se a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a captura de vídeo e fecha todas as janelas
cam.release()
cv2.destroyAllWindows()
