# Dashboard Node-RED - Drone de Entregas

Este guia explica como configurar o dashboard visual para monitorar o drone de entregas em tempo real.

## Pré-requisitos

1. Node-RED instalado e rodando
2. Node-RED Dashboard instalado

## Instalação do Node-RED Dashboard

Se ainda não tiver o Node-RED Dashboard instalado, execute no terminal do Node-RED:

```bash
npm install -g node-red-dashboard
```

Ou através da interface do Node-RED:
1. Menu: **Manage Palette** (ícone de três linhas no canto superior direito)
2. Aba: **Install**
3. Busque: `node-red-dashboard`
4. Clique em **Install**

## Importar o Dashboard

1. Abra o Node-RED: http://localhost:1880
2. Menu: **Import** > **Clipboard**
3. Cole o conteúdo do arquivo `node_red_dashboard.json`
4. Clique em **Deploy** (botão vermelho no canto superior direito)

## Acessar o Dashboard

Após fazer o deploy, acesse o dashboard em:

**http://localhost:1880/ui**

## Componentes do Dashboard

O dashboard inclui:

### 1. **Trajetória do Drone**
   - Gráfico de linha mostrando a posição X e Y do drone ao longo do tempo
   - Atualização em tempo real

### 2. **Velocidade**
   - Gauge mostrando a velocidade atual do drone (m/s)
   - Cores: Verde (0-2 m/s), Amarelo (2-3.5 m/s), Vermelho (>3.5 m/s)

### 3. **Métricas da Simulação**
   - Tempo total decorrido
   - Distância total percorrida
   - Número de replanejamentos
   - Eficiência (%)

### 4. **Status**
   - Pontos detectados
   - Pontos entregues
   - Tamanho da rota atual

### 5. **Contadores Visuais**
   - **Pontos Detectados**: Gauge circular
   - **Pontos Entregues**: Gauge circular
   - **Replanejamentos**: Gauge circular

### 6. **Tabela de Pontos**
   - Lista todos os pontos detectados
   - Mostra: ID, Posição (X, Y, Z), Status (Pendente/Entregue), Hora da detecção

## Estrutura de Dados

O dashboard recebe dados no formato:

```json
{
  "event": "state|detection|delivery|replan",
  "data": { ... },
  "metrics": { ... }
}
```

## Personalização

Você pode personalizar o dashboard editando os nós no Node-RED:

1. Clique duas vezes em qualquer widget
2. Ajuste cores, tamanhos, limites, etc.
3. Clique em **Deploy** para aplicar mudanças

## Troubleshooting

### Dashboard não aparece
- Verifique se o Node-RED Dashboard está instalado
- Verifique se fez o deploy do fluxo
- Acesse http://localhost:1880/ui (não apenas /)

### Dados não aparecem
- Verifique se a simulação está rodando
- Verifique se o Node-RED está habilitado no `config.yaml`:
  ```yaml
  node_red:
    enabled: true
    protocol: "http"
    http:
      url: "http://localhost:1880/drone-data"
  ```
- Verifique o console do Node-RED para erros

### Widgets não atualizam
- Verifique se os dados estão chegando (use o debug node)
- Verifique se os tópicos estão corretos
- Limpe o cache do navegador

## Próximos Passos

Você pode adicionar:
- Gráfico de altitude ao longo do tempo
- Mapa 2D mostrando posição do drone e pontos
- Gráfico de energia consumida
- Histórico de eventos
- Alertas e notificações

