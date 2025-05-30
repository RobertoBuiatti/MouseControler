import json
import requests
from typing import Dict, Any, Optional, Union, List
from gemini_config import GeminiConfig

class VoiceProcessor:
    def __init__(self):
        """Inicializa o processador de voz com as configurações do Gemini"""
        self.config = GeminiConfig

    def process_command(self, text: str) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Processa o comando de voz usando a API do Gemini
        
        Args:
            text: O texto do comando de voz a ser processado
            
        Returns:
            Dict ou List[Dict] com a interpretação do comando ou None se houver erro
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
                    # Extrai o texto da resposta
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    # Remove espaços em branco e quebras de linha extras
                    text_response = text_response.strip()
                    
                    # Remove marcadores Markdown de código se presentes
                    text_response = text_response.replace('```json', '').replace('```', '').strip()
                    
                    # Log para debug
                    print(f"Resposta bruta do Gemini: {text_response}")
                    
                    # Verifica se é um array de comandos
                    if text_response.lstrip().startswith('['):
                        json_start = text_response.find('[')
                        json_end = text_response.rfind(']') + 1
                    else:
                        json_start = text_response.find('{')
                        json_end = text_response.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = text_response[json_start:json_end]
                        parsed_json = json.loads(json_str)
                        
                        # Valida se é um array ou comando único
                        if isinstance(parsed_json, list):
                            # Valida cada comando no array
                            for cmd in parsed_json:
                                if not self._validate_command(cmd):
                                    print("JSON inválido: campos obrigatórios ausentes em comando sequencial")
                                    return None
                            return parsed_json
                        else:
                            # Valida comando único
                            if self._validate_command(parsed_json):
                                return parsed_json
                            else:
                                print("JSON inválido: campos obrigatórios ausentes")
                                return None
                    else:
                        print("Não foi possível encontrar JSON válido na resposta")
                        return None
                        
                except (KeyError, json.JSONDecodeError) as e:
                    print(f"Erro ao processar resposta do Gemini: {e}")
                    print(f"Resposta problemática: {text_response}")
                    return None
            else:
                print(f"Erro na requisição: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro ao processar comando: {e}")
            return None

    def _validate_command(self, command: Dict[str, Any]) -> bool:
        """
        Valida se um comando possui todos os campos obrigatórios
        
        Args:
            command: Dicionário com o comando a ser validado
            
        Returns:
            True se o comando é válido, False caso contrário
        """
        required_fields = ['action', 'direction', 'distance', 'command', 'target']
        return all(field in command for field in required_fields)

    def interpret_command(self, result: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """
        Interpreta o resultado do processamento em uma string legível
        
        Args:
            result: Dicionário ou lista de dicionários com o resultado do processamento
            
        Returns:
            String descritiva do comando interpretado
        """
        if not result:
            return "Comando não reconhecido"
            
        # Se for uma lista de comandos
        if isinstance(result, list):
            interpretations = []
            for cmd in result:
                interpretations.append(self._interpret_single_command(cmd))
            return " → ".join(interpretations)
        else:
            # Se for um comando único
            return self._interpret_single_command(result)

    def _interpret_single_command(self, result: Dict[str, Any]) -> str:
        """
        Interpreta um único comando
        
        Args:
            result: Dicionário com o comando a ser interpretado
            
        Returns:
            String descritiva do comando
        """
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
