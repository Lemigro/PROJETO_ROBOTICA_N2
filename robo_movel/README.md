# 🤖 Robô Móvel Diferencial

Sistema de simulação de robô móvel diferencial com evasão de obstáculos reativa, sensores ultrassônicos e navegação com trajetória de referência.

## 📋 Características

- **Evasão de obstáculos reativa**: Usa sensores ultrassônicos para detectar e desviar de obstáculos
- **Navegação inteligente**: Segue trajetória de referência enquanto evita obstáculos
- **Sensores múltiplos**: Frontais, laterais e traseiros para detecção completa
- **Visualização**: Linha amarela mostra direção do objetivo (olhos do robô)
- **Métricas em tempo real**: Monitoramento via Node-RED

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.8+
- Mosquitto MQTT Broker
- Node-RED (opcional, para dashboards)

### Instalação

```bash
# Instalar dependências
pip install -r config/requirements.txt

# Iniciar Mosquitto (Windows)
net start mosquitto

# Iniciar Node-RED
node-red
```

### Executar

```bash
# Terminal - Robô Móvel
cd robo_movel
python main.py
```

### Configurar Node-RED

1. Acesse: http://localhost:1880
2. Importe: `node_red/node_red_flow.json`
3. Faça Deploy
4. Acesse Dashboard: http://localhost:1880/ui

## 📁 Estrutura

```
robo_movel/
├── main.py                # Executar: python main.py
├── src/                    # Código fonte
│   ├── robo_movel.py
│   └── node_red_interface.py
├── config/                 # Configurações
│   ├── config.py
│   └── requirements.txt
└── node_red/              # Fluxos Node-RED
    └── node_red_flow.json
```

## 📊 Métricas (Node-RED)

- **Distância percorrida** (gráfico em tempo real)
- **Número de colisões**
- **Tempo de reação médio**
- **Erro médio lateral**
- **Distância percorrida sem impacto**

## 🔧 Configuração

Edite `config/config.py` para ajustar:
- Parâmetros PID (Kp, Ki, Kd)
- Velocidades máximas
- Alcance dos sensores
- Configurações MQTT

## 🎯 Funcionalidades

### Navegação
- Segue trajetória de referência (linha vermelha tracejada)
- Detecta e passa por brechas entre obstáculos
- Prioriza direção do objetivo (linha amarela)
- Nunca dá meia-volta (sempre avança)

### Sensores
- **Front**: Detecção frontal (2.0m)
- **Front Left/Right**: Detecção diagonal (1.5m)
- **Left/Right**: Detecção lateral (1.5m)
- **Back Left/Right**: Detecção traseira (1.0m)

### Controle
- Controlador PID para seguimento de trajetória
- Controlador PID para evasão de obstáculos
- Movimento fluido usando forças e torques físicos

## 🆘 Troubleshooting

### MQTT não conecta
```bash
# Verificar Mosquitto
sc query mosquitto
net start mosquitto
```

### Dashboard vazio
- Verifique se o robô está executando
- Verifique se o fluxo Node-RED foi importado
- Veja painel Debug do Node-RED

### Robô não segue a linha
- Verifique se há obstáculos bloqueando o caminho
- Ajuste parâmetros PID em `config/config.py` se necessário
- Verifique se o robô está detectando o objetivo (linha amarela)

