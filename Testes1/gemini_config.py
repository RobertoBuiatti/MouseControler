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
        Você é um analisador de comandos de voz em português que DEVE retornar APENAS um objeto JSON válido, sem nenhum texto adicional ou formatação.

        Analise o seguinte comando: "{text}"

        REGRAS:
        1. Retorne APENAS o JSON, sem texto adicional
        2. Se houver múltiplos comandos separados por "e" ou "depois", retorne um array de comandos
        3. Use EXATAMENTE este formato para cada comando:
        {{
            "action": "mover|clicar|sistema",
            "direction": "cima|baixo|esquerda|direita|null",
            "distance": número em pixels (20=pouco, 50=médio, 100=muito),
            "command": "clique|duplo|fechar|minimizar|maximizar|abrir|null",
            "target": "nome do programa/arquivo se houver ou null"
        }}

        4. Todos os campos são obrigatórios
        5. Use "null" quando um campo não se aplicar
        6. Nunca deixe campos vazios ou undefined

        Exemplos de comandos únicos:
        - "um pouco para direita" 
        {{"action": "mover", "direction": "direita", "distance": 20, "command": null, "target": null}}

        - "clique duplo" 
        {{"action": "clicar", "direction": null, "distance": 0, "command": "duplo", "target": null}}

        Exemplos de comandos sequenciais:
        - "mova para direita e clique" 
        [
            {{"action": "mover", "direction": "direita", "distance": 20, "command": null, "target": null}},
            {{"action": "clicar", "direction": null, "distance": 0, "command": "clique", "target": null}}
        ]

        - "mova muito para cima depois clique duas vezes e minimize"
        [
            {{"action": "mover", "direction": "cima", "distance": 100, "command": null, "target": null}},
            {{"action": "clicar", "direction": null, "distance": 0, "command": "duplo", "target": null}},
            {{"action": "sistema", "direction": null, "distance": 0, "command": "minimizar", "target": null}}
        ]

        - "abra o chrome e maximize"
        [
            {{"action": "sistema", "direction": null, "distance": 0, "command": "abrir", "target": "chrome"}},
            {{"action": "sistema", "direction": null, "distance": 0, "command": "maximizar", "target": null}}
        ]
        """
