"""
Configurações para a API do Gemini
"""

class GeminiConfig:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    API_KEY = "AIzaSyA8_mnMJCeRNBtddv8Js4L94HNsZ4_7NxM"
    HEADERS = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    @staticmethod
    def get_command_prompt(text: str) -> str:
        return f"""
        Analise o comando de voz em português: "{text}"
        
        Retorne apenas um JSON com o seguinte formato, sem nenhum texto adicional:
        {{
            "action": "mover|clicar|sistema",
            "direction": "cima|baixo|esquerda|direita|null",
            "distance": número em pixels (20 para pouco, 50 para médio, 100 para muito),
            "command": "clique|duplo|fechar|minimizar|maximizar|abrir|null",
            "target": "nome do programa/arquivo se houver ou null"
        }}
        
        Exemplos de interpretação:
        "um pouco para direita" -> {{"action": "mover", "direction": "direita", "distance": 20, "command": null, "target": null}}
        "muito para cima" -> {{"action": "mover", "direction": "cima", "distance": 100, "command": null, "target": null}}
        "clique duas vezes" -> {{"action": "clicar", "direction": null, "distance": 0, "command": "duplo", "target": null}}
        "abra o chrome" -> {{"action": "sistema", "direction": null, "distance": 0, "command": "abrir", "target": "chrome"}}
        """
