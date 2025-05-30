import speech_recognition as sr
import pyautogui
import threading
import time
import win32gui
import win32con
import os
from typing import Optional, Dict, Callable
import re
from queue import Queue
from voice_processor import VoiceProcessor

class VoiceController:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Melhorias no reconhecimento de voz
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 400
        self.recognizer.pause_threshold = 0.5
        self.recognizer.phrase_threshold = 0.3
        
        self.is_running = False
        self.command_history = []
        self.current_directory = os.getcwd()
        self.default_distance = 20  # Distância padrão em pixels
        
        # Fila para comunicação entre threads
        self.command_queue = Queue()
        
        # Processador de voz com Gemini
        self.processor = VoiceProcessor()

    def start(self):
        """Inicia o controlador de voz"""
        self.is_running = True
        threading.Thread(target=self._run_recognition, daemon=True).start()

    def stop(self):
        """Para o controlador de voz"""
        self.is_running = False

    def get_command(self) -> Optional[str]:
        """Retorna o próximo comando da fila, se houver"""
        if not self.command_queue.empty():
            return self.command_queue.get()
        return None

    def _run_recognition(self):
        """Loop principal de reconhecimento de voz"""
        while self.is_running:
            try:
                with sr.Microphone() as source:
                    print("Aguardando comando...")
                    # Ajusta o reconhecedor para o nível de ruído ambiente
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source)
                    
                try:
                    text = self.recognizer.recognize_google(audio, language='pt-BR').lower()
                    print(f"Texto reconhecido: {text}")
                    
                    # Processa o comando usando Gemini
                    result = self.processor.process_command(text)
                    if result:
                        # Adiciona o comando interpretado à fila
                        interpreted = self.processor.interpret_command(result)
                        self.command_queue.put(interpreted)
                        print(f"Comando interpretado: {interpreted}")
                        
                        # Executa a ação baseada no resultado
                        self._execute_command(result)
                    
                except sr.UnknownValueError:
                    print("Não foi possível entender o áudio")
                except sr.RequestError as e:
                    print(f"Erro na requisição ao serviço de reconhecimento: {e}")
                    
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(1)

    def _execute_command(self, result: Dict):
        """Executa o comando baseado no resultado do processamento"""
        action = result.get('action')
        
        if action == 'mover':
            self._move_mouse(
                result.get('direction', ''),
                result.get('distance', self.default_distance)
            )
            
        elif action == 'clicar':
            command = result.get('command')
            if command == 'duplo':
                self._double_click()
            else:
                self._click()
                
        elif action == 'sistema':
            command = result.get('command')
            target = result.get('target')
            
            if command == 'fechar':
                self._close_window()
            elif command == 'minimizar':
                self._minimize_window()
            elif command == 'maximizar':
                self._maximize_window()
            elif command == 'abrir' and target:
                self._open_program(target)

    def _move_mouse(self, direction: str, distance: int):
        """Move o mouse em uma direção específica por uma distância determinada"""
        x, y = pyautogui.position()
        
        if direction == "cima":
            pyautogui.moveTo(x, y - distance)
        elif direction == "baixo":
            pyautogui.moveTo(x, y + distance)
        elif direction == "esquerda":
            pyautogui.moveTo(x - distance, y)
        elif direction == "direita":
            pyautogui.moveTo(x + distance, y)

    def _click(self):
        """Realiza um clique simples"""
        pyautogui.click()

    def _double_click(self):
        """Realiza um clique duplo"""
        pyautogui.doubleClick()

    def _close_window(self):
        """Fecha a janela atual"""
        hwnd = win32gui.GetForegroundWindow()
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    def _minimize_window(self):
        """Minimiza a janela atual"""
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

    def _maximize_window(self):
        """Maximiza a janela atual"""
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

    def _open_program(self, program: str):
        """Tenta abrir um programa ou arquivo"""
        try:
            os.startfile(program)
        except Exception as e:
            print(f"Erro ao abrir {program}: {e}")

def start_detection():
    """Inicia o detector de voz"""
    controller = VoiceController()
    controller.start()
    return controller

def stop_detection(controller: Optional[VoiceController]):
    """Para o detector de voz"""
    if controller:
        controller.stop()
