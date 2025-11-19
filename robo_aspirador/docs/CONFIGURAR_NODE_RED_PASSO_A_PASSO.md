# Configurar Node-RED - Passo a Passo Completo

## 🎯 Objetivo

Configurar o Node-RED para receber dados do robô, exibir dashboards e armazenar histórico.

---

## 📋 Pré-requisitos

- ✅ Node-RED instalado (`node-red --version` deve funcionar)
- ✅ Node-RED Dashboard instalado (opcional mas recomendado)

---

## 🚀 Passo 1: Iniciar Node-RED

### Opção A: Linha de Comando

```bash
node-red
```

### Opção B: Script Batch (Windows)

```bash
scripts\iniciar-node-red.bat
```

### Opção C: Em Segundo Plano

```bash
# PowerShell
Start-Process node-red
```

**Aguarde até ver:**
```
[info] Server now running at http://127.0.0.1:1880/
[info] Started flows
```

---

## 🌐 Passo 2: Acessar Interface

Abra seu navegador e acesse:

**http://localhost:1880** ou **http://127.0.0.1:1880**

Você verá a interface do Node-RED com:
- Paleta esquerda (nós disponíveis)
- Área central (canvas)
- Painel direito (informações/debug)
- Botão **Deploy** (vermelho, canto superior direito)

---

## 📥 Passo 3: Importar Flow Completo

### 3.1 Abrir Menu de Import

1. Clique no **menu** (☰) no canto superior direito
2. Selecione **Import**

### 3.2 Importar Flow

**Opção A: Importar Arquivo (Recomendado)**

1. Clique em **select a file to import**
2. Navegue até: `node-red/node-red-flow-completo-windows.json`
3. Selecione o arquivo
4. Clique em **Import**

**Opção B: Copiar e Colar**

1. Abra o arquivo `node-red/node-red-flow-completo-windows.json`
2. Copie todo o conteúdo (Ctrl+A, Ctrl+C)
3. No Node-RED, clique em **Import**
4. Cole o conteúdo na área de texto
5. Clique em **Import**

### 3.3 Verificar Importação

Após importar, você verá:
- Vários nós no canvas
- Conexões entre os nós
- Um nó "Receber Dados Robô" (HTTP In)
- Nós de dashboard (gauges, charts)
- Nós de arquivo (salvar dados)

---

## 🔧 Passo 4: Configurar Caminhos de Arquivo (Windows)

### 4.1 Editar Nós de Arquivo

Os arquivos serão salvos em `C:\temp\`. Se quiser mudar:

1. **Clique duas vezes** no nó "Salvar Métricas"
2. Altere o campo **Filename**:
   ```
   C:\temp\node-red-robot-metrics.json
   ```
   Para outro caminho, exemplo:
   ```
   C:\Users\SeuUsuario\Documents\robot-data\metrics.json
   ```
3. Clique em **Done**

4. **Repita** para:
   - "Salvar Trajetória"
   - "Salvar Resumo"

### 4.2 Criar Pasta (se necessário)

Se a pasta não existir, o Node-RED criará automaticamente. Ou crie manualmente:

```powershell
mkdir C:\temp
```

---

## 🚀 Passo 5: Fazer Deploy

1. Clique no botão **Deploy** (vermelho, canto superior direito)
2. Aguarde a mensagem: **"Successfully deployed"**

**Importante**: Sempre faça Deploy após fazer mudanças!

---

## ✅ Passo 6: Verificar Funcionamento

### 6.1 Testar Endpoint

Execute o teste:

```bash
python tests/test-node-red.py
```

Você deve ver:
```
[OK] Métricas enviadas com sucesso!
[OK] Trajetória enviada com sucesso!
[OK] Resumo enviado com sucesso!
```

### 6.2 Verificar Debug

No Node-RED:
1. Abra o painel **Debug** (lado direito, ícone 🐛)
2. Você deve ver os dados chegando

### 6.3 Verificar Dashboard

1. Acesse: **http://localhost:1880/ui**
2. Você verá:
   - Gauges (Cobertura, Eficiência, Energia)
   - Gráficos vazios (preencherão durante execução)

---

## 📊 Passo 7: Executar Projeto

Agora execute o robô:

```bash
# Primeira execução
python main.py --execution 1
```

**Durante a execução**, você verá no dashboard:
- Gauges atualizando
- Gráfico de evolução
- Trajetória sendo plotada

**Após a execução**, você verá:
- Resumo no debug
- Gráfico comparativo atualizado
- Dados salvos nos arquivos

---

## 🔍 Passo 8: Verificar Dados Salvos

### Verificar Arquivos

**Windows**:
```
C:\temp\node-red-robot-metrics.json
C:\temp\node-red-robot-trajectory.json
C:\temp\node-red-robot-summary.json
```

Abra os arquivos para ver os dados salvos (formato JSON).

---

## 🎨 Passo 9: Personalizar Dashboard (Opcional)

### Alterar Cores

1. Clique duas vezes em um nó de chart
2. Edite o campo **Colors**
3. Exemplo: `["#1f77b4", "#ff7f0e", "#2ca02c"]`
4. **Deploy**

### Alterar Tamanhos

1. Clique duas vezes em um gauge/chart
2. Ajuste **Width** e **Height**
3. **Deploy**

### Adicionar Mais Visualizações

1. Arraste nós da paleta (ui_gauge, ui_chart, etc.)
2. Conecte aos dados
3. Configure
4. **Deploy**

---

## 🐛 Troubleshooting

### Problema: "Cannot find module 'node-red-dashboard'"

**Solução**:
```bash
npm install -g node-red-dashboard
```
Reinicie Node-RED.

### Problema: Dashboard não aparece (404)

**Solução**:
1. Verifique se instalou dashboard: `npm list -g node-red-dashboard`
2. Acesse: http://localhost:1880/ui (note o `/ui`)
3. Reinicie Node-RED

### Problema: Dados não chegam

**Verificações**:
1. ✅ Node-RED está rodando?
2. ✅ Endpoint está correto? (`/robo-data`)
3. ✅ Flow foi feito Deploy?
4. ✅ Debug está ativado?

**Teste manual**:
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:1880/robo-data" -Method POST -Body '{"test":"data"}' -ContentType "application/json"
```

### Problema: Arquivos não são salvos

**Verificações**:
1. ✅ Pasta existe ou tem permissão de criação?
2. ✅ Caminho está correto?
3. ✅ Verifique logs do Node-RED no console

**Criar pasta manualmente**:
```powershell
mkdir C:\temp
```

### Problema: Gráfico comparativo vazio

**Normal**: Aparece apenas após a segunda execução.

**Verificar**:
1. Execute pelo menos 2 vezes
2. Verifique se resumos estão chegando (debug)
3. Verifique se histórico está sendo mantido

---

## 📋 Checklist de Configuração

Use este checklist:

- [ ] Node-RED instalado e rodando
- [ ] Node-RED Dashboard instalado
- [ ] Flow importado com sucesso
- [ ] Caminhos de arquivo configurados
- [ ] Deploy realizado
- [ ] Teste de conexão passou
- [ ] Dashboard acessível (http://localhost:1880/ui)
- [ ] Debug mostrando dados
- [ ] Projeto executado com sucesso
- [ ] Dados sendo salvos nos arquivos

---

## 🎯 Próximos Passos

Após configurar:

1. **Execute múltiplas vezes** para ver o aprendizado:
   ```bash
   python main.py --execution 1
   python main.py --execution 2 --load-map --map-file map_exec_1.json
   python main.py --execution 3 --load-map --map-file map_exec_2.json
   ```

2. **Observe o dashboard** durante as execuções

3. **Compare os dados** salvos nos arquivos

4. **Analise o gráfico comparativo** para ver melhorias

---

## 📚 Recursos Adicionais

- [Guia Completo Node-RED](NODE_RED_GUIA_COMPLETO.md)
- [Implementações Completas](IMPLEMENTACOES_COMPLETAS.md)
- [Início Rápido Node-RED](INICIO_RAPIDO_NODE_RED.md)

---

## ✅ Pronto!

Agora o Node-RED está configurado e pronto para receber dados do robô! 🎉
