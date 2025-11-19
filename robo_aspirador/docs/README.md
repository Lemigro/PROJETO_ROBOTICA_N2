# Robô Aspirador Inteligente com Mapeamento e Aprendizado

Sistema completo de simulação de um robô aspirador inteligente usando PyBullet, com capacidades de mapeamento, aprendizado de rotas e integração com Node-RED.

## Características

- 🤖 **Robô Diferencial**: Base diferencial com controle de velocidade independente
- 📡 **Sensores Ultrassônicos**: Array de 5 sensores para detecção de obstáculos
- 🗺️ **Mapeamento de Ocupação**: Mapa 2D construído em tempo real
- 🧠 **Aprendizado de Rotas**: Otimização de trajetórias em execuções subsequentes
- 📊 **Métricas de Desempenho**: Cobertura, tempo, energia, eficiência
- 🔌 **Integração Node-RED**: Logging em tempo real via HTTP/MQTT

## Instalação

1. **Clone ou baixe o projeto**

2. **Crie um ambiente virtual (recomendado)**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

## Uso

### Execução Básica

```bash
python main.py
```

### Opções de Linha de Comando

```bash
# Executar sem interface gráfica (mais rápido)
python main.py --no-gui

# Carregar mapa de execução anterior
python main.py --load-map --map-file map_exec_1.json

# Especificar número da execução (para aprendizado)
python main.py --execution 2 --load-map --map-file map_exec_1.json
```

### Primeira Execução

Na primeira execução, o robô explora o ambiente de forma exploratória:

```bash
python main.py --execution 1
```

### Execuções Subsequentes

Nas execuções seguintes, o robô utiliza o mapa aprendido para otimizar a rota:

```bash
# Segunda execução
python main.py --execution 2 --load-map --map-file map_exec_1.json

# Terceira execução
python main.py --execution 3 --load-map --map-file map_exec_2.json
```

## Estrutura do Projeto

```
robo_aspirador/
├── main.py              # Arquivo principal de execução
├── robot.py             # Classe do robô diferencial
├── sensors.py           # Sistema de sensores ultrassônicos
├── controller.py        # Controladores de navegação
├── mapping.py           # Sistema de mapeamento
├── learning.py          # Sistema de aprendizado
├── logger.py            # Logger para Node-RED
├── environment.py       # Ambiente de simulação
├── requirements.txt     # Dependências
└── README.md           # Este arquivo
```

## Componentes

### Robô (robot.py)
- Base diferencial com rodas independentes
- Controle de velocidade linear e angular
- Estimativa de consumo de energia

### Sensores (sensors.py)
- Array de 5 sensores ultrassônicos
- Ray casting para detecção de obstáculos
- Alcance configurável (padrão: 2m)

### Controladores (controller.py)
- **ObstacleAvoidanceController**: Evasão de obstáculos usando potential fields
- **ExplorationController**: Exploração inteligente do ambiente

### Mapeamento (mapping.py)
- Mapa de ocupação 2D (livre/ocupado/desconhecido)
- Mapa de cobertura (células visitadas)
- Registro de trajetória completa
- Salvamento/carregamento em JSON

### Aprendizado (learning.py)
- Análise de histórico de execuções
- Otimização de rotas
- Sugestões de áreas a evitar

### Logger (logger.py)
- Envio de métricas ao Node-RED via HTTP
- Suporte opcional para MQTT
- Coleta de métricas de desempenho

## Métricas Coletadas

- **Cobertura**: Porcentagem de área coberta
- **Tempo Total**: Duração da execução
- **Energia Consumida**: Estimativa baseada em velocidade e tempo
- **Colisões**: Número de colisões detectadas
- **Eficiência**: Cobertura / Energia
- **Comprimento da Trajetória**: Distância total percorrida

## Integração com Node-RED

O sistema envia logs em tempo real para o Node-RED via HTTP POST.

### 📚 Documentação Completa

- **[Guia Completo Node-RED](NODE_RED_GUIA_COMPLETO.md)** - Guia completo para configurar e usar Node-RED com projetos Python
- **[Início Rápido Node-RED](INICIO_RAPIDO_NODE_RED.md)** - Comece em 5 minutos
- [Instalar Node-RED](INSTALAR_NODE_RED.md) - Instalação passo a passo
- [Configurar Node-RED](CONFIGURAR_NODE_RED.md) - Configuração do endpoint

### Endpoint Esperado
```
POST http://localhost:1880/robo-data
```

### Formato dos Dados

**Métricas:**
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "type": "metrics",
  "data": {
    "total_time": 120.5,
    "coverage_percentage": 85.3,
    "total_energy": 150.2,
    "efficiency": 0.568
  }
}
```

**Trajetória:**
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "type": "trajectory",
  "data": {
    "x": 1.5,
    "y": 2.3,
    "yaw": 0.5,
    "sensors": [1.2, 0.8, 1.5, 1.0, 1.3]
  }
}
```

### Configuração Rápida

1. **Inicie Node-RED**: `node-red` ou `scripts\iniciar-node-red.bat`
2. **Acesse**: http://localhost:1880
3. **Crie Flow**: HTTP In (`/robo-data`, POST) → Debug
4. **Deploy**: Clique no botão vermelho
5. **Teste**: `python tests/test-node-red.py`

Veja o [Guia Completo](NODE_RED_GUIA_COMPLETO.md) para mais detalhes e recursos avançados.

## Arquivos Gerados

- `map_exec_N.json`: Mapa salvo após cada execução N
- Contém: mapa de ocupação, cobertura, trajetória completa

## Parâmetros Configuráveis

### No código (main.py):
- `max_simulation_time`: Tempo máximo de simulação (padrão: 300s)
- `num_sensors`: Número de sensores (padrão: 5)
- `max_range`: Alcance dos sensores (padrão: 2.0m)
- `safe_distance`: Distância segura até obstáculos (padrão: 0.3m)

### No ambiente (environment.py):
- Tamanho e posição dos obstáculos
- Layout do ambiente

## Melhorias de Eficiência

O sistema aprende com execuções anteriores:
- **Execução 1**: Exploração exploratória
- **Execução 2+**: Reutiliza mapa, evita áreas já cobertas
- **Métricas**: Redução de tempo e energia em execuções subsequentes

## Troubleshooting

### PyBullet não abre janela
- Verifique se está usando `--no-gui` por engano
- Certifique-se de ter drivers gráficos atualizados

### Node-RED não recebe dados
- Verifique se o Node-RED está rodando
- O sistema continua funcionando mesmo sem Node-RED (logs são silenciosamente ignorados)

### Robô fica preso
- O sistema tem detecção de "stuck" e tenta manobras de escape
- Ajuste `safe_distance` se necessário

## Próximos Passos

- [ ] Adicionar visualização do mapa em tempo real
- [ ] Implementar SLAM mais sofisticado
- [ ] Adicionar mais algoritmos de planejamento de caminho
- [ ] Dashboard Node-RED completo
- [ ] Suporte para múltiplos robôs

## Licença

Este projeto é para fins educacionais.

## Autor

Desenvolvido como parte do Projeto de Robótica N2.

