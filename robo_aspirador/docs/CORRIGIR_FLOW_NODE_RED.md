# Como Corrigir o Flow no Node-RED

## Problema: Timeout ao Enviar Dados

O erro "Cannot GET /robo-data" confirma que o endpoint existe, mas o POST está dando timeout.

## Solução: Configurar HTTP Response

### Opção 1: Adicionar HTTP Response (Recomendado)

1. **No seu flow atual**, o nó "http" no final deve ser um **"http response"**
2. **Clique duas vezes** no nó "http"
3. Configure:
   - **Status Code**: `200`
   - **Response Headers**: Deixe vazio ou adicione `Content-Type: application/json`
4. **Clique em Done**
5. **Clique em Deploy**

### Opção 2: Remover HTTP Response (Mais Simples)

Se você não precisa de resposta:

1. **Delete o nó "http"** do final
2. O flow fica: `Recebe Dados do Robô` → `debug 1`
3. **Clique em Deploy**

## Verificar Configuração do HTTP In

1. **Clique duas vezes** no nó "Recebe Dados do Robô"
2. Verifique:
   - **Method**: `POST` ou `any` (recomendo `any` para aceitar GET e POST)
   - **URL**: `/robo-data` (exatamente assim, sem espaços)
3. **Clique em Done**
4. **Clique em Deploy**

## Flow Correto

```
[HTTP In: POST /robo-data] → [Debug] → [HTTP Response: 200] (opcional)
```

OU mais simples:

```
[HTTP In: POST /robo-data] → [Debug]
```

## Testar

Depois de configurar:

```bash
python testar-endpoint-simples.py
```

OU execute o robô:

```bash
python main.py --execution 1
```

Os dados devem aparecer no painel de debug do Node-RED!

