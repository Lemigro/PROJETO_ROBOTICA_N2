# Resumo: Arquitetura Node-RED

## Resposta Direta

**Use UMA instância do Node-RED e separe os projetos por ABAS (tabs).**

## Estrutura

```
┌─────────────────────────────────────────┐
│      Node-RED (localhost:1880)         │
├─────────────────────────────────────────┤
│  Dashboard com 2 Abas:                 │
│                                          │
│  [Manipulador Planar] [Robô Móvel]     │
│  ┌──────────────────┐ ┌──────────────┐│
│  │ Gráfico Erro     │ │ Gráfico Dist.││
│  │ Gauges           │ │ Métricas      ││
│  │ Status           │ │ Colisões      ││
│  └──────────────────┘ └──────────────┘│
└─────────────────────────────────────────┘
```

## Arquivos

1. **`node_red_flow.json`** - Versão original (tudo em uma aba)
2. **`node_red_flow_organizado.json`** - **RECOMENDADO** (abas separadas)

## Como Usar

1. Importe `node_red_flow_organizado.json` no Node-RED
2. Você terá 2 abas no dashboard:
   - **"Manipulador Planar"** - Métricas do braço robótico
   - **"Robô Móvel"** - Métricas do robô

## Vantagens

✅ **Simples**: Uma instalação, um acesso  
✅ **Organizado**: Cada projeto em sua aba  
✅ **Eficiente**: Compartilha broker MQTT  
✅ **Escalável**: Fácil adicionar mais projetos  

## Adicionar Mais Projetos

Basta criar uma nova aba e fluxo no mesmo arquivo JSON!

