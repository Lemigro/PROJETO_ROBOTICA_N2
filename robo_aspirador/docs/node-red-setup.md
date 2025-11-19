# Configuração Node-RED para Robô Aspirador

## Instalação do Node-RED

### Opção 1: Via npm (Recomendado)

1. **Instalar Node.js** (se ainda não tiver):
   - Baixe em: https://nodejs.org/
   - Instale a versão LTS

2. **Instalar Node-RED globalmente:**
```bash
npm install -g --unsafe-perm node-red
```

3. **Iniciar Node-RED:**
```bash
node-red
```

4. **Acessar interface:**
   - Abra o navegador em: http://localhost:1880

### Opção 2: Via Docker (Alternativa)

```bash
docker run -it -p 1880:1880 --name mynodered nodered/node-red
```

## Configuração do Flow

Após instalar, importe o flow fornecido em `node-red-flow.json` ou crie manualmente conforme instruções abaixo.

## Endpoint Esperado

O robô enviará dados para:
- **URL:** http://localhost:1880/robot-logs
- **Método:** POST
- **Content-Type:** application/json

## Estrutura dos Dados

### Métricas:
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

### Trajetória:
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

