<h1 align="center">🖱️ MouseControler</h1>

<p align="center">
  Mouse virtual controlado por <b>detecção facial e movimento dos olhos</b> — operar o computador sem usar as mãos.<br>
  Projeto de pesquisa em <b>tecnologia assistiva</b> desenvolvido no IFTM.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/MediaPipe-0097A7?style=for-the-badge&logo=google&logoColor=white" alt="MediaPipe" />
  <img src="https://img.shields.io/badge/PyAutoGUI-2C2C2C?style=for-the-badge&logo=windowsterminal&logoColor=white" alt="PyAutoGUI" />
</p>

---

## 🎯 Motivação

Pessoas com mobilidade reduzida nos membros superiores dependem de periféricos caros ou adaptações improvisadas para usar um computador. O MouseControler propõe uma alternativa acessível: **uma webcam comum é suficiente**. A posição do rosto move o cursor e o piscar dos olhos executa os cliques.

## ✨ Funcionalidades

- 🎥 **Rastreamento facial em tempo real** com a malha de 468 pontos do MediaPipe Face Mesh
- 🖱️ **Movimento do cursor** proporcional à inclinação e à posição da cabeça
- 👁️ **Clique por piscada** — detecção da razão de abertura dos olhos para disparar o clique
- ✋ **Detecção de mãos** como modo alternativo de comando
- 🪟 **Interface gráfica** em ttkbootstrap para calibrar sensibilidade e iniciar/parar o rastreamento
- 📦 **Empacotamento em executável** com cx_Freeze / PyInstaller

## 📂 Estrutura do projeto

```
.
├── Software/                  # Versão com interface gráfica
│   ├── interface.py           # Janela principal (ttkbootstrap)
│   ├── detector.py            # Pipeline de detecção e controle do cursor
│   ├── detectorFace.py        # Rastreamento facial (MediaPipe Face Mesh)
│   └── icon.svg / icon.jpg    # Identidade visual do app
├── Codigo/                    # Protótipos e versões de linha de comando
│   ├── MouseFace.py
│   ├── MouseFaceComInterface.py
│   └── MouseTeste.py
├── Testes1/ e testes/         # Experimentos de calibração e detecção de mãos
├── MouseCabeçaPontos.py       # Estudo dos pontos de referência da cabeça
├── interface.spec             # Configuração de build do executável
└── requirements.txt           # Dependências fixadas
```

## 🚀 Como executar

### Pré-requisitos

- Python 3.10 ou superior
- Webcam

### Instalação

```bash
git clone https://github.com/RobertoBuiatti/MouseControler.git
cd MouseControler

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### Execução

```bash
python Software/interface.py
```

### Gerar o executável

```bash
python setup.py build
```

## 🧠 Como funciona

1. O OpenCV captura os quadros da webcam.
2. O MediaPipe Face Mesh devolve os pontos de referência do rosto a cada quadro.
3. O deslocamento do ponto central do rosto é convertido em coordenadas de tela.
4. O PyAutoGUI move o cursor para essas coordenadas com suavização, evitando tremores.
5. A razão de abertura das pálpebras é monitorada — quando cai abaixo do limiar por tempo suficiente, um clique é disparado.

## 🧱 Stack

| Biblioteca | Papel |
| --- | --- |
| OpenCV | Captura e pré-processamento de vídeo |
| MediaPipe | Malha facial e detecção de mãos |
| PyAutoGUI | Controle do cursor e cliques do sistema |
| ttkbootstrap | Interface gráfica |
| NumPy / SciPy | Cálculos de distância e suavização |
| cx_Freeze | Empacotamento em executável |

## ⚠️ Observações

- A precisão depende da iluminação do ambiente e do posicionamento da webcam.
- Recomenda-se calibrar a sensibilidade antes do uso prolongado.

## 🗺️ Próximos passos

- [ ] Perfis de calibração salvos por usuário
- [ ] Clique direito e arraste por gestos
- [ ] Teclado virtual integrado

## 👤 Autor

**Roberto Buiatti** — projeto de pesquisa no IFTM  
[GitHub](https://github.com/RobertoBuiatti) · [LinkedIn](https://www.linkedin.com/in/roberto-buiatti-10b403143)
