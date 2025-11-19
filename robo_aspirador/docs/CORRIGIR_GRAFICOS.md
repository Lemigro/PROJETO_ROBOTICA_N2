# Corrigir Gráficos que Não Mostram Dados

## 🔴 Problema

Os gráficos estão vazios:
- **Evolução Tempo vs Cobertura**: Sem dados
- **Trajetória 2D**: Sem dados
- **Comparativo**: Sem dados (ou vazio após múltiplas execuções)

## ✅ Solução: Importar Flow Corrigido

### Passo 1: Importar Flow Atualizado

1. No Node-RED, clique em **Menu** (☰) → **Import**
2. Selecione: `node-red/node-red-flow-corrigido.json`
3. Clique em **Import**
4. Clique em **Deploy**

### Passo 2: Recarregar Dashboard

1. Acesse: http://localhost:1880/ui
2. Pressione **F5** para recarregar
3. Execute: `python main.py --execution 1`

---

## 🔧 Correções Aplicadas

### 1. Gráfico de Evolução (Tempo vs Cobertura)

**Formato correto para line chart:**
```javascript
[
    {x: timestamp, y: coverage, series: 'Cobertura'},
    {x: timestamp, y: time, series: 'Tempo'}
]
```

### 2. Trajetória 2D

**Formato correto para xy chart:**
```javascript
[{
    x: data.x,
    y: data.y,
    series: 'Trajetória'
}]
```

### 3. Comparativo Entre Execuções

**Formato correto:**
```javascript
[
    {x: execution, y: coverage, series: 'Cobertura'},
    {x: execution, y: time, series: 'Tempo'},
    {x: execution, y: efficiency, series: 'Eficiência'}
]
```

---

## 📋 Se Preferir Corrigir Manualmente

### 1. Corrigir Gráfico de Evolução

Edite o nó "Separar Métricas":

```javascript
const data = msg.payload;
const now = Date.now();

node.send([
    {payload: data.coverage_percentage || 0},
    {payload: data.efficiency || 0},
    {payload: data.total_energy || 0},
    {payload: [
        {x: now, y: data.coverage_percentage || 0, series: 'Cobertura'},
        {x: now, y: data.total_time || 0, series: 'Tempo'}
    ]},
    {payload: data}
]);

return null;
```

### 2. Corrigir Trajetória

Edite o nó "Formatar Trajetória":

```javascript
const data = msg.payload;

if (typeof data.x === 'number' && typeof data.y === 'number') {
    msg.payload = [{
        x: data.x,
        y: data.y,
        series: 'Trajetória'
    }];
    return msg;
}

return null;
```

### 3. Corrigir Comparativo

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

// Formato correto: array com objetos {x, y, series}
const allData = [
    ...history.map(h => ({x: h.execution, y: h.coverage, series: 'Cobertura'})),
    ...history.map(h => ({x: h.execution, y: h.time, series: 'Tempo'})),
    ...history.map(h => ({x: h.execution, y: h.efficiency, series: 'Eficiência'}))
];

msg.payload = allData;
return msg;
```

**Altere Outputs para 1** (não 3)

---

## ✅ Resultado Esperado

Após corrigir:

- ✅ **Evolução**: Mostra linha de cobertura e tempo ao longo do tempo
- ✅ **Trajetória**: Mostra pontos (x, y) do caminho do robô
- ✅ **Comparativo**: Mostra 3 linhas (Cobertura, Tempo, Eficiência) após 2+ execuções

---

## 🆘 Ainda não funciona?

1. **Verifique o Debug**: Veja se os dados estão chegando
2. **Verifique o formato**: Charts precisam de array com objetos {x, y, series}
3. **Recarregue**: F5 no dashboard
4. **Limpe cache**: Ctrl+Shift+Delete

---

**Importe o flow corrigido e faça Deploy!**

