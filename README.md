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
root/
├── drone/                  
│   ├── src/                
│   ├── config/             
│   └── README.md           
│
├── robo_aspirador/         
│   ├── src/                
│   ├── maps/               
│   └── docs/               
│
├── braco_mecanico/         
│   ├── src/
│   ├── examples/
│   └── docs/
│
└── README.md               
```

---

# 🚀 Detalhes dos Projetos

## 1. 🚁 Drone de Entregas — Planejamento Dinâmico

Simulação em que um drone identifica pontos e entrega pacotes da forma mais eficiente possível.

### **Principais Recursos**

* Planejamento de rota baseado no **Traveling Salesperson Problem (TSP)**
* Controle de voo com **PID**
* Algoritmos gulosos para otimização
* Telemetria integrada com Node-RED (posição, velocidade e progresso das entregas)

---

## 2. 🧹 Robô Aspirador — Mapeamento e Aprendizado

Voltado para exploração autônoma de ambientes desconhecidos.

### **Características**

* Construção de **Grid Map** usando sensores ultrassônicos
* Modo *Aprendizado*: melhora o caminho com base em mapas armazenados
* Geração automática de mapas em JSON
* Dashboard em tempo real com evolução do mapa

---

## 3. 🦾 Braço Mecânico & Robô Móvel

Um conjunto de simulações focadas nos fundamentos matemáticos e físicos da robótica.

### **Braço Mecânico**

* Manipulador planar (2–3 DOF)
* Controle **PID**
* Cálculo de cinemática direta e inversa
* Métricas de desempenho (erro, overshoot, torque)

### **Robô Móvel**

* Veículo diferencial
* Lógica reativa e desvio de obstáculos
* Integração com PyBullet

### **Comunicação MQTT**

* Envio estruturado de dados usando Mosquitto Broker

---

# 🛠️ Instalação e Requisitos

## ✔ Pré-requisitos Globais

* Python **3.8+**
* Node.js (para Node-RED)
* Mosquitto MQTT Broker *(necessário para o braço mecânico)*

## ✔ Instalação de um módulo

Cada projeto é independente.

```bash
cd drone
# ou
cd robo_aspirador
# ou
cd braco_mecanico

pip install -r requirements.txt
```

---

# 📊 Dashboard de Telemetria — Node-RED

Os três projetos fornecem dados visualizados num dashboard único.

### **Instalação**

```bash
npm install -g node-red
```

### **Executar**

```bash
node-red
```

### **Acessar**

[http://localhost:1880](http://localhost:1880)

### **Importar os Dashboards**

Cada pasta contém o arquivo:

```
node_red_flow.json
```

Basta importar no Node-RED.

---

# 📝 Licença e Créditos

Projeto desenvolvido para fins educacionais como parte da avaliação de **Robótica (N2)**.
Sinta-se à vontade para explorar, modificar e expandir.
