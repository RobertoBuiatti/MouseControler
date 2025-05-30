import json
import requests
from typing import Dict, Any, Optional
from gemini_config import GeminiConfig

class VoiceProcessor:
    def __init__(self):
        """Inicializa o processador de voz com as configurações do Gemini"""
        self.config = GeminiConfig

    def process_command(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Processa o comando de voz usando a API do Gemini
        
        Args:
            text: O texto do comando de voz a ser processado
            
        Returns:
            Dict com a interpretação do comando ou None se houver erro
        """
        try:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": self.config.get_command_prompt(text)
                    }]
                }]
            }
            
            response = requests.post(
                self.config.URL,
                headers=self.config.HEADERS,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extrai o JSON da resposta do modelo
                try:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    # Remove espaços em branco e quebras de linha extras
                    text_response = text_response.strip()
                    return json.loads(text_response)
                except (KeyError, json.JSONDecodeError) as e:
                    print(f"Erro ao processar resposta: {e}")
                    return None
            else:
                print(f"Erro na requisição: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro ao processar comando: {e}")
            return None

    def interpret_command(self, result: Dict[str, Any]) -> str:
        """
        Interpreta o resultado do processamento em uma string legível
        
        Args:
            result: Dicionário com o resultado do processamento
            
        Returns:
            String descritiva do comando interpretado
        """
        if not result:
            return "Comando não reconhecido"
            
        action = result.get('action')
        if action == 'mover':
            direction = result.get('direction', '')
            distance = result.get('distance', 0)
            return f"Mover {distance} pixels para {direction}"
            
        elif action == 'clicar':
            command = result.get('command', '')
            if command == 'duplo':
                return "Clique duplo"
            return "Clique simples"
            
        elif action == 'sistema':
            command = result.get('command', '')
            target = result.get('target', '')
            if target:
                return f"{command.capitalize()} {target}"
            return command.capitalize()
            
        return "Comando não reconhecido"
