# 🤖 Projeto Integrado de Robótica e Automação — N2

**Simulações Robóticas com PyBullet + Telemetria em Node-RED**

Este repositório reúne três simulações robóticas independentes desenvolvidas em **Python** usando a engine de física **PyBullet**.
O objetivo é aplicar conceitos de **controle**, **planejamento**, **mapeamento**, **cinemática** e **comunicação**, com monitoramento em **tempo real via Node-RED**.

---

## 📋 Visão Geral

| Projeto                            | Diretório         | Descrição                               | Tecnologias-Chave                    |
| ---------------------------------- | ----------------- | --------------------------------------- | ------------------------------------ |
| 🚁 **Drone de Entregas**           | `/drone`          | Planejamento de rotas e controle de voo | TSP, Algoritmos Gulosos, PID         |
| 🧹 **Robô Aspirador**              | `/robo_aspirador` | Mapeamento e aprendizado                | Grid Mapping, SLAM simples           |
| 🦾 **Braço Mecânico & Robô Móvel** | `/braco_mecanico` | Controle e cinemática                   | PID, Cinemática Direta/Inversa, MQTT |

---

## 📂 Estrutura do Repositório

```
PROJETO_ROBOTICA_N2/
├── braco_mecanico/         # Parte 1a e 1b
│   ├── src/                # Código fonte
│   ├── examples/           # Exemplos de execução
│   ├── config/             # Configurações
│   ├── node_red/          # Fluxos Node-RED
│   ├── scripts/            # Scripts utilitários
│   └── README.md          # Documentação
├── drone/                  # Parte 3
│   ├── src/               # Código fonte
│   ├── config/            # Configurações YAML
│   ├── node_red/          # Fluxo Node-RED
│   ├── logs/              # Logs da simulação
│   └── README.md          # Documentação
├── robo_aspirador/         # Parte 2
│   ├── src/               # Código fonte
│   ├── maps/              # Mapas gerados
│   ├── node-red/          # Fluxo Node-RED
│   ├── scripts/           # Utilitários
│   ├── tests/             # Testes
│   └── README.md          # Documentação
└── README.md              # Este arquivo
```

---

# 🚀 Detalhes dos Projetos

## 1. 🚁 Drone de Entregas — Planejamento Dinâmico

Simulação em que um drone identifica pontos e entrega pacotes da forma mais eficiente possível.

### **Principais Recursos**

* Planejamento de rota baseado no **Traveling Salesperson Problem (TSP)**
* Controle de voo com **PID**
* Detecção dinâmica de pontos de entrega
* Replanejamento adaptativo durante execução
* Algoritmos: nearest_neighbor ou greedy

### **Executar**

```bash
cd drone
python main.py
```

### **Métricas no Dashboard**

- Trajetória percorrida (X, Y)
- Velocidade e altitude
- Tempo total e distância
- Número de replanejamentos
- Pontos detectados/entregues
- Eficiência de rota
- Tempo médio por ponto

---

## 2. 🧹 Robô Aspirador — Mapeamento e Aprendizado

Voltado para exploração autônoma de ambientes desconhecidos com aprendizado de rotas.

### **Características**

* Construção de **Grid Map** usando sensores ultrassônicos
* Modo *Aprendizado*: melhora o caminho com base em mapas armazenados
* Geração automática de mapas em JSON
* Dashboard em tempo real com evolução do mapa

### **Executar**

```bash
cd robo_aspirador
# Primeira execução (exploração)
python main.py --execution 1

# Execuções com aprendizado
python main.py --execution 2 --load-map --map-file maps/map_exec_1.json
```

### **Métricas no Dashboard**

- Cobertura (%) - Gauge
- Eficiência (%/J) - Gauge
- Energia consumida (J) - Gauge
- Evolução Tempo vs Cobertura - Gráfico
- Trajetória 2D (vista superior) - Scatter
- Comparativo entre execuções - Gráfico histórico

---

## 3. 🦾 Braço Mecânico & Robô Móvel

Um conjunto de simulações focadas nos fundamentos matemáticos e físicos da robótica.

### **Braço Mecânico (1a)**

* Manipulador planar (2–3 DOF)
* Controle **PID** por junta
* Cinemática direta
* Reação a perturbações
* Métricas: erro médio, tempo de estabilização, energia, overshoot

### **Robô Móvel (1b)**

* Veículo diferencial
* Lógica reativa e desvio de obstáculos
* Navegação com trajetória de referência
* Sensores ultrassônicos (frontal e laterais)
* Métricas: colisões, distância percorrida, tempo de reação, erro lateral

### **Executar**

```bash
cd braco_mecanico
# Terminal 1 - Manipulador Planar
python src/manipulador_planar.py

# Terminal 2 - Robô Móvel
python src/robo_movel.py
```

### **Comunicação MQTT**

* Envio estruturado de dados usando Mosquitto Broker
* Tópicos: `robotica_n2/manipulador_planar/metrics` e `robotica_n2/robo_movel/metrics`

---

# 🛠️ Instalação e Requisitos

## ✔ Pré-requisitos Globais

* Python **3.8+**
* Node.js (para Node-RED)
* Mosquitto MQTT Broker *(necessário para o braço mecânico)*

## ✔ Instalação

Cada projeto é independente. Instale as dependências de cada um:

```bash
# Braço Mecânico
cd braco_mecanico
pip install -r config/requirements.txt

# Drone
cd drone
pip install -r requirements.txt

# Robô Aspirador
cd robo_aspirador
pip install -r requirements.txt
```

### Iniciar Serviços

```bash
# Mosquitto MQTT (necessário para Braço Mecânico)
net start mosquitto

# Node-RED (para todos os projetos)
node-red
```

---

# 📊 Dashboard de Telemetria — Node-RED

Os três projetos fornecem dados visualizados em um **dashboard único com 4 abas separadas**.

### **Instalação**

```bash
npm install -g node-red node-red-dashboard
```

### **Executar**

```bash
node-red
```

### **Acessar**

- **Editor**: [http://localhost:1880](http://localhost:1880)
- **Dashboard**: [http://localhost:1880/ui](http://localhost:1880/ui)

### **Importar os Fluxos**

Importe os 3 fluxos no Node-RED (pode importar todos de uma vez):

1. **Braço Mecânico**: `braco_mecanico/node_red/node_red_flow_organizado.json`
   - Cria 2 abas: "Manipulador Planar" e "Robô Móvel"
   - Protocolo: **MQTT** (tópicos: `robotica_n2/manipulador_planar/metrics` e `robotica_n2/robo_movel/metrics`)

2. **Drone**: `drone/node_red/node_red_complete.json`
   - Cria 1 aba: "Drone de Entregas"
   - Protocolo: **HTTP** (endpoint: `/drone-data`)

3. **Robô Aspirador**: `robo_aspirador/node-red/node-red-flow-corrigido.json`
   - Cria 1 aba: "Robô Aspirador"
   - Protocolo: **HTTP** (endpoint: `/robo-data`)

### **Estrutura do Dashboard**

Após importar todos os fluxos, o dashboard terá **4 abas**:
- **Aba 1**: Manipulador Planar (Braço Mecânico)
- **Aba 2**: Robô Móvel (Braço Mecânico)
- **Aba 3**: Drone de Entregas
- **Aba 4**: Robô Aspirador

---

# 🎯 Execução Rápida

### Passo a Passo Completo

1. **Instalar dependências de cada projeto**
2. **Iniciar Mosquitto**: `net start mosquitto`
3. **Iniciar Node-RED**: `node-red`
4. **Importar fluxos** no Node-RED (http://localhost:1880)
5. **Executar projetos** (cada um em seu terminal)
6. **Acessar dashboard**: http://localhost:1880/ui

### Scripts Úteis

Cada projeto possui scripts próprios:
- **Braço Mecânico**: `scripts/iniciar_tudo.bat`
- **Drone**: `run.bat`
- **Robô Aspirador**: `run.bat`

# 📝 Licença e Créditos

Projeto desenvolvido para fins educacionais como parte da avaliação de **Robótica (N2)**.

## ✅ Conformidade

Este projeto está **100% conforme** com a especificação do documento de requisitos. Todos os componentes foram implementados e testados.

Sinta-se à vontade para explorar, modificar e expandir.
