# Como Instalar e Configurar Node-RED

## Instalação Rápida

### 1. Instalar Node-RED

Abra o PowerShell como Administrador e execute:

```powershell
npm install -g --unsafe-perm node-red
```

**OU** se der erro de permissão, tente:

```powershell
npm install -g node-red
```

### 2. Instalar Dashboard (Opcional mas Recomendado)

Para visualizações bonitas, instale o node-red-dashboard:

```powershell
npm install -g node-red-dashboard
```

### 3. Iniciar Node-RED

```powershell
node-red
```

Você verá algo como:
```
Welcome to Node-RED
===================
...
[info] Server now running at http://127.0.0.1:1880/
```

### 4. Acessar Interface

Abra o navegador em: **http://localhost:1880**

## Configuração do Flow

### Opção 1: Importar Flow Automático

1. Na interface do Node-RED, clique no menu (☰) no canto superior direito
2. Selecione **Import**
3. Cole o conteúdo do arquivo `node-red-flow.json`
4. Clique em **Deploy**

### Opção 2: Criar Manualmente

1. **HTTP In Node:**
   - Arraste um nó "http in" para a tela
   - Configure:
     - URL: `/robot-logs`
     - Method: `POST`
   - Conecte a um nó "function"

2. **Function Node:**
   - Adicione código para processar os dados recebidos
   - Separe por tipo (metrics, trajectory, summary)

3. **Debug Node:**
   - Conecte para ver os dados recebidos
   - Ative o debug no painel direito

4. **Dashboard Nodes (se instalou dashboard):**
   - Adicione nós de gauge, chart, etc.
   - Configure para mostrar métricas

## Testar Conexão

Após configurar, execute o robô:

```bash
python main.py --execution 1
```

Os dados devem aparecer no Node-RED!

## Troubleshooting

### Node-RED não inicia
- Verifique se a porta 1880 está livre
- Tente: `node-red -p 1881` (usa porta diferente)

### Dados não chegam
- Verifique se o Node-RED está rodando
- Confirme que o endpoint está em `/robot-logs`
- Veja os logs no console do Node-RED

### Dashboard não aparece
- Instale: `npm install -g node-red-dashboard`
- Reinicie o Node-RED
- Acesse: http://localhost:1880/ui

