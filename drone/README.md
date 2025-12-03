# 🚁 Drone de Entregas com Planejamento Dinâmico de Rotas

Simulação de drone de entregas usando PyBullet com planejamento dinâmico de rotas (TSP dinâmico).

## 📋 Características

- Simulação física em PyBullet
- Controle PID para estabilização
- Detecção dinâmica de pontos de entrega
- Planejamento de rotas adaptativo (TSP dinâmico)
- Replanejamento durante execução
- Integração com Node-RED para monitoramento

## 🚀 Início Rápido

### Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Testar instalação
python test_simple.py
```

### Executar

```bash
# Opção 1: Script
.\run.bat

# Opção 2: Direto
python main.py
```

### Configurar Node-RED

1. Inicie Node-RED: `node-red`
2. Acesse: http://localhost:1880
3. Importe: `node_red_complete.json`
4. Configure `config/config.yaml`:
   ```yaml
   node_red:
     enabled: true
     protocol: "http"
     http:
       url: "http://localhost:1880/drone-data"
   ```
5. Acesse Dashboard: http://localhost:1880/ui

## 📁 Estrutura

```
drone/
├── src/
│   ├── drone_simulator.py   # Simulação PyBullet
│   ├── pid_controller.py    # Controle PID
│   ├── route_planner.py     # Planejamento de rotas
│   ├── sensor.py            # Detecção de pontos
│   └── logger.py            # Integração Node-RED
├── config/
│   └── config.yaml          # Configurações
├── main.py                  # Execução principal
├── node_red_complete.json   # Fluxo Node-RED
└── requirements.txt
```

## ⚙️ Configuração

Edite `config/config.yaml`:

- **Número de pontos**: `environment.num_delivery_points` (padrão: 10)
- **Raio de detecção**: `sensor.detection_radius` (padrão: 3.0m)
- **Algoritmo de rota**: `route_planning.algorithm` (nearest_neighbor ou greedy)
- **Node-RED**: Habilitar/desabilitar integração

## 🎯 Comportamento

1. Drone parte da base e patrulha a área
2. Detecta pontos de entrega dentro do raio
3. Planeja rota otimizada (TSP)
4. Durante o voo, novos pontos podem ser detectados
5. Ao concluir entrega, replaneja rota restante
6. Retorna à base após todas as entregas

## 📊 Métricas (Node-RED)

- Trajetória percorrida (gráfico X, Y)
- Velocidade e altitude (gauges)
- Tempo total e distância total
- Número de replanejamentos
- Pontos detectados/entregues
- Eficiência de rota (gauge)
- Tempo médio por ponto
- Tabela de pontos visitados

## 🔧 Algoritmos de Rota

- **nearest_neighbor**: Escolhe sempre o ponto mais próximo (rápido)
- **greedy**: Considera distância atual e média entre pontos (melhor qualidade)

## 🆘 Troubleshooting

### PyBullet não abre janela
- Verifique drivers gráficos
- Use modo headless se necessário

### Node-RED não recebe dados
- Verifique se Node-RED está rodando
- Confirme URL no `config.yaml`
- Verifique logs em `logs/drone_simulation.log`

### Drone não se move
- Ajuste ganhos PID em `config.yaml`
- Verifique se há pontos detectados
- Aumente `max_velocity` se necessário
