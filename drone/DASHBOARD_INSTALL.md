# Instalação Rápida do Dashboard

## ⚠️ IMPORTANTE: Use APENAS um fluxo!

**NÃO coloque ambos os fluxos (example e dashboard) no mesmo Node-RED.**

## Opção Recomendada: Fluxo Completo

1. **Remova TODOS os fluxos antigos** do Node-RED
2. **Importe APENAS** o arquivo `node_red_complete.json`
3. **Deploy**
4. Acesse: **http://localhost:1880/ui**

## Passo a Passo

### 1. Limpar Node-RED
- Abra Node-RED: http://localhost:1880
- Selecione TODOS os nós (Ctrl+A ou Cmd+A)
- Delete (Delete ou Backspace)
- Clique em **Deploy**

### 2. Importar Fluxo Completo
- Menu: **Import** > **Clipboard**
- Abra o arquivo `node_red_complete.json`
- Copie TODO o conteúdo (Ctrl+A, Ctrl+C)
- Cole no Node-RED
- Clique em **Deploy**

### 3. Verificar
- Deve aparecer apenas UM nó "Drone Data" (http in)
- Deve ter vários nós de dashboard (ui_gauge, ui_chart, etc.)
- Acesse: http://localhost:1880/ui

### 4. Testar
- Execute a simulação Python: `python main.py`
- O dashboard deve começar a atualizar automaticamente

## Troubleshooting

### Dashboard vazio
1. Verifique se a simulação está rodando
2. Verifique se Node-RED está habilitado no `config.yaml`:
   ```yaml
   node_red:
     enabled: true
   ```
3. Abra o debug do Node-RED (ícone de debug no canto direito)
4. Veja se os dados estão chegando no nó "Log All Data"

### Erro "nó ausente"
- Instale Node-RED Dashboard:
  ```bash
  npm install -g node-red-dashboard
  ```
- Reinicie Node-RED

### Dados não aparecem
- Verifique o console do Node-RED para erros
- Verifique se o endpoint está correto: `/drone-data`
- Teste enviando dados manualmente via Postman ou curl

