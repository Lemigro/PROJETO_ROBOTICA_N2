# 🏠 Robô Aspirador Inteligente com Mapeamento e Aprendizado

Sistema completo de simulação de robô aspirador usando PyBullet, com mapeamento, aprendizado de rotas e integração Node-RED.

## 📋 Características

- 🤖 Robô diferencial com controle de velocidade
- 📡 5 sensores ultrassônicos para detecção de obstáculos
- 🗺️ Mapeamento de ocupação 2D em tempo real
- 🧠 Aprendizado de rotas (otimização em execuções subsequentes)
- 📊 Métricas: cobertura, tempo, energia, eficiência
- 🔌 Integração Node-RED via HTTP

## 🚀 Início Rápido

### Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Testar importações
python tests/test_imports.py
```

### Executar

```bash
# Opção 1: Script
.\run.bat 1

# Opção 2: Python direto
# Primeira execução (exploração)
python main.py --execution 1

# Execuções subsequentes (com aprendizado)
python main.py --execution 2 --load-map --map-file maps/map_exec_1.json
```

### Configurar Node-RED

1. Inicie Node-RED: `node-red`
2. Acesse: http://localhost:1880
3. Importe: `node-red/node-red-flow-corrigido.json`
4. Faça Deploy
5. Acesse Dashboard: http://localhost:1880/ui

## 📁 Estrutura

```
robo_aspirador/
├── src/
│   ├── robot.py           # Classe do robô
│   ├── sensors.py         # Sensores ultrassônicos
│   ├── controller.py      # Controladores de navegação
│   ├── mapping.py         # Sistema de mapeamento
│   ├── learning.py        # Sistema de aprendizado
│   ├── logger.py          # Logger Node-RED
│   └── environment.py     # Ambiente de simulação
├── tests/                 # Scripts de teste
├── maps/                  # Mapas gerados (auto)
├── node-red/              # Fluxo Node-RED
├── scripts/               # Utilitários
├── main.py               # Execução principal
└── requirements.txt
```

## 🎮 Uso

### Primeira Execução
```bash
python main.py --execution 1
```
- Explora o ambiente
- Gera `maps/map_exec_1.json`

### Execuções com Aprendizado
```bash
python main.py --execution 2 --load-map --map-file maps/map_exec_1.json
```
- Reutiliza mapa anterior
- Otimiza rota evitando áreas já cobertas
- Melhora eficiência

### Visualizar Mapa
```bash
python scripts/visualizar_mapa.py maps/map_exec_1.json
```

## 📊 Métricas (Node-RED)

- Cobertura (%) - Gauge
- Eficiência (%/J) - Gauge
- Energia consumida (J) - Gauge
- Evolução Tempo vs Cobertura - Gráfico
- Trajetória 2D (vista superior) - Scatter
- Comparativo entre execuções - Gráfico histórico

## 🧠 Aprendizado

O sistema aprende com execuções anteriores:
- **Execução 1**: Exploração exploratória
- **Execução 2+**: Reutiliza mapa, evita áreas já cobertas
- **Resultado**: Redução de tempo e energia, aumento de eficiência

## 🆘 Troubleshooting

### PyBullet não abre
- Verifique drivers gráficos
- Use `--no-gui` para modo headless

### Node-RED não recebe dados
- Verifique se Node-RED está rodando
- Confirme endpoint: `http://localhost:1880/robo-data`
- Teste: `python tests/test-node-red.py`

### Mapa não é gerado
- Verifique permissões de escrita na pasta `maps/`
- Execute pelo menos uma vez completamente
