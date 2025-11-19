# 🤖 Projeto Robótica N2 - Braço Mecânico e Robô Móvel

Sistema completo de simulação robótica com controle PID, visualização 3D e monitoramento em tempo real via Node-RED.

## 📁 Estrutura do Projeto

```
braco_mecanico/
├── src/                    # Código fonte principal
│   ├── manipulador_planar.py
│   ├── robo_movel.py
│   └── node_red_interface.py
│
├── examples/               # Exemplos de uso
│   ├── exemplo_manipulador.py
│   └── exemplo_robo_movel.py
│
├── config/                 # Configurações
│   ├── config.py
│   └── requirements.txt
│
├── docs/                   # Documentação
│   ├── README.md (este arquivo)
│   ├── COMO_INICIAR.md
│   ├── CONFIGURACAO_NODE_RED.md
│   └── ... (outros docs)
│
├── node_red/              # Fluxos Node-RED
│   ├── node_red_flow_organizado.json
│   └── node_red_flow.json
│
├── scripts/               # Scripts utilitários
│   ├── teste_rapido.py
│   ├── testar_mqtt.py
│   ├── iniciar_tudo.bat
│   └── instalar_node_red.bat
│
└── README.md             # Este arquivo
```

## 🚀 Início Rápido

### 1. Instalar Dependências
```bash
pip install -r config/requirements.txt
```

### 2. Iniciar Sistema
```bash
# Windows
scripts\iniciar_tudo.bat

# Ou manualmente:
# 1. Iniciar Mosquitto
net start mosquitto

# 2. Iniciar Node-RED
node-red

# 3. Importar fluxo: node_red/node_red_flow_organizado.json

# 4. Executar sistemas
python examples/exemplo_manipulador.py
python examples/exemplo_robo_movel.py
```

### 3. Testar Sistema
```bash
# Teste rápido
python scripts/teste_rapido.py

# Teste MQTT
python scripts/testar_mqtt.py
```

### 3. Acessar Dashboard
http://localhost:1880/ui

## 📚 Documentação

- **Início Rápido**: `docs/INICIO_RAPIDO.md`
- **Guia Completo**: `docs/COMO_INICIAR.md`
- **Node-RED**: `docs/CONFIGURACAO_NODE_RED.md`
- **Ajustes**: `docs/AJUSTES_REALIZADOS.md`

## 🎯 Componentes

### 1. Manipulador Planar 2/3 DOF
- Controle PID por junta
- Cinemática direta
- Métricas: erro, tempo de estabilização, energia, overshoot

### 2. Robô Móvel Diferencial
- Evasão de obstáculos
- Sensores ultrassônicos
- Métricas: colisões, distância, tempo de reação

### 3. Node-RED Dashboard
- Visualização em tempo real
- Gráficos e gauges
- Abas separadas por projeto

## 🔧 Configuração

Edite `config/config.py` para ajustar:
- Parâmetros PID
- Limites de torque/velocidade
- Configurações MQTT

## 📖 Documentação

- **Estrutura**: `ESTRUTURA_PROJETO.md`
- **Início Rápido**: `docs/INICIO_RAPIDO.md`
- **Guia Completo**: `docs/COMO_INICIAR.md`
- **Node-RED**: `docs/CONFIGURACAO_NODE_RED.md`

## 📊 Requisitos

- Python 3.8+
- PyBullet >= 3.2.7
- Node.js (para Node-RED)
- Mosquitto MQTT Broker

## 🆘 Suporte

Veja `docs/COMO_INICIAR.md` para troubleshooting.

## 📝 Licença

Projeto educacional.

