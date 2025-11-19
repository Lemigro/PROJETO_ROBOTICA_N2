# 🔧 Corrigir Dashboard - Solução Rápida

## 🔴 Problemas

1. **Gauges mostrando JSON completo** em vez de números
2. **Trajetória com "Bad data inject"** - formato errado

## ✅ Solução: Importar Flow Corrigido

### Passo 1: No Node-RED

1. Abra: http://localhost:1880
2. Clique em **Menu** (☰) → **Import**
3. Selecione: `node-red/node-red-flow-corrigido.json`
4. Clique em **Import**
5. **IMPORTANTE**: Isso substitui o flow atual
6. Clique em **Deploy** (botão vermelho)

### Passo 2: Recarregar Dashboard

1. Acesse: http://localhost:1880/ui
2. Pressione **F5** para recarregar
3. Execute: `python main.py --execution 1`

### Passo 3: Verificar

Agora você deve ver:
- ✅ **Cobertura**: `2.33%` (número, não JSON)
- ✅ **Eficiência**: `0.15` (número, não JSON)
- ✅ **Energia**: `15.39J` (número, não JSON)
- ✅ **Trajetória**: Plotando sem erros

---

## 🔍 O que foi corrigido?

1. **Função "Separar Métricas"**: Extrai valores individuais para cada gauge
2. **Função "Formatar Trajetória"**: Formata corretamente para chart xy
3. **Chart de Trajetória**: Tipo alterado para `xy`

---

## 🆘 Se não funcionar

1. **Limpe o cache**: Ctrl+Shift+Delete → Limpar cache
2. **Recarregue**: F5 no dashboard
3. **Verifique Deploy**: Botão deve estar verde

---

**Importe o arquivo `node-red-flow-corrigido.json` e faça Deploy!**

