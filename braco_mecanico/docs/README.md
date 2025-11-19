# Projeto Robótica N2 - Braço Mecânico e Robô Móvel

Este projeto implementa dois sistemas de controle robótico usando PyBullet:

## 1a) Manipulador Planar 2/3 DOF com Controle de Posição

Simula um braço robótico articulado em plano (2 ou 3 juntas rotacionais) no PyBullet, controlado por loops PID para atingir ângulos de referência.

### Características:
- **Cinemática direta simples**: Cálculo da posição do efetuador baseado nos ângulos das juntas
- **Controle em malha fechada**: PID individual por junta
- **Reação a perturbações**: Sistema corrige erros mesmo com pesos diferentes no efetuador
- **Sensores simulados**: 
  - Encoder virtual (leitura de ângulo das juntas)
  - Torque (fornecido pelo PyBullet)
- **Atuadores**: Motores nas juntas com controle de torque
- **Métricas enviadas ao Node-RED**: 
  - Erro médio de posição
  - Tempo de estabilização
  - Energia total gasta
  - Overshoot máximo (quanto passa do objetivo)

## 1b) Robô Móvel Diferencial com Evasão de Obstáculos

Simula um robô com dois motores de tração e sensores ultrassônicos frontais e laterais, navegando e evitando colisões.

### Características:
- **Controle reativo**: Ajuste de trajetória em tempo real baseado em sensores
- **Feedback sensorial direto**: Distância detectada → velocidade diferencial
- **Simulação de ruído e atraso**: Sensores com ruído gaussiano
- **Sensores**: Ultrassônicos (distância frontal, esquerda e direita)
- **Atuadores**: Dois motores (velocidade controlada via PWM simulado)
- **Métricas enviadas ao Node-RED**: 
  - Número de colisões
  - Tempo de reação
  - Distância percorrida sem impacto
  - Erro médio lateral

## Instalação

### Requisitos:
- Python 3.8 ou superior
- PyBullet
- NumPy
- paho-mqtt (opcional, para comunicação com Node-RED)

### Instalar dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Manipulador Planar:

**Execução básica:**
```bash
python manipulador_planar.py
```

**Usando o exemplo:**
```bash
python exemplo_manipulador.py
```

O manipulador irá:
1. Inicializar com 2 juntas
2. Mover para os ângulos de referência (45° e 30°)
3. Após estabilizar, mudar para novos ângulos (90° e -45°)
4. Exibir métricas no console e enviar ao Node-RED

**Para 3 DOF:**
Edite `exemplo_manipulador.py` e descomente a linha `exemplo_3_dof()`

### Robô Móvel:

**Execução básica:**
```bash
python robo_movel.py
```

**Usando o exemplo:**
```bash
python exemplo_robo_movel.py
```

O robô irá:
1. Inicializar em um ambiente com obstáculos aleatórios
2. Navegar evitando colisões usando os sensores ultrassônicos
3. Ajustar velocidade diferencial baseado na diferença de distâncias laterais
4. Registrar métricas de desempenho

## Configuração Node-RED

As métricas são enviadas via MQTT. Para configurar:

### 1. Instalar e configurar broker MQTT (Mosquitto):
```bash
# Ubuntu/Debian
sudo apt-get install mosquitto mosquitto-clients

# Windows: Baixar de https://mosquitto.org/download/
```

### 2. Configurar Node-RED:

1. Instalar Node-RED: `npm install -g node-red`
2. Iniciar Node-RED: `node-red`
3. Adicionar nó MQTT In:
   - Broker: `localhost:1883`
   - Topic: `robotica_n2/manipulador_planar/metrics` ou `robotica_n2/robo_movel/metrics`
4. Conectar a nós de visualização (Dashboard, Chart, etc.)

### 3. Configuração no código:

Edite `config.py` ou `node_red_interface.py` para ajustar:
- Endereço do broker MQTT
- Porta
- Prefixo dos tópicos

**Nota**: Se o MQTT não estiver disponível, as métricas ainda serão exibidas no console.

## Estrutura do Projeto

```
braco_mecanico/
├── manipulador_planar.py    # Implementação do manipulador 2/3 DOF
├── robo_movel.py            # Implementação do robô móvel diferencial
├── node_red_interface.py    # Interface MQTT para Node-RED
├── config.py                # Configurações do projeto
├── exemplo_manipulador.py   # Exemplos de uso do manipulador
├── exemplo_robo_movel.py    # Exemplos de uso do robô móvel
├── requirements.txt         # Dependências Python
├── README.md               # Este arquivo
└── .gitignore              # Arquivos ignorados pelo Git
```

## Conceitos Aplicados

### Manipulador Planar:
- **Cinemática direta**: Posição do efetuador = f(ângulos das juntas)
- **Controle PID**: Erro = ângulo_referência - ângulo_medido → Torque
- **Estabilização**: Sistema converge para o estado desejado
- **Robustez**: Reage a perturbações (pesos no efetuador)

### Robô Móvel:
- **Controle reativo**: Ação baseada diretamente na percepção
- **Feedback sensorial**: Distância → velocidade diferencial
- **Evasão de obstáculos**: Algoritmo baseado em diferença de distâncias laterais
- **Comportamento emergente**: Navegação sem planejamento global

## Personalização

### Ajustar parâmetros PID:
Edite `config.py` ou modifique diretamente nos arquivos:
- `kp`: Ganho proporcional (resposta ao erro atual)
- `ki`: Ganho integral (elimina erro residual)
- `kd`: Ganho derivativo (reduz overshoot)

### Modificar ambiente:
- **Manipulador**: Altere massa do efetuador para testar perturbações
- **Robô Móvel**: Modifique número e posição dos obstáculos em `create_environment()`

## Troubleshooting

**PyBullet não instala:**
```bash
pip install --upgrade pip
pip install pybullet
```

**Erro de conexão MQTT:**
- Verifique se o broker está rodando: `mosquitto -v`
- Confirme endereço e porta em `config.py`

**Visualização não aparece:**
- Certifique-se de que `use_gui=True` na inicialização
- No Linux, pode precisar de: `sudo apt-get install python3-opengl`

## Licença

Este projeto é para fins educacionais.

