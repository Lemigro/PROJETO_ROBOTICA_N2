# Debug: Trajetória e Comparativo Não Aparecem

## 🔍 Problema

Os gráficos de **Trajetória do Robô** e **Comparativo Entre Execuções** não estão exibindo dados.

---

## ✅ Correções Aplicadas

### 1. Adicionados Debug Nodes

- **Trajetória Debug**: Mostra os dados recebidos antes do chart
- **Resumo Debug**: Mostra os dados do resumo antes do comparativo

### 2. Melhorias nas Funções

- **Formatar Trajetória**: Adicionado validação e mensagens de erro
- **Preparar Comparativo**: Adicionado debug e validação

### 3. Ajustes nos Charts

- **removeOlder**: Desabilitado (0) para não remover dados
- **nodata**: Mensagens informativas quando não há dados

---

## 🧪 Como Testar

### Passo 1: Importar Flow Atualizado

1. No Node-RED: http://localhost:1880
2. Menu (☰) → Import
3. Selecione: `node-red/node-red-flow-corrigido.json`
4. Clique em Import
5. Clique em Deploy

### Passo 2: Verificar Debug

1. Abra o painel de Debug (ícone de bug no canto superior direito)
2. Execute o robô: `python main.py --execution 1`
3. Verifique se aparecem mensagens nos debug nodes:
   - **Trajetória Debug**: Deve mostrar objetos com `{x: number, y: number}`
   - **Resumo**: Deve mostrar o resumo da execução

### Passo 3: Verificar Logs

No console do Node-RED (terminal onde está rodando), verifique se há:
- Avisos sobre dados de trajetória
- Avisos sobre dados de comparativo

---

## 🔧 Possíveis Problemas

### Problema 1: Trajetória Não Aparece

**Causa**: Dados não estão chegando ou formato incorreto

**Solução**:
1. Verifique o debug "Trajetória Debug"
2. Se não aparecer nada, verifique se o Python está enviando dados
3. Se aparecer dados, verifique o formato: deve ser `{x: number, y: number}`

**Formato Esperado**:
```javascript
{
    payload: {
        x: 1.5,  // número
        y: 2.3   // número
    },
    topic: 'Trajetória'
}
```

### Problema 2: Comparativo Não Aparece

**Causa**: Precisa de pelo menos 2 execuções

**Solução**:
1. Execute pelo menos 2 vezes:
   ```bash
   python main.py --execution 1
   python main.py --execution 2
   ```
2. Verifique o debug "Resumo" - deve aparecer dados
3. Verifique o histórico global: `global.get('execution_history')`

**Formato Esperado**:
```javascript
// Múltiplas mensagens, cada uma com topic diferente
{payload: 45.2, topic: 'Cobertura'}
{payload: 120.5, topic: 'Tempo'}
{payload: 0.37, topic: 'Eficiência'}
// ... repetido para cada execução
```

---

## 📊 Verificar Dados Manualmente

### No Node-RED

1. Abra o painel de Debug
2. Execute o robô
3. Verifique as mensagens:
   - **Trajetória Debug**: Deve mostrar `{x: ..., y: ...}`
   - **Resumo**: Deve mostrar `{execution_number: ..., coverage_percentage: ..., ...}`

### No Python

Verifique se os dados estão sendo enviados:
- `log_trajectory_point()` é chamado periodicamente
- `log_execution_summary()` é chamado no final

---

## 🎯 Próximos Passos

Se os dados estão chegando mas não aparecem nos gráficos:

1. **Verifique o tipo do chart**:
   - Trajetória: `scatter`
   - Comparativo: `line`

2. **Verifique a configuração**:
   - Ambos devem ter `removeOlder: 0`
   - Ambos devem ter `nodata` configurado

3. **Teste com dados manuais**:
   - Use um nó `inject` para enviar dados de teste
   - Formato: `{payload: {x: 1, y: 2}, topic: 'Trajetória'}`

---

## 📝 Notas

- **Trajetória**: Dados são enviados durante a execução (a cada `log_interval` steps)
- **Comparativo**: Dados são enviados apenas no final de cada execução
- **Comparativo precisa de 2+ execuções** para mostrar algo

---

**Importe o flow atualizado e verifique os debug nodes!**

