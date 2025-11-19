# Guia Completo: Node-RED para Projetos Python

Este guia explica como configurar, instalar e usar Node-RED para integrar com projetos Python, especialmente para projetos de robótica e IoT.

## 📋 Índice

1. [O que é Node-RED?](#o-que-é-node-red)
2. [Instalação](#instalação)
3. [Configuração Inicial](#configuração-inicial)
4. [Criando seu Primeiro Flow](#criando-seu-primeiro-flow)
5. [Integração com Python](#integração-com-python)
6. [Flows Pré-configurados](#flows-pré-configurados)
7. [Dashboard e Visualizações](#dashboard-e-visualizações)
8. [Troubleshooting](#troubleshooting)
9. [Próximos Passos](#próximos-passos)

---

## 🎯 O que é Node-RED?

Node-RED é uma ferramenta de programação visual baseada em fluxo (flow-based) para conectar dispositivos, APIs e serviços online. É ideal para:

- **IoT e Robótica**: Coletar dados de sensores e dispositivos
- **Visualização**: Criar dashboards em tempo real
- **Integração**: Conectar diferentes sistemas e serviços
- **Prototipagem Rápida**: Criar soluções sem escrever código complexo

### Por que usar Node-RED com Python?

- ✅ **Visualização em Tempo Real**: Dashboards interativos
- ✅ **Processamento de Dados**: Filtros, transformações e agregações
- ✅ **Armazenamento**: Salvar dados em bancos de dados
- ✅ **Alertas**: Notificações quando eventos ocorrem
- ✅ **Integração**: Conectar com outros serviços (MQTT, HTTP, WebSockets)

---

## 📦 Instalação

### Pré-requisitos

- **Node.js** (versão 16 ou superior)
- **npm** (geralmente vem com Node.js)

### Verificar Instalação

```bash
node --version
npm --version
```

Se não estiver instalado, baixe em: https://nodejs.org/

### Instalar Node-RED

#### Windows (PowerShell como Administrador)

```powershell
npm install -g --unsafe-perm node-red
```

**OU** se der erro de permissão:

```powershell
npm install -g node-red
```

#### Linux/Mac

```bash
sudo npm install -g --unsafe-perm node-red
```

### Verificar Instalação

```bash
node-red --version
```

Você deve ver algo como: `Node-RED v4.1.1`

### Instalar Extensões Úteis (Opcional mas Recomendado)

```bash
# Dashboard para visualizações
npm install -g node-red-dashboard

# MQTT (se precisar)
npm install -g node-red-contrib-mqtt-broker
```

---

## 🚀 Configuração Inicial

### 1. Iniciar Node-RED

#### Opção 1: Linha de Comando

```bash
node-red
```

#### Opção 2: Script Batch (Windows)

```bash
scripts\iniciar-node-red.bat
```

#### Opção 3: Em Segundo Plano (Background)

```bash
# Windows PowerShell
Start-Process node-red

# Linux/Mac
node-red &
```

### 2. Acessar Interface

Abra seu navegador e acesse:

**http://localhost:1880** ou **http://127.0.0.1:1880**

Você verá a interface do Node-RED com:
- **Paleta esquerda**: Nós disponíveis
- **Área central**: Canvas para criar flows
- **Painel direito**: Informações e debug
- **Botão Deploy**: Para ativar suas mudanças

### 3. Primeira Execução

Quando iniciar pela primeira vez, você verá:

```
Welcome to Node-RED
===================
[info] Server now running at http://127.0.0.1:1880/
[info] Started flows
```

**Importante**: Mantenha o terminal aberto enquanto o Node-RED estiver rodando!

---

## 🎨 Criando seu Primeiro Flow

### Flow Básico: Receber Dados HTTP

Este é o flow mais comum para projetos Python.

#### Passo 1: Criar Endpoint HTTP

1. **Arraste** um nó `http in` da paleta para o canvas
2. **Clique duas vezes** no nó para configurar:
   - **Method**: `POST`
   - **URL**: `/robo-data` (ou o endpoint que seu projeto usa)
   - **Name**: `Receber Dados` (opcional)
3. Clique em **Done**

#### Passo 2: Adicionar Debug

1. **Arraste** um nó `debug` para o canvas
2. **Conecte** o `http in` ao `debug` (arraste uma linha)
3. **Clique duas vezes** no debug:
   - **Output**: `msg.payload` (para ver apenas os dados)
   - Ou `complete msg object` (para ver tudo)
4. **Ative o debug** no painel direito (ícone de bug 🐛)

#### Passo 3: Deploy

1. Clique no botão **Deploy** (canto superior direito, vermelho)
2. Você verá: `Successfully deployed`

#### Passo 4: Testar

Execute um teste do seu projeto Python ou use:

```bash
python tests/test-node-red.py
```

Você deve ver os dados aparecendo no painel de **Debug** (lado direito)!

---

## 🐍 Integração com Python

### Estrutura de Dados

Seu projeto Python deve enviar dados no formato JSON via HTTP POST:

```python
import requests
import json
from datetime import datetime

def enviar_para_node_red(dados):
    url = "http://127.0.0.1:1880/robo-data"
    
    payload = {
        'timestamp': datetime.now().isoformat(),
        'type': 'metrics',  # ou 'trajectory', 'summary'
        'data': dados
    }
    
    try:
        response = requests.post(url, json=payload, timeout=1)
        return response.status_code == 200
    except:
        return False  # Node-RED não está rodando
```

### Exemplo Completo: Logger para Node-RED

```python
# src/logger.py
import requests
from datetime import datetime

class NodeREDLogger:
    def __init__(self, url="http://127.0.0.1:1880", endpoint="/robo-data"):
        self.url = f"{url}{endpoint}"
        self.session = requests.Session()
    
    def log(self, tipo, dados):
        payload = {
            'timestamp': datetime.now().isoformat(),
            'type': tipo,
            'data': dados
        }
        
        try:
            self.session.post(self.url, json=payload, timeout=0.5)
        except:
            pass  # Ignora se Node-RED não estiver rodando
```

### Tipos de Dados Comuns

#### 1. Métricas (Tempo Real)

```python
logger.log('metrics', {
    'coverage': 45.2,
    'energy': 123.5,
    'collisions': 3,
    'time': 12.5
})
```

#### 2. Trajetória (Pontos de Movimento)

```python
logger.log('trajectory', {
    'x': 1.5,
    'y': 2.3,
    'yaw': 0.5,
    'sensors': [0.8, 1.2, 0.5, 0.9, 1.1]
})
```

#### 3. Resumo de Execução

```python
logger.log('execution_summary', {
    'execution_number': 1,
    'coverage_percentage': 95.0,
    'total_time': 120.5,
    'total_energy': 500.0,
    'efficiency': 0.19
})
```

---

## 📊 Flows Pré-configurados

### Importar Flow do Projeto

1. No Node-RED, clique no **menu** (☰) no canto superior direito
2. Selecione **Import**
3. Clique em **select a file to import** ou cole o JSON
4. Selecione o arquivo: `node-red/node-red-flow.json`
5. Clique em **Import**
6. Clique em **Deploy**

### Estrutura do Flow Recomendado

```
[HTTP In: /robo-data] 
    ↓
[Function: Processar Dados]
    ↓
[Switch: Separar por Tipo]
    ├─→ [Debug: Métricas]
    ├─→ [Debug: Trajetória]
    └─→ [Debug: Resumo]
```

### Flow Mínimo (Para Testes)

Arquivo: `node-red/FLOW_MINIMO.txt`

1. Crie um nó `http in` com URL `/robo-data` e Method `POST`
2. Conecte a um nó `debug`
3. Deploy
4. Pronto!

---

## 📈 Dashboard e Visualizações

### Instalar Dashboard

```bash
npm install -g node-red-dashboard
```

Reinicie o Node-RED após instalar.

### Criar Dashboard Básico

1. **Arraste** um nó `ui_base` (aparece após instalar dashboard)
2. Configure o nome do dashboard
3. **Arraste** nós de visualização:
   - `ui_gauge`: Para valores numéricos (cobertura, energia)
   - `ui_chart`: Para gráficos de linha (trajetória, métricas ao longo do tempo)
   - `ui_text`: Para mostrar texto/status
4. Conecte seus dados aos nós de visualização
5. **Deploy**
6. Acesse: **http://localhost:1880/ui**

### Exemplo: Dashboard de Métricas

```
[HTTP In] → [Function] → [Switch]
                              ├─→ [Gauge: Cobertura]
                              ├─→ [Gauge: Energia]
                              ├─→ [Chart: Trajetória]
                              └─→ [Text: Status]
```

---

## 🔧 Configuração Avançada

### Alterar Porta Padrão

Se a porta 1880 estiver ocupada:

```bash
node-red -p 1881
```

Acesse: http://localhost:1881

### Configurar Credenciais

1. No Node-RED, vá em **Menu** → **Settings** → **Credentials**
2. Configure uma senha para proteger seus flows
3. Salve e reinicie

### Persistência de Dados

Os flows são salvos automaticamente em:
- **Windows**: `C:\Users\<usuario>\.node-red\flows.json`
- **Linux/Mac**: `~/.node-red/flows.json`

---

## 🐛 Troubleshooting

### Problema: Node-RED não inicia

**Solução 1**: Verifique se a porta está livre
```bash
# Windows
netstat -ano | findstr :1880

# Linux/Mac
lsof -i :1880
```

**Solução 2**: Use outra porta
```bash
node-red -p 1881
```

### Problema: Dados não chegam do Python

**Verificações**:

1. ✅ Node-RED está rodando? (veja o terminal)
2. ✅ URL está correta? (`http://127.0.0.1:1880/robo-data`)
3. ✅ Endpoint está configurado? (Method: POST)
4. ✅ Flow foi feito Deploy?
5. ✅ Debug está ativado?

**Teste Manual**:

```bash
# PowerShell
Invoke-WebRequest -Uri "http://127.0.0.1:1880/robo-data" -Method POST -Body '{"test": "data"}' -ContentType "application/json"

# Linux/Mac
curl -X POST http://127.0.0.1:1880/robo-data -H "Content-Type: application/json" -d '{"test": "data"}'
```

### Problema: Erro "Cannot find module"

**Solução**: Reinstale Node-RED
```bash
npm uninstall -g node-red
npm install -g node-red
```

### Problema: Dashboard não aparece

**Solução**:
1. Instale: `npm install -g node-red-dashboard`
2. Reinicie Node-RED
3. Acesse: http://localhost:1880/ui (note o `/ui`)

### Problema: Python não consegue conectar

**Verificações**:
1. Node-RED está rodando?
2. Firewall não está bloqueando?
3. URL está correta? (use `127.0.0.1` em vez de `localhost`)
4. Timeout muito baixo? (aumente para 2-5 segundos)

---

## 📝 Checklist de Configuração

Use este checklist para cada novo projeto:

- [ ] Node-RED instalado (`node-red --version`)
- [ ] Node-RED iniciado e acessível (http://localhost:1880)
- [ ] Flow básico criado (HTTP In + Debug)
- [ ] Deploy realizado
- [ ] Teste Python executado com sucesso
- [ ] Dados aparecendo no Debug
- [ ] Dashboard configurado (opcional)
- [ ] Documentação do endpoint atualizada

---

## 🚀 Próximos Passos

### Para Projetos de Robótica

1. **Visualização de Trajetória**: Plotar caminho do robô em tempo real
2. **Métricas em Tempo Real**: Gauges para cobertura, energia, velocidade
3. **Histórico**: Salvar dados em arquivo ou banco de dados
4. **Alertas**: Notificações quando colisões ou erros ocorrem

### Melhorias Avançadas

1. **MQTT**: Para comunicação mais eficiente
2. **WebSockets**: Para atualizações em tempo real no navegador
3. **Banco de Dados**: InfluxDB, MongoDB, SQLite
4. **Machine Learning**: Processar dados com TensorFlow.js
5. **Integração Cloud**: AWS IoT, Azure IoT, Google Cloud

### Recursos Adicionais

- **Documentação Oficial**: https://nodered.org/docs/
- **Node-RED Library**: https://flows.nodered.org/
- **Exemplos**: https://cookbook.nodered.org/

---

## 📚 Estrutura de Pastas Recomendada

Para projetos com Node-RED, organize assim:

```
projeto/
├── src/                    # Código Python
│   └── logger.py          # Integração Node-RED
├── node-red/              # Configurações Node-RED
│   ├── flow.json          # Flow principal
│   ├── flow-simples.json  # Flow mínimo
│   └── FLOW_MINIMO.txt    # Instruções
├── scripts/               # Scripts utilitários
│   └── iniciar-node-red.bat
├── tests/                 # Testes
│   └── test-node-red.py   # Teste de conexão
└── docs/                  # Documentação
    └── NODE_RED_GUIA_COMPLETO.md
```

---

## 💡 Dicas Finais

1. **Sempre faça Deploy** após mudanças no flow
2. **Use Debug** para entender o formato dos dados
3. **Teste primeiro** com o flow mínimo antes de criar complexos
4. **Documente seus endpoints** para facilitar integração
5. **Mantenha Node-RED rodando** enquanto desenvolve
6. **Use try/except** no Python para não quebrar se Node-RED estiver offline

---

## 🎓 Exemplo Completo: Projeto Robótica

### 1. Iniciar Node-RED

```bash
node-red
```

### 2. Configurar Flow

- HTTP In: `/robo-data`, POST
- Debug: `msg.payload`
- Deploy

### 3. Executar Projeto Python

```bash
python main.py --execution 1
```

### 4. Ver Dados no Node-RED

- Abra o painel Debug
- Veja os dados chegando em tempo real

### 5. Adicionar Visualizações (Opcional)

- Instale dashboard
- Adicione gauges e charts
- Conecte aos dados
- Acesse http://localhost:1880/ui

---

**Pronto!** Agora você está preparado para usar Node-RED em qualquer projeto Python! 🎉

Para dúvidas específicas, consulte a documentação do seu projeto ou os arquivos em `docs/`.
