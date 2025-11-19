# Arquitetura Node-RED - Um ou Múltiplos?

## Resposta Rápida

**Use UMA instância do Node-RED e separe os projetos usando abas (tabs) ou fluxos (flows) diferentes.**

## Por quê?

### Vantagens de uma única instância:
1. ✅ **Mais simples**: Instalar e manter apenas uma instância
2. ✅ **Compartilhamento**: Broker MQTT, configurações e recursos compartilhados
3. ✅ **Organização**: Separação clara por abas/fluxos
4. ✅ **Eficiência**: Menos recursos do sistema
5. ✅ **Facilidade**: Um único ponto de acesso (localhost:1880)

### Quando usar múltiplas instâncias:
- ❌ Projetos completamente independentes
- ❌ Diferentes ambientes (dev, prod)
- ❌ Diferentes organizações/equipes
- ❌ Necessidade de isolamento total

## Organização Recomendada

### Opção 1: Abas Separadas (Recomendado)
```
Node-RED (uma instância)
├── Aba 1: Manipulador Planar
│   ├── Fluxo MQTT → Parse → Dashboard
│   └── Visualizações específicas
│
└── Aba 2: Robô Móvel
    ├── Fluxo MQTT → Parse → Dashboard
    └── Visualizações específicas
```

**Vantagens:**
- Separação visual clara
- Fácil navegação
- Cada projeto tem sua própria aba no dashboard

### Opção 2: Fluxos Separados
```
Node-RED (uma instância)
├── Flow 1: Manipulador Planar
│   └── Todos os nós do manipulador
│
└── Flow 2: Robô Móvel
    └── Todos os nós do robô
```

**Vantagens:**
- Organização por funcionalidade
- Pode desabilitar fluxos individualmente

### Opção 3: Híbrido (Abas + Fluxos)
```
Node-RED (uma instância)
├── Tab: Manipulador Planar
│   └── Flow: Manipulador Flow
│
└── Tab: Robô Móvel
    └── Flow: Robô Flow
```

## Estrutura do Arquivo JSON

O arquivo `node_red_flow_organizado.json` usa a **Opção 1 (Abas Separadas)**:

```json
{
  "id": "manipulador_tab",
  "type": "ui_tab",
  "name": "Manipulador Planar"
},
{
  "id": "robo_tab",
  "type": "ui_tab",
  "name": "Robô Móvel"
}
```

Cada projeto tem:
- **Sua própria aba** no dashboard
- **Seu próprio grupo** de visualizações
- **Seu próprio fluxo** (z: "manipulador_flow" ou "robo_flow")

## Como Funciona

### 1. Broker MQTT Compartilhado
```
MQTT Broker (localhost:1883)
├── Tópico: robotica_n2/manipulador_planar/metrics
└── Tópico: robotica_n2/robo_movel/metrics
```

Ambos os projetos usam o **mesmo broker**, mas **tópicos diferentes**.

### 2. Fluxos Separados
- **manipulador_flow**: Todos os nós do manipulador
- **robo_flow**: Todos os nós do robô

### 3. Dashboard com Abas
- **Aba "Manipulador Planar"**: Mostra apenas métricas do manipulador
- **Aba "Robô Móvel"**: Mostra apenas métricas do robô

## Adicionar Novos Projetos

Para adicionar um terceiro projeto:

1. **Criar nova aba**:
```json
{
  "id": "projeto3_tab",
  "type": "ui_tab",
  "name": "Projeto 3",
  "order": 3
}
```

2. **Criar novo fluxo**:
```json
{
  "id": "projeto3_mqtt",
  "type": "mqtt in",
  "z": "projeto3_flow",
  "topic": "robotica_n2/projeto3/metrics"
}
```

3. **Criar grupo no dashboard**:
```json
{
  "id": "projeto3_group",
  "type": "ui_group",
  "tab": "projeto3_tab"
}
```

## Comparação Visual

### Uma Instância (Recomendado)
```
┌─────────────────────────────────┐
│     Node-RED (localhost:1880)   │
├─────────────────────────────────┤
│  Tab: Manipulador │ Tab: Robô   │
│  ┌──────────────┐ │ ┌─────────┐ │
│  │ Gráficos     │ │ │ Gráficos│ │
│  │ Gauges       │ │ │ Métricas│ │
│  └──────────────┘ │ └─────────┘ │
└─────────────────────────────────┘
```

### Múltiplas Instâncias (Não Recomendado)
```
┌─────────────────┐  ┌─────────────────┐
│ Node-RED :1880  │  │ Node-RED :1881  │
│ Manipulador     │  │ Robô Móvel      │
└─────────────────┘  └─────────────────┘
```

## Recomendação Final

**Use o arquivo `node_red_flow_organizado.json`** que já está configurado com:
- ✅ Abas separadas para cada projeto
- ✅ Fluxos organizados
- ✅ Broker MQTT compartilhado
- ✅ Dashboard limpo e organizado

## Próximos Passos

1. Importe `node_red_flow_organizado.json` no Node-RED
2. Você verá duas abas no dashboard:
   - "Manipulador Planar"
   - "Robô Móvel"
3. Cada aba mostra apenas as métricas do seu projeto

## Resumo

| Aspecto | Uma Instância | Múltiplas Instâncias |
|---------|---------------|---------------------|
| Instalação | ✅ Simples | ❌ Complexa |
| Manutenção | ✅ Fácil | ❌ Difícil |
| Recursos | ✅ Eficiente | ❌ Mais recursos |
| Organização | ✅ Por abas/fluxos | ✅ Por instância |
| Compartilhamento | ✅ Fácil | ❌ Difícil |
| **Recomendado** | ✅ **SIM** | ❌ Não |

**Conclusão: Use uma instância e organize por abas!** 🎯

