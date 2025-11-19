# 🚀 Configurar Node-RED - Guia Visual

## ✅ Passo 1: Verificar Instalação

Node-RED está instalado! ✅

Agora vamos verificar o dashboard:

```bash
npm list -g node-red-dashboard
```

Se não estiver instalado:
```bash
npm install -g node-red-dashboard
```

---

## 🎯 Passo 2: Iniciar Node-RED

Execute em um terminal:

```bash
node-red
```

**OU** use o script:

```bash
scripts\iniciar-node-red.bat
```

Aguarde até ver:
```
[info] Server now running at http://127.0.0.1:1880/
```

**Mantenha este terminal aberto!**

---

## 🌐 Passo 3: Abrir Node-RED no Navegador

Abra seu navegador e acesse:

**http://localhost:1880**

Você verá a interface do Node-RED.

---

## 📥 Passo 4: Importar Flow Completo

### 4.1 Abrir Menu

1. Clique no **menu** (☰) no canto superior direito
2. Selecione **Import**

### 4.2 Importar Arquivo

1. Clique em **"select a file to import"**
2. Navegue até: `node-red/node-red-flow-completo-windows.json`
3. Selecione o arquivo
4. Clique em **Import**

### 4.3 Verificar

Você verá vários nós aparecerem no canvas:
- ✅ "Receber Dados Robô" (HTTP In)
- ✅ Gauges (Cobertura, Eficiência, Energia)
- ✅ Gráficos (Evolução, Trajetória, Comparativo)
- ✅ Nós de arquivo (Salvar dados)

---

## 🚀 Passo 5: Fazer Deploy

1. Clique no botão **Deploy** (vermelho, canto superior direito)
2. Aguarde: **"Successfully deployed"**

**Importante**: Sempre faça Deploy após mudanças!

---

## ✅ Passo 6: Testar Conexão

Em outro terminal, execute:

```bash
python tests/test-node-red.py
```

**Resultado esperado:**
```
[OK] Métricas enviadas com sucesso!
[OK] Trajetória enviada com sucesso!
[OK] Resumo enviado com sucesso!
```

**No Node-RED:**
- Abra o painel **Debug** (lado direito, ícone 🐛)
- Você deve ver os dados chegando

---

## 📊 Passo 7: Ver Dashboard

Acesse: **http://localhost:1880/ui**

Você verá:
- Gauges (Cobertura, Eficiência, Energia)
- Gráficos (vazios inicialmente)

---

## 🎮 Passo 8: Executar Projeto

Agora execute o robô:

```bash
python main.py --execution 1
```

**Durante a execução**, você verá no dashboard:
- ✅ Gauges atualizando
- ✅ Gráfico de evolução
- ✅ Trajetória sendo plotada

---

## 📁 Passo 9: Verificar Dados Salvos

Os dados são salvos em:

```
C:\temp\node-red-robot-metrics.json
C:\temp\node-red-robot-trajectory.json
C:\temp\node-red-robot-summary.json
```

---

## 🆘 Problemas Comuns

### Node-RED não inicia
- Verifique se a porta 1880 está livre
- Tente: `node-red -p 1881` (usa outra porta)

### Dashboard não aparece
- Instale: `npm install -g node-red-dashboard`
- Reinicie Node-RED
- Acesse: http://localhost:1880/ui

### Dados não chegam
- Verifique se fez **Deploy**
- Verifique se o endpoint é `/robo-data`
- Veja o painel Debug

### Arquivos não são salvos
- Crie a pasta: `mkdir C:\temp`
- Verifique permissões

---

## 📚 Documentação Completa

Para mais detalhes, veja:
- [Configurar Node-RED Passo a Passo](docs/CONFIGURAR_NODE_RED_PASSO_A_PASSO.md)
- [Guia Completo Node-RED](docs/NODE_RED_GUIA_COMPLETO.md)

---

## ✅ Pronto!

Agora o Node-RED está configurado! 🎉

Execute o projeto e veja os dados em tempo real no dashboard!

