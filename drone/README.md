# Drone de Entregas com Planejamento Dinâmico de Rotas

Projeto de simulação de drone de entregas usando PyBullet com planejamento dinâmico de rotas (TSP dinâmico).

## Características

- Simulação física em PyBullet
- Controle PID para estabilização do drone
- Detecção dinâmica de pontos de entrega
- Planejamento de rotas adaptativo (TSP dinâmico)
- Integração com Node-RED para monitoramento
- Métricas de desempenho em tempo real

## Instalação

### Requisitos

- Python 3.8 ou superior
- pip

### Instalar Dependências

```bash
pip install -r requirements.txt
```

### Testar Instalação

```bash
python test_simple.py
```

## Configuração

Edite o arquivo `config/config.yaml` para ajustar parâmetros da simulação:

- **Número de pontos**: `environment.num_delivery_points` (padrão: 10, objetivo: ~100)
- **Raio de detecção**: `sensor.detection_radius` (padrão: 3.0m)
- **Algoritmo de rota**: `route_planning.algorithm` (nearest_neighbor ou greedy)
- **Node-RED**: Configure `node_red` para habilitar/desabilitar integração

## Execução

### Simulação Completa

```bash
python main.py
```

A simulação abrirá uma janela do PyBullet mostrando:
- O drone (caixa azul)
- Pontos de entrega (cilindros vermelhos)
- Rota planejada (linhas ciano)
- Alvo atual (linha amarela)

### Comportamento

1. O drone parte da base e patrulha a área
2. Quando detecta pontos dentro do raio, os registra
3. Planeja rota otimizada para entregar em todos os pontos
4. Durante o voo, novos pontos podem ser detectados
5. Ao concluir uma entrega, replaneja a rota restante
6. Retorna à base após todas as entregas

## Estrutura do Projeto

```
drone/
├── config/
│   └── config.yaml          # Configurações do sistema
├── src/
│   ├── __init__.py
│   ├── drone_simulator.py   # Simulação PyBullet e ambiente
│   ├── pid_controller.py    # Controle PID para estabilização
│   ├── route_planner.py     # Algoritmo de planejamento de rotas
│   ├── sensor.py            # Sistema de detecção de pontos
│   └── logger.py            # Logging e integração Node-RED
├── logs/                    # Logs da simulação (criado automaticamente)
├── main.py                  # Script principal de execução
├── test_simple.py          # Testes básicos do sistema
├── requirements.txt        # Dependências Python
├── node_red_example.json   # Exemplo de fluxo Node-RED
└── README.md               # Este arquivo
```

## Node-RED

O projeto envia dados para Node-RED via HTTP/MQTT. Veja `NODE_RED_SETUP.md` para instruções detalhadas.

### Configuração Rápida

1. Instale Node-RED: `npm install -g node-red`
2. Inicie: `node-red`
3. Importe o fluxo de `node_red_example.json`
4. Configure `config/config.yaml`:
   ```yaml
   node_red:
     enabled: true
     protocol: "http"
     http:
       url: "http://localhost:1880/drone-data"
   ```

## Métricas

O sistema coleta as seguintes métricas:

- **Distância total percorrida**: Soma de todas as distâncias
- **Número de replanejamentos**: Quantas vezes a rota foi recalculada
- **Tempo médio por ponto**: Tempo desde detecção até entrega
- **Eficiência**: Razão entre distância percorrida e ideal
- **Pontos detectados/entregues**: Contadores de progresso

## Algoritmos de Rota

- **nearest_neighbor**: Escolhe sempre o ponto mais próximo (rápido, simples)
- **greedy**: Considera distância atual e média entre pontos restantes (melhor qualidade)

## Troubleshooting

### PyBullet não abre janela
- Verifique se há display disponível (X11 no Linux)
- Use `p.DIRECT` em `drone_simulator.py` para modo headless

### Node-RED não recebe dados
- Verifique se Node-RED está rodando
- Confirme a URL no `config.yaml`
- Verifique logs em `logs/drone_simulation.log`

### Drone não se move
- Ajuste ganhos PID em `config/config.yaml`
- Verifique se há pontos detectados
- Aumente `max_velocity` se necessário

