# Solução Final - Dashboard Node-RED

## 🔴 Problemas Identificados

1. **Gauges mostrando JSON completo** em vez de valores numéricos
2. **Gráfico de trajetória com "Bad data inject"** - formato incorreto
3. **Dados chegando corretamente** mas não sendo processados

## ✅ Solução: Importar Flow Corrigido

### Passo 1: Importar Flow Corrigido

1. No Node-RED, clique em **Menu** (☰) → **Import**
2. Selecione: `node-red/node-red-flow-corrigido.json`
3. Clique em **Import**
4. **IMPORTANTE**: Isso substitui o flow atual
5. Clique em **Deploy**

### Passo 2: Verificar

1. Recarregue o dashboard: http://localhost:1880/ui (F5)
2. Execute o projeto: `python main.py --execution 1`
3. Verifique:
   - Gauges mostrando números (não JSON)
   - Trajetória plotando sem erros

---

## 🔧 Correções Aplicadas

### 1. Função "Separar Métricas"

Adiciona um nó function que extrai valores individuais:

```javascript
const data = msg.payload;

node.send([
    {payload: data.coverage_percentage || 0},  // Para Gauge Cobertura
    {payload: data.efficiency || 0},            // Para Gauge Eficiência
    {payload: data.total_energy || 0},          // Para Gauge Energia
    {payload: {time: data.total_time || 0, coverage: data.coverage_percentage || 0}}, // Para Chart
    {payload: data}                             // Para Arquivo
]);
```

### 2. Função "Formatar Trajetória" Corrigida

```javascript
const data = msg.payload;

if (typeof data.x === 'number' && typeof data.y === 'number') {
    msg.payload = {
        x: data.x,
        y: data.y
    };
    return msg;
}

return null;
```

### 3. Chart de Trajetória

- Tipo alterado para `xy` (não `scatter`)
- Isso corrige os avisos "Bad data inject"

---

## 📋 Se Preferir Corrigir Manualmente

### 1. Adicionar Nó Function para Métricas

1. **Arraste** um nó `function` para o canvas
2. **Conecte**: Switch (saída metrics) → Function → Gauges
3. **Configure o Function**:
   - Nome: "Separar Métricas"
   - Código (cole no campo "Function"):
   ```javascript
   const data = msg.payload;
   
   node.send([
       {payload: data.coverage_percentage || 0},
       {payload: data.efficiency || 0},
       {payload: data.total_energy || 0},
       {payload: {time: data.total_time || 0, coverage: data.coverage_percentage || 0}},
       {payload: data}
   ]);
   
   return null;
   ```
   - Outputs: **5**
4. **Conecte as saídas**:
   - Saída 1 → Gauge Cobertura
   - Saída 2 → Gauge Eficiência
   - Saída 3 → Gauge Energia
   - Saída 4 → Chart Evolução
   - Saída 5 → File Métricas

### 2. Corrigir Trajetória

1. **Edite** o nó "Formatar Trajetória"
2. **Substitua** o código por:
   ```javascript
   const data = msg.payload;
   
   if (typeof data.x === 'number' && typeof data.y === 'number') {
       msg.payload = {
           x: data.x,
           y: data.y
       };
       return msg;
   }
   
   return null;
   ```

3. **Edite** o Chart "Trajetória 2D":
   - Chart Type: `xy` (mude de `scatter` para `xy`)

### 3. Deploy

Clique em **Deploy** (botão vermelho)

---

## ✅ Resultado Esperado

Após corrigir:

- ✅ **Cobertura**: `2.33%` (número, não JSON)
- ✅ **Eficiência**: `0.15` (número, não JSON)  
- ✅ **Energia**: `15.39J` (número, não JSON)
- ✅ **Trajetória**: Plotando corretamente sem avisos
- ✅ **Evolução**: Gráfico funcionando

---

## 🆘 Ainda não funciona?

1. **Limpe o cache**: Ctrl+Shift+Delete → Limpar cache
2. **Recarregue**: F5 no dashboard
3. **Verifique Deploy**: Botão deve estar verde
4. **Veja Debug**: Confirme que dados estão chegando

---

## 📁 Arquivo Criado

- `node-red/node-red-flow-corrigido.json` - Flow completo corrigido

**Importe este arquivo e faça Deploy!**

