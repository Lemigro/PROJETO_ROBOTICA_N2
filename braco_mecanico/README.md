# 🤖 Braço Mecânico - Manipulador Planar

Sistema de simulação de manipulador planar com controle PID, visualização 3D e monitoramento em tempo real via Node-RED.

## 📋 Componentes

### Manipulador Planar (2/3 DOF)
- Controle PID por junta
- Cinemática direta
- Reação a perturbações
- Métricas: erro médio, tempo de estabilização, energia, overshoot

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
# Terminal - Manipulador Planar
cd braco_mecanico
python main.py
```

### Configurar Node-RED

1. Acesse: http://localhost:1880
2. Importe: `node_red/node_red_flow_organizado.json`
3. Faça Deploy
4. Acesse Dashboard: http://localhost:1880/ui

## 📁 Estrutura

```
braco_mecanico/
├── main.py                # Executar: python main.py
├── src/                   # Código fonte
│   ├── manipulador_planar.py
│   └── node_red_interface.py
├── config/                # Configurações
│   ├── config.py
│   └── requirements.txt
└── node_red/             # Fluxos Node-RED
    └── node_red_flow_organizado.json
```

## 📊 Métricas (Node-RED)

### Manipulador Planar
- Erro médio de posição (gráfico + gauge)
- Tempo de estabilização (gauge)
- Energia total gasta (gauge)
- Overshoot máximo (gauge)
- Status de estabilização

## 🔧 Configuração

Edite `config/config.py` para ajustar:
- Parâmetros PID (Kp, Ki, Kd)
- Limites de torque/velocidade
- Configurações MQTT

## 📚 Documentação Adicional

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

