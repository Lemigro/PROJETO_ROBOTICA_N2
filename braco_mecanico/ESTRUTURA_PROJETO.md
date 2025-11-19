# 📁 Estrutura do Projeto

## Organização de Pastas

```
braco_mecanico/
│
├── src/                          # Código fonte principal
│   ├── __init__.py              # Inicialização do módulo
│   ├── manipulador_planar.py    # Manipulador 2/3 DOF
│   ├── robo_movel.py            # Robô móvel diferencial
│   └── node_red_interface.py    # Interface MQTT/Node-RED
│
├── examples/                     # Exemplos de uso
│   ├── exemplo_manipulador.py   # Exemplo do manipulador
│   └── exemplo_robo_movel.py    # Exemplo do robô móvel
│
├── config/                       # Configurações
│   ├── config.py                # Parâmetros do sistema
│   └── requirements.txt         # Dependências Python
│
├── docs/                         # Documentação
│   ├── README.md                # Documentação principal
│   ├── COMO_INICIAR.md          # Guia de início
│   ├── CONFIGURACAO_NODE_RED.md # Config Node-RED
│   └── ...                      # Outros documentos
│
├── node_red/                     # Fluxos Node-RED
│   ├── node_red_flow_organizado.json  # Fluxo recomendado
│   └── node_red_flow.json       # Fluxo alternativo
│
├── scripts/                      # Scripts utilitários
│   ├── teste_rapido.py          # Teste de importações
│   ├── testar_mqtt.py           # Teste MQTT
│   ├── iniciar_tudo.bat         # Script de inicialização
│   └── instalar_node_red.bat    # Instalação Node-RED
│
└── README.md                     # Este arquivo
```

## Como Usar

### Executar Exemplos
```bash
python examples/exemplo_manipulador.py
python examples/exemplo_robo_movel.py
```

### Executar Testes
```bash
python scripts/teste_rapido.py
python scripts/testar_mqtt.py
```

### Instalar Dependências
```bash
pip install -r config/requirements.txt
```

### Importar no Código
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from manipulador_planar import ManipuladorPlanar
from robo_movel import RoboMovel
```

## Vantagens da Estrutura

✅ **Organização clara**: Cada tipo de arquivo em sua pasta  
✅ **Fácil manutenção**: Código separado de exemplos e docs  
✅ **Escalável**: Fácil adicionar novos módulos  
✅ **Profissional**: Estrutura padrão de projetos Python  

