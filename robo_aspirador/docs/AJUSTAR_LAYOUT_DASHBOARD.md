# Ajustar Layout do Dashboard - Gráficos Lado a Lado

## 📐 Sistema de Grid do Node-RED Dashboard

O dashboard usa um sistema de **12 colunas**:
- `width: 12` = Largura total (100%)
- `width: 6` = Metade da largura (50%)
- `width: 4` = Um terço (33%)
- `width: 3` = Um quarto (25%)

## ✅ Layout Ajustado

### Gauges (Linha 1)
- **Cobertura**: `width: 4` (33%)
- **Eficiência**: `width: 4` (33%)
- **Energia**: `width: 4` (33%)
- **Total**: 12 colunas = 3 gauges lado a lado ✅

### Gráficos (Linha 2)
- **Evolução**: `width: 6` (50%)
- **Trajetória**: `width: 6` (50%)
- **Total**: 12 colunas = 2 gráficos lado a lado ✅

### Comparativo (Linha 3)
- **Comparativo**: `width: 12` (100%)
- Ocupa toda a largura (gráfico maior)

---

## 🔧 Como Ajustar Manualmente

### 1. Editar Largura dos Widgets

1. **Clique duas vezes** no widget (gauge ou chart)
2. No campo **Width**, altere:
   - `0` = Largura automática (ocupa tudo)
   - `4` = 33% da largura
   - `6` = 50% da largura
   - `12` = 100% da largura
3. Clique em **Done**
4. **Deploy**

### 2. Layout Recomendado

**Linha 1 - Gauges (3 lado a lado)**:
- Gauge 1: `width: 4`, `order: 1`
- Gauge 2: `width: 4`, `order: 2`
- Gauge 3: `width: 4`, `order: 3`

**Linha 2 - Gráficos (2 lado a lado)**:
- Evolução: `width: 6`, `order: 4`
- Trajetória: `width: 6`, `order: 5`

**Linha 3 - Comparativo (largura total)**:
- Comparativo: `width: 12`, `order: 6`

---

## 📊 Outros Layouts Possíveis

### Opção 1: Todos os Gráficos Lado a Lado (3 colunas)

```
Evolução (4) | Trajetória (4) | Comparativo (4)
```

Configure:
- Evolução: `width: 4`
- Trajetória: `width: 4`
- Comparativo: `width: 4`

### Opção 2: Gráficos Empilhados (largura total)

```
Evolução (12)
Trajetória (12)
Comparativo (12)
```

Configure todos com: `width: 12`

### Opção 3: Layout Atual (Recomendado)

```
Gauges: [4] [4] [4]
Gráficos: [6] [6]
Comparativo: [12]
```

---

## ✅ Resultado

Após ajustar:
- ✅ **3 Gauges** lado a lado na primeira linha
- ✅ **2 Gráficos** lado a lado na segunda linha
- ✅ **Comparativo** ocupa toda a largura na terceira linha

---

## 🎨 Dica: Altura dos Gráficos

Você também pode ajustar a altura:
- `height: 4` = Altura média
- `height: 6` = Altura maior
- `height: 0` = Altura automática

---

**O flow já foi atualizado com o layout lado a lado!**  
**Importe novamente e faça Deploy para ver as mudanças!**

