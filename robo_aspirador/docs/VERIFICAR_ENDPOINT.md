# Verificar Endpoint Node-RED

## 🔍 Problema: Timeout ao Testar

Se o teste dá timeout, verifique:

### 1. Node-RED está rodando?

Veja no terminal onde iniciou o Node-RED:
```
[info] Server now running at http://127.0.0.1:1880/
[info] Started flows
```

### 2. Flow foi importado e deployado?

No Node-RED (http://localhost:1880):
1. Verifique se há nós no canvas
2. Verifique se há um nó "http in" com URL `/robo-data`
3. Verifique se o botão Deploy está verde (não vermelho)

### 3. Endpoint está correto?

O endpoint deve ser: `/robo-data` (não `/robot-logs`)

### 4. Teste Manual no Node-RED

1. Abra o Node-RED: http://localhost:1880
2. Clique duas vezes no nó "Receber Dados Robô" (HTTP In)
3. Verifique:
   - **URL**: `/robo-data`
   - **Method**: `POST`
4. Clique em **Done**
5. Clique em **Deploy**

### 5. Verificar Debug

1. No Node-RED, abra o painel **Debug** (lado direito)
2. Ative o debug (ícone 🐛)
3. Execute o teste: `python tests/test-node-red.py`
4. Veja se os dados aparecem no debug

---

## ✅ Solução Rápida

1. **Abra Node-RED**: http://localhost:1880
2. **Verifique se há um flow importado**
3. **Se não houver, importe**:
   - Menu (☰) → Import
   - Selecione: `node-red/node-red-flow-completo-windows.json`
   - Import → Deploy
4. **Teste novamente**: `python tests/test-node-red.py`

---

## 🆘 Ainda não funciona?

Crie um flow mínimo manualmente:

1. Arraste `http in` para o canvas
2. Configure:
   - **URL**: `/robo-data`
   - **Method**: `POST`
3. Arraste `debug` para o canvas
4. Conecte `http in` ao `debug`
5. Clique em **Deploy**
6. Teste: `python tests/test-node-red.py`
7. Veja os dados no painel Debug
