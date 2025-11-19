# Formato Correto para Charts Node-RED Dashboard

## 📊 Formato Esperado pelo Dashboard

### Line Chart (Gráfico de Linha)

**Formato**: Objeto simples com `topic` e `payload` numérico

```javascript
{
    payload: 2.33,        // Valor numérico
    topic: 'Cobertura'    // Nome da série
}
```

**Múltiplas séries**: Envie mensagens separadas, cada uma com `topic` diferente.

### Scatter/XY Chart (Gráfico de Dispersão)

**Formato**: Objeto com `x` e `y`

```javascript
{
    payload: {
        x: 1.5,           // Coordenada X
        y: 2.3            // Coordenada Y
    },
    topic: 'Trajetória'   // Nome da série (opcional)
}
```

---

## ✅ Correções Aplicadas no Flow

### 1. Gráfico de Evolução (Line Chart)

**Antes** (errado):
```javascript
payload: [{x: now, y: coverage, series: 'Cobertura'}, ...]
```

**Agora** (correto):
```javascript
// Envia 2 mensagens separadas
{payload: coverage, topic: 'Cobertura'}
{payload: time, topic: 'Tempo'}
```

### 2. Trajetória 2D (Scatter Chart)

**Antes** (errado):
```javascript
payload: [{x: x, y: y, series: 'Trajetória'}]
```

**Agora** (correto):
```javascript
payload: {x: x, y: y}
topic: 'Trajetória'
```

### 3. Comparativo (Line Chart)

**Antes** (errado):
```javascript
payload: [{x: 1, y: coverage, series: 'Cobertura'}, ...]
```

**Agora** (correto):
```javascript
// Envia múltiplas mensagens, cada uma com topic diferente
{payload: coverage1, topic: 'Cobertura'}
{payload: time1, topic: 'Tempo'}
{payload: efficiency1, topic: 'Eficiência'}
{payload: coverage2, topic: 'Cobertura'}
...
```

---

## 🔧 Como Corrigir Manualmente

### Gráfico de Evolução

Edite o nó "Separar Métricas":

```javascript
const data = msg.payload;

node.send([
    {payload: data.coverage_percentage || 0},  // Gauge
    {payload: data.efficiency || 0},            // Gauge
    {payload: data.total_energy || 0},          // Gauge
    {payload: data.coverage_percentage || 0, topic: 'Cobertura'},  // Chart série 1
    {payload: data.total_time || 0, topic: 'Tempo'},                // Chart série 2
    {payload: data}                             // Arquivo
]);

return null;
```

**Outputs**: 6

### Trajetória 2D

Edite o nó "Formatar Trajetória":

```javascript
const data = msg.payload;

if (typeof data.x === 'number' && typeof data.y === 'number') {
    msg.payload = {
        x: data.x,
        y: data.y
    };
    msg.topic = 'Trajetória';
    return msg;
}

return null;
```

**Chart Type**: `scatter` (não `xy`)

### Comparativo

Edite o nó "Preparar Comparativo":

```javascript
const summary = msg.payload;
const execNum = summary.execution_number || 1;

let history = global.get('execution_history') || [];

history.push({
    execution: execNum,
    coverage: summary.coverage_percentage || 0,
    time: summary.total_time || 0,
    efficiency: summary.efficiency || 0
});

if (history.length > 10) {
    history = history.slice(-10);
}

global.set('execution_history', history);

// Envia cada ponto separadamente
const msgs = [];
history.forEach(h => {
    msgs.push({payload: h.coverage, topic: 'Cobertura'});
    msgs.push({payload: h.time, topic: 'Tempo'});
    msgs.push({payload: h.efficiency, topic: 'Eficiência'});
});

return msgs;
```

---

## ✅ Resultado

Após corrigir:
- ✅ **Evolução**: 2 linhas (Cobertura e Tempo)
- ✅ **Trajetória**: Pontos (x, y) plotando
- ✅ **Comparativo**: 3 linhas após 2+ execuções

---

**Importe o flow corrigido e faça Deploy!**

