# Robô Aspirador Inteligente com Mapeamento e Aprendizado

Sistema completo de simulação de um robô aspirador inteligente usando PyBullet, com capacidades de mapeamento, aprendizado de rotas e integração com Node-RED.

## 📁 Estrutura do Projeto

```
robo_aspirador/
├── src/                    # Código fonte principal
│   ├── robot.py           # Classe do robô diferencial
│   ├── sensors.py         # Sistema de sensores ultrassônicos
│   ├── controller.py      # Controladores de navegação
│   ├── mapping.py         # Sistema de mapeamento
│   ├── learning.py        # Sistema de aprendizado
│   ├── logger.py          # Logger para Node-RED
│   └── environment.py     # Ambiente de simulação
│
├── tests/                 # Scripts de teste
│   ├── test_imports.py
│   ├── test-node-red.py
│   ├── testar-endpoint-simples.py
│   └── test_run.py
│
├── maps/                  # Mapas gerados (criado automaticamente)
│   └── map_exec_*.json
│
├── docs/                  # Documentação
│   ├── README.md
│   ├── QUICKSTART.md
│   └── ...
│
├── node-red/              # Arquivos de configuração Node-RED
│   └── node-red-flow-corrigido.json  # Flow completo com dashboard
│
├── scripts/               # Scripts utilitários
│   ├── visualizar_mapa.py
│   └── iniciar-node-red.bat
│
├── main.py               # Arquivo principal de execução
├── requirements.txt      # Dependências
└── .venv312/            # Ambiente virtual (não versionado)
```

## 🚀 Instalação Rápida

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Testar importações:**
```bash
python tests/test_imports.py
```

## 🎮 Uso

### Primeira Execução (Exploração)
```bash
python main.py --execution 1
```

### Execuções Subsequentes (Com Aprendizado)
```bash
python main.py --execution 2 --load-map --map-file map_exec_1.json
```

### Visualizar Mapa Gerado
```bash
pip install matplotlib
python scripts/visualizar_mapa.py maps/map_exec_1.json
```

## 📊 Características

- 🤖 **Robô Diferencial**: Base diferencial com controle de velocidade
- 📡 **Sensores Ultrassônicos**: Array de 5 sensores para detecção de obstáculos
- 🗺️ **Mapeamento de Ocupação**: Mapa 2D construído em tempo real
- 🧠 **Aprendizado de Rotas**: Otimização de trajetórias em execuções subsequentes
- 📊 **Métricas de Desempenho**: Cobertura, tempo, energia, eficiência
- 🔌 **Integração Node-RED**: Logging em tempo real via HTTP (veja [Guia Completo](docs/NODE_RED_GUIA_COMPLETO.md))

## 📚 Documentação

Consulte a pasta `docs/` para:
- **[Implementações Completas](docs/IMPLEMENTACOES_COMPLETAS.md)** - Todas as melhorias implementadas
- **[Validação Completa dos Requisitos](docs/VALIDACAO_REQUISITOS_COMPLETA.md)** - Checklist completo do que está implementado
- **[Guia Completo Node-RED](docs/NODE_RED_GUIA_COMPLETO.md)** - Configuração completa do Node-RED para projetos Python
- **[Mapeamento 2D - Explicação Técnica](docs/MAPEAMENTO_2D_EXPLICACAO.md)** - Como funciona o mapeamento 2D
- [Guia rápido de início](docs/QUICKSTART.md)
- [Instruções de instalação do Node-RED](docs/INSTALAR_NODE_RED.md)
- [Próximos passos e melhorias](docs/PROXIMOS_PASSOS.md)

## 🧪 Testes

```bash
# Testar importações
python tests/test_imports.py

# Testar Node-RED
python tests/test-node-red.py

# Testar inicialização
python tests/test_run.py
```

## 📝 Licença

Este projeto é para fins educacionais.

