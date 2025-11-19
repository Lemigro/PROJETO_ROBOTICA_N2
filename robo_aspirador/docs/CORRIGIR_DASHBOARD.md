# Corrigir Dashboard - Gauges Mostrando JSON

## 🔴 Problema

Os gauges estão mostrando o objeto JSON completo em vez dos valores numéricos:
```
{"total_time":22.96,"coverage_percentage":2.32,...}%
```

## ✅ Solução

### Opção 1: Importar Flow Corrigido (Recomendado)

1. **No Node-RED**, clique em **Menu** (☰) → **Import**
2. Selecione: `node-red/node-red-flow-corrigido.json`
3. Clique em **Import**
4. **IMPORTANTE**: Isso vai substituir o flow atual
5. Clique em **Deploy**

### Opção 2: Corrigir Manualmente

1. **Adicione um nó Function** entre "Separar por Tipo" e os Gauges:
   - Arraste um nó `function` para o canvas
   - Conecte a saída "metrics" do switch ao function
   - Conecte o function aos gauges

2. **Configure o Function**:
   - Nome: "Separar Métricas"
   - Código:
   ```javascript
   const data = msg.payload;
   
   // Envia valores separados
   node.send([
       {payload: data.coverage_percentage || 0},
       {payload: data.efficiency || 0},
       {payload: data.total_energy || 0},
       {payload: {time: data.total_time || 0, coverage: data.coverage_percentage || 0}}
   ]);
   
   return null;
   ```
   - Outputs: 4
   - Conecte cada saída ao gauge correspondente

3. **Configure cada Gauge**:
   - **Gauge Cobertura**: Recebe `data.coverage_percentage`
   - **Gauge Eficiência**: Recebe `data.efficiency`
   - **Gauge Energia**: Recebe `data.total_energy`

4. **Deploy**

### Opção 3: Corrigir Trajetória 2D

O gráfico de trajetória também precisa de correção:

1. **Edite o nó "Formatar Trajetória"**:
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

2. **Configure o Chart de Trajetória**:
   - Chart Type: `xy` (não `scatter`)
   - Isso corrige os avisos "Bad data inject"

3. **Deploy**

---

## 📋 Passos Completos

1. ✅ Importar `node-red-flow-corrigido.json`
2. ✅ Fazer Deploy
3. ✅ Recarregar dashboard: http://localhost:1880/ui
4. ✅ Executar projeto: `python main.py --execution 1`
5. ✅ Verificar gauges mostrando valores numéricos

---

## ✅ Resultado Esperado

Após corrigir, você verá:
- **Cobertura**: `2.33%` (número, não JSON)
- **Eficiência**: `0.15` (número, não JSON)
- **Energia**: `15.39J` (número, não JSON)
- **Trajetória**: Plotando corretamente sem avisos

---

## 🆘 Ainda não funciona?

1. **Limpe o cache do navegador** (Ctrl+Shift+Delete)
2. **Recarregue a página** do dashboard (F5)
3. **Verifique o debug** no Node-RED para ver os dados chegando
4. **Verifique se o Deploy foi feito** (botão deve estar verde)

