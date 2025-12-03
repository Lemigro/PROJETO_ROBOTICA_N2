# 🤖 Braço Mecânico e Robô Móvel

Sistema completo de simulação robótica com controle PID, visualização 3D e monitoramento em tempo real via Node-RED.

## 📋 Componentes

### 1. Manipulador Planar (2/3 DOF)
- Controle PID por junta
- Cinemática direta
- Reação a perturbações
- Métricas: erro médio, tempo de estabilização, energia, overshoot

### 2. Robô Móvel Diferencial
- Evasão de obstáculos reativa
- Sensores ultrassônicos (frontal e laterais)
- Navegação com trajetória de referência
- Métricas: colisões, distância percorrida, tempo de reação, erro lateral

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
# Opção 1: Script automático
.\scripts\iniciar_tudo.bat

# Opção 2: Manual
# Terminal 1 - Manipulador Planar
python examples/exemplo_manipulador.py

# Terminal 2 - Robô Móvel
python examples/exemplo_robo_movel.py
```

### Configurar Node-RED

1. Acesse: http://localhost:1880
2. Importe: `node_red/node_red_flow_organizado.json`
3. Faça Deploy
4. Acesse Dashboard: http://localhost:1880/ui

## 📁 Estrutura

```
braco_mecanico/
├── src/                    # Código fonte
│   ├── manipulador_planar.py
│   ├── robo_movel.py
│   └── node_red_interface.py
├── examples/               # Exemplos de execução
│   ├── exemplo_manipulador.py
│   └── exemplo_robo_movel.py
├── config/                 # Configurações
│   ├── config.py
│   └── requirements.txt
├── node_red/              # Fluxos Node-RED
│   └── node_red_flow_organizado.json
└── scripts/               # Scripts utilitários
    ├── iniciar_tudo.bat
    └── testar_mqtt.py
```

## 📊 Métricas (Node-RED)

### Manipulador Planar
- Erro médio de posição (gráfico + gauge)
- Tempo de estabilização (gauge)
- Energia total gasta (gauge)
- Overshoot máximo (gauge)
- Status de estabilização

### Robô Móvel
- Distância percorrida (gráfico)
- Número de colisões
- Tempo de reação médio
- Erro médio lateral

## 🔧 Configuração

Edite `config/config.py` para ajustar:
- Parâmetros PID (Kp, Ki, Kd)
- Limites de torque/velocidade
- Configurações MQTT

## 📚 Documentação Adicional

- **Como Executar**: `COMO_EXECUTAR.md`
- **Correções**: `CORRECAO_ROBO_MOVEL.md`
- **Documentação Completa**: `docs/`

## 🆘 Troubleshooting

### MQTT não conecta
```bash
# Verificar Mosquitto
sc query mosquitto
net start mosquitto
```

### Dashboard vazio
- Verifique se os projetos estão executando
- Verifique se o fluxo Node-RED foi importado
- Veja painel Debug do Node-RED

### Robô não segue a linha
- Verifique `CORRECAO_ROBO_MOVEL.md` para correções aplicadas
- Ajuste parâmetros PID se necessário
