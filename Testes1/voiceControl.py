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
                    print("\n=== Iniciando reconhecimento de voz ===")
                    text = self.recognizer.recognize_google(audio, language='pt-BR').lower()
                    print(f"✓ Texto reconhecido: '{text}'")
                    
                    print("\n=== Processando comando ===")
                    # Processa o comando usando Gemini
                    result = self.processor.process_command(text)
                    
                    if result:
                        # Adiciona o comando interpretado à fila
                        interpreted = self.processor.interpret_command(result)
                        self.command_queue.put(interpreted)
                        print(f"✓ Comando interpretado com sucesso: '{interpreted}'")
                        print(f"✓ Detalhes do comando: {result}")
                        
                        # Executa a ação baseada no resultado
                        print("\n=== Executando comando ===")
                        self._execute_command(result)
                        print("✓ Comando executado com sucesso")
                    else:
                        print("✗ Falha ao processar comando - resultado nulo")
                    
                except sr.UnknownValueError:
                    print("✗ Não foi possível entender o áudio - fala não reconhecida")
                except sr.RequestError as e:
                    print(f"✗ Erro na requisição ao serviço de reconhecimento: {e}")
                    print("  Verifique sua conexão com a internet")
                    
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(1)

    def _execute_command(self, result: Union[Dict[str, Any], List[Dict[str, Any]]]):
        """Executa o comando ou sequência de comandos baseado no resultado do processamento"""
        try:
            # Se for uma lista de comandos, executa cada um em sequência
            if isinstance(result, list):
                print(f"\n=== Executando sequência de {len(result)} comandos ===")
                for i, cmd in enumerate(result, 1):
                    print(f"\n▶ Executando comando {i}/{len(result)}")
                    self._execute_single_command(cmd)
                    # Pequena pausa entre comandos sequenciais
                    if i < len(result):
                        time.sleep(0.5)
            else:
                # Se for um comando único
                self._execute_single_command(result)
                
        except Exception as e:
            print(f"✗ Erro ao executar sequência de comandos: {str(e)}")
            print(f"  Detalhes: {result}")

    def _execute_single_command(self, cmd: Dict[str, Any]):
        """Executa um único comando"""
        try:
            action = cmd.get('action')
            print(f"\nExecutando ação: {action}")
            
            if action == 'mover':
                direction = cmd.get('direction', '')
                distance = cmd.get('distance', self.default_distance)
                print(f"→ Movendo mouse: direção={direction}, distância={distance}px")
                self._move_mouse(direction, distance)
                print("✓ Mouse movido com sucesso")
                
            elif action == 'clicar':
                command = cmd.get('command')
                if command == 'duplo':
                    print("→ Executando clique duplo")
                    self._double_click()
                    print("✓ Clique duplo realizado")
                else:
                    print("→ Executando clique simples")
                    self._click()
                    print("✓ Clique simples realizado")
                    
            elif action == 'sistema':
                command = cmd.get('command')
                target = cmd.get('target')
                print(f"→ Comando do sistema: {command}")
                
                if command == 'fechar':
                    print("→ Fechando janela atual")
                    self._close_window()
                    print("✓ Janela fechada")
                elif command == 'minimizar':
                    print("→ Minimizando janela atual")
                    self._minimize_window()
                    print("✓ Janela minimizada")
                elif command == 'maximizar':
                    print("→ Maximizando janela atual")
                    self._maximize_window()
                    print("✓ Janela maximizada")
                elif command == 'abrir' and target:
                    print(f"→ Abrindo programa: {target}")
                    self._open_program(target)
                    print(f"✓ Programa {target} iniciado")
                else:
                    print(f"✗ Comando do sistema não reconhecido: {command}")
            else:
                print(f"✗ Ação não reconhecida: {action}")
                
        except Exception as e:
            print(f"✗ Erro ao executar comando: {str(e)}")
            print(f"  Detalhes do comando: {cmd}")

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
