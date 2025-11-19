# Configuração do Node-RED

Este documento descreve como configurar o Node-RED para receber e visualizar dados do drone de entregas.

## Instalação do Node-RED

```bash
npm install -g node-red
```

## Instalação do Node-RED Dashboard

Para ter um dashboard visual completo, instale o Node-RED Dashboard:

```bash
npm install -g node-red-dashboard
```

Ou através da interface do Node-RED:
1. Menu: **Manage Palette** > **Install**
2. Busque: `node-red-dashboard`
3. Clique em **Install**

## Iniciar Node-RED

```bash
node-red
```

Acesse: http://localhost:1880

## Importar Fluxo

### Opção 1: Dashboard Completo (Recomendado)

1. Abra o Node-RED
2. Menu: Import > Clipboard
3. Cole o conteúdo do arquivo `node_red_dashboard.json`
4. Clique em "Deploy"
5. Acesse o dashboard em: **http://localhost:1880/ui**

### Opção 2: Fluxo Básico (Apenas Debug)

1. Abra o Node-RED
2. Menu: Import > Clipboard
3. Cole o conteúdo do arquivo `node_red_example.json`
4. Clique em "Deploy"

**Veja `DASHBOARD_SETUP.md` para mais detalhes sobre o dashboard visual.**

## Endpoints

### HTTP Endpoint
- URL: `http://localhost:1880/drone-data`
- Método: POST
- Content-Type: application/json

### Estrutura de Dados

O drone envia eventos no formato:

```json
{
  "event": "detection|delivery|replan|state",
  "data": { ... },
  "metrics": { ... }
}
```

### Eventos

1. **detection**: Novo ponto detectado
   ```json
   {
     "event": "detection",
     "data": {
       "type": "detection",
       "timestamp": 1234567890.123,
       "point_id": 1,
       "point_position": [10.0, 5.0, 0.1],
       "drone_position": [9.5, 4.8, 2.0]
     }
   }
   ```

2. **delivery**: Entrega concluída
   ```json
   {
     "event": "delivery",
     "data": {
       "type": "delivery",
       "timestamp": 1234567890.123,
       "point_id": 1,
       "point_position": [10.0, 5.0, 0.1],
       "drone_position": [10.0, 5.0, 0.5]
     }
   }
   ```

3. **replan**: Replanejamento de rota
   ```json
   {
     "event": "replan",
     "data": {
       "type": "replan",
       "timestamp": 1234567890.123,
       "reason": "route_completion",
       "route_length": 5,
       "route_points": [1, 3, 2, 4, 5]
     }
   }
   ```

4. **state**: Estado atual do drone
   ```json
   {
     "event": "state",
     "data": {
       "timestamp": 1234567890.123,
       "drone_position": [10.0, 5.0, 2.0],
       "drone_velocity": [1.0, 0.5, 0.0],
       "target_position": [12.0, 6.0, 2.0],
       "route_length": 3,
       "detected_points_count": 5,
       "delivered_points_count": 2
     },
     "metrics": {
       "elapsed_time": 120.5,
       "total_distance": 150.3,
       "replan_count": 3,
       "points_detected": 5,
       "points_delivered": 2,
       "avg_delivery_time": 15.2,
       "efficiency": 0.85
     }
   }
   ```

## Dashboard

O fluxo exemplo inclui:
- Contadores de eventos (detecções, entregas, replanejamentos)
- Armazenamento de estado em arquivo
- Logs de debug

Para criar dashboards visuais mais avançados, instale o node-red-dashboard:

```bash
npm install node-red-dashboard
```

## MQTT (Alternativa)

Se preferir usar MQTT ao invés de HTTP:

1. Configure o broker MQTT no Node-RED
2. Altere `config/config.yaml`:
   ```yaml
   node_red:
     enabled: true
     protocol: "mqtt"
     mqtt:
       broker: "localhost"
       port: 1883
       topic: "drone/delivery"
   ```

3. Adicione um nó MQTT In no Node-RED para receber os dados

