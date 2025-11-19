# 🔧 Solução: Gráficos Vazios no Dashboard

## 🔴 Problema

Os gráficos não mostram dados:
- **Evolução Tempo vs Cobertura**: Vazio
- **Trajetória 2D**: Vazio  
- **Comparativo**: Vazio

## ✅ Solução Rápida

### 1. Importar Flow Corrigido

1. No Node-RED: http://localhost:1880
2. **Menu** (☰) → **Import**
3. Selecione: `node-red/node-red-flow-corrigido.json`
4. Clique em **Import**
5. Clique em **Deploy** (botão vermelho)

### 2. Recarregar Dashboard

1. Acesse: http://localhost:1880/ui
2. Pressione **F5** para recarregar

### 3. Executar Projeto

```bash
python main.py --execution 1
```

---

## 🔍 O que foi corrigido?

### 1. Gráfico de Evolução

**Antes**: Objeto simples `{time: X, coverage: Y}`  
**Agora**: Array com formato correto:
```javascript
[
    {x: timestamp, y: coverage, series: 'Cobertura'},
    {x: timestamp, y: time, series: 'Tempo'}
]
```

### 2. Trajetória 2D

**Antes**: Objeto `{x: X, y: Y}`  
**Agora**: Array com formato correto:
```javascript
[{
    x: data.x,
    y: data.y,
    series: 'Trajetória'
}]
```

### 3. Comparativo

**Antes**: 3 arrays separados  
**Agora**: 1 array combinado com todas as séries:
```javascript
[
    {x: 1, y: coverage1, series: 'Cobertura'},
    {x: 1, y: time1, series: 'Tempo'},
    {x: 1, y: efficiency1, series: 'Eficiência'},
    {x: 2, y: coverage2, series: 'Cobertura'},
    ...
]
```

---

## ✅ Resultado Esperado

Após importar e fazer Deploy:

- ✅ **Evolução**: Mostra 2 linhas (Cobertura e Tempo) ao longo do tempo
- ✅ **Trajetória**: Mostra pontos (x, y) do caminho do robô
- ✅ **Comparativo**: Mostra 3 linhas após 2+ execuções

---

## 📊 Para Ver o Comparativo

Execute múltiplas vezes:

```bash
# Execução 1
python main.py --execution 1

# Execução 2 (com aprendizado)
python main.py --execution 2 --load-map --map-file map_exec_1.json

# Execução 3
python main.py --execution 3 --load-map --map-file map_exec_2.json
```

Após a segunda execução, o gráfico comparativo mostrará as 3 linhas!

---

## 🆘 Ainda não funciona?

1. **Verifique Debug**: Veja se dados estão chegando
2. **Limpe Cache**: Ctrl+Shift+Delete → Limpar cache
3. **Recarregue**: F5 no dashboard
4. **Verifique Deploy**: Botão deve estar verde

---

**Importe o flow corrigido e faça Deploy! Os gráficos devem aparecer agora!** 🎉

