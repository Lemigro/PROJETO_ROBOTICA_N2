# Node-RED Reinstalado com Sucesso! ✅

## Agora você pode iniciar o Node-RED

### Iniciar Node-RED:

```powershell
node-red
```

OU use o arquivo:
```powershell
.\iniciar-node-red.bat
```

### O que você verá:

1. Mensagens no terminal indicando que está iniciando
2. Algo como: `Server now running at http://127.0.0.1:1880/`
3. Abra o navegador em: **http://localhost:1880**

## Configuração Rápida

### 1. Importar Flow Básico

1. Na interface do Node-RED, clique no **menu (☰)** no canto superior direito
2. Selecione **Import**
3. Abra o arquivo `node-red-flow-simples.json` e copie TODO o conteúdo
4. Cole na área de importação do Node-RED
5. Clique em **Import**
6. Clique em **Deploy** (canto superior direito)

### 2. Testar Conexão

Em outro terminal (deixe o Node-RED rodando):

```bash
python test-node-red.py
```

Você deve ver dados aparecendo no painel de debug do Node-RED (lado direito).

### 3. Executar Robô com Integração

```bash
python main.py --execution 1
```

Os dados do robô serão enviados automaticamente ao Node-RED em tempo real!

## Estrutura do Flow

O flow simples criado tem:
- **HTTP In**: Recebe dados em `/robot-logs`
- **Function**: Separa dados por tipo (metrics, trajectory, summary)
- **Debug**: Mostra todos os dados recebidos

## Próximos Passos (Opcional)

Para visualizações mais avançadas, instale o dashboard:

```powershell
npm install -g node-red-dashboard
```

Depois reinicie o Node-RED e importe o flow completo `node-red-flow.json`.

