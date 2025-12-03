# 🤖 Projeto Robótica N2

Sistema completo de simulação robótica com três projetos integrados: Braço Mecânico, Drone de Entregas e Robô Aspirador Inteligente.

## 📦 Projetos

### 1. 🤖 Braço Mecânico (`braco_mecanico/`)
- **Manipulador Planar 2/3 DOF**: Controle PID, cinemática direta
- **Robô Móvel Diferencial**: Evasão de obstáculos, navegação reativa
- **Protocolo**: MQTT
- **Dashboard**: 2 abas separadas no Node-RED

### 2. 🚁 Drone de Entregas (`drone/`)
- Planejamento dinâmico de rotas (TSP dinâmico)
- Detecção e entrega de pontos
- Replanejamento adaptativo
- **Protocolo**: HTTP
- **Dashboard**: 1 aba no Node-RED

### 3. 🏠 Robô Aspirador (`robo_aspirador/`)
- Mapeamento de ocupação 2D
- Aprendizado de rotas
- Otimização entre execuções
- **Protocolo**: HTTP
- **Dashboard**: 1 aba no Node-RED

## 🚀 Início Rápido

### Pré-requisitos Globais

- Python 3.8+
- Node.js (para Node-RED)
- Mosquitto MQTT Broker (para Braço Mecânico)

### Instalação Completa

```bash
# 1. Limpar e preparar (opcional)
.\limpar_tudo.bat

# 2. Iniciar todos os projetos
.\iniciar_todos_projetos.bat

# 3. Ou instalar manualmente em cada projeto:
cd braco_mecanico && pip install -r config/requirements.txt
cd ../drone && pip install -r requirements.txt
cd ../robo_aspirador && pip install -r requirements.txt
```

### Iniciar Serviços

```bash
# Mosquitto (para Braço Mecânico)
net start mosquitto

# Node-RED (para todos os projetos)
node-red
```

### Configurar Node-RED

1. Acesse: http://localhost:1880
2. Importe os 3 fluxos:
   - `braco_mecanico/node_red/node_red_flow_organizado.json`
   - `drone/node_red_complete.json`
   - `robo_aspirador/node-red/node-red-flow-corrigido.json`
3. Faça Deploy
4. Acesse Dashboard: http://localhost:1880/ui

## 📊 Dashboards

O dashboard Node-RED possui **4 abas separadas**:

1. **Manipulador Planar** - Métricas do braço robótico
2. **Robô Móvel** - Métricas do robô diferencial
3. **Drone de Entregas** - Trajetória, métricas e pontos
4. **Robô Aspirador** - Cobertura, eficiência e trajetória

## 🎯 Executar Projetos

### Braço Mecânico
```bash
cd braco_mecanico
# Terminal 1
python examples/exemplo_manipulador.py
# Terminal 2
python examples/exemplo_robo_movel.py
```

### Drone
```bash
cd drone
python main.py
```

### Robô Aspirador
```bash
cd robo_aspirador
# Primeira execução
python main.py --execution 1
# Execuções com aprendizado
python main.py --execution 2 --load-map --map-file maps/map_exec_1.json
```

## 📁 Estrutura do Projeto

```
PROJETO_ROBOTICA_N2/
├── braco_mecanico/        # Parte 1a e 1b
│   ├── src/               # Código fonte
│   ├── examples/          # Exemplos de execução
│   ├── node_red/         # Fluxo Node-RED
│   └── README.md         # Documentação
├── drone/                 # Parte 3
│   ├── src/              # Código fonte
│   ├── config/           # Configurações
│   ├── node_red_complete.json
│   └── README.md         # Documentação
├── robo_aspirador/        # Parte 2
│   ├── src/              # Código fonte
│   ├── maps/             # Mapas gerados
│   ├── node-red/         # Fluxo Node-RED
│   └── README.md         # Documentação
├── README.md             # Este arquivo
├── GUIA_LIMPEZA_E_INICIO.md
├── REVISAO_NODE_RED_ESPECIFICACAO.md
└── iniciar_todos_projetos.bat
```

## 📚 Documentação

- **Guia Completo**: `GUIA_LIMPEZA_E_INICIO.md`
- **Revisão Node-RED**: `REVISAO_NODE_RED_ESPECIFICACAO.md`
- **Troubleshooting**: `TROUBLESHOOTING_DASHBOARD_VAZIO.md`
- **Cada projeto**: Veja `README.md` dentro de cada pasta

## 🔧 Requisitos por Projeto

### Braço Mecânico
- PyBullet >= 3.2.7
- NumPy >= 1.20.0
- paho-mqtt >= 1.6.0
- Mosquitto MQTT Broker

### Drone
- PyBullet == 3.2.5
- NumPy == 1.24.3
- requests == 2.31.0
- PyYAML == 6.0.1

### Robô Aspirador
- PyBullet >= 3.2.5
- NumPy >= 1.21.0
- requests >= 2.28.0

## 🆘 Troubleshooting

### Dashboards vazios
- Verifique se os projetos estão executando
- Verifique se Node-RED está rodando
- Veja `TROUBLESHOOTING_DASHBOARD_VAZIO.md`

### MQTT não conecta
- Verifique Mosquitto: `sc query mosquitto`
- Inicie: `net start mosquitto`

### Node-RED não inicia
- Verifique Node.js: `node --version`
- Reinstale: `npm install -g node-red node-red-dashboard`

## 📝 Notas Importantes

- **Node-RED**: Uma única instância serve todos os projetos
- **Mosquitto**: Necessário apenas para Braço Mecânico
- **Dashboards**: Separados por abas, sem conflitos
- **Portas**: Node-RED (1880), Mosquitto (1883)

## 🎓 Conformidade com Especificação

✅ **100% Conforme** - Todos os requisitos do documento de especificação foram implementados. Veja `REVISAO_NODE_RED_ESPECIFICACAO.md` para detalhes.

## 📄 Licença

Projeto educacional para fins acadêmicos.

