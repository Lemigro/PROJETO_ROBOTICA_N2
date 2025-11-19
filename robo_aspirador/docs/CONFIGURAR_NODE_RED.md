# Como Configurar o Endpoint no Node-RED

## Passo a Passo

### 1. Verificar se Node-RED está rodando

Abra http://127.0.0.1:1880 no navegador. Você deve ver a interface do Node-RED.

### 2. Criar o Endpoint HTTP

1. **Arraste um nó "http in"** da paleta esquerda para a área de trabalho
2. **Clique duas vezes** no nó para configurar:
   - **Method**: `POST`
   - **URL**: `/robo-data`
   - **Name**: `Robo Data` (opcional)
3. Clique em **Done**

### 3. Adicionar Nó de Debug

1. **Arraste um nó "debug"** para a área de trabalho
2. **Conecte** o nó "http in" ao nó "debug" (arraste uma linha entre eles)
3. **Clique duas vezes** no debug:
   - **Output**: `complete msg object` ou `msg.payload`
   - Ative o debug no painel direito (ícone de bug)

### 4. Deploy

Clique no botão **Deploy** (canto superior direito, vermelho).

### 5. Testar

Execute no terminal:
```bash
python test-node-red.py
```

Você deve ver os dados aparecendo no painel de debug do Node-RED!

## Estrutura Básica do Flow

```
[HTTP In: /robo-data] --> [Debug]
```

## Formato dos Dados Recebidos

O robô envia JSON no formato:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "type": "metrics" | "trajectory" | "execution_summary",
  "data": { ... }
}
```

## Próximos Passos (Opcional)

Depois que estiver funcionando, você pode adicionar:
- Nós Function para processar os dados
- Nós de visualização (chart, gauge, etc.)
- Armazenamento em banco de dados

