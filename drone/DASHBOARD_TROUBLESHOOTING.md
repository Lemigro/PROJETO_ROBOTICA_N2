# Troubleshooting do Dashboard

## Problema: Dashboard mostra "parado" ou valores zerados

### 1. Verificar se os dados estão chegando

**No Node-RED:**
1. Abra o painel de debug (ícone de debug no canto direito)
2. Verifique se o nó "Log All Data" está mostrando mensagens
3. Se não aparecer nada, os dados não estão chegando do Python

**Verificar no Python:**
1. Abra `config/config.yaml`
2. Verifique se está habilitado:
   ```yaml
   node_red:
     enabled: true
     protocol: "http"
     http:
       url: "http://localhost:1880/drone-data"
   ```

### 2. Testar conexão manualmente

Execute no terminal (PowerShell):
```powershell
curl -X POST http://localhost:1880/drone-data -H "Content-Type: application/json" -d '{\"event\":\"state\",\"data\":{\"drone_position\":[1,2,3],\"drone_velocity\":[0.5,0.5,0]},\"metrics\":{\"elapsed_time\":10,\"total_distance\":50}}'
```

Se retornar erro, o Node-RED não está recebendo.

### 3. Verificar se Node-RED está rodando

Acesse: http://localhost:1880

Se não abrir, inicie o Node-RED:
```bash
node-red
```

### 4. Verificar formato dos dados

O dashboard espera:
- **Gauges**: Número direto (ex: `msg.payload = 5.0`)
- **Charts**: Array de objetos (ex: `msg.payload = [{series:'X', x:Date.now(), y:10}]`)
- **Text**: Objeto com propriedades (ex: `msg.payload = {time:'10s', distance:'50m'}`)

### 5. Reimportar o fluxo corrigido

1. **Remova TODOS os fluxos** no Node-RED
2. **Importe novamente** o arquivo `node_red_complete.json` corrigido
3. **Deploy**
4. **Execute** a simulação Python: `python main.py`
5. **Acesse** o dashboard: http://localhost:1880/ui

### 6. Verificar logs do Python

Execute a simulação e verifique se há erros:
```bash
python main.py
```

Procure por mensagens como:
- "Erro ao enviar HTTP"
- "Falha ao conectar"

### 7. Verificar firewall/antivírus

Alguns firewalls bloqueiam conexões locais. Tente:
- Desabilitar temporariamente o firewall
- Adicionar exceção para Node-RED e Python

## Solução Rápida

Se nada funcionar, tente esta sequência:

1. **Parar tudo**: Feche Node-RED e Python
2. **Reiniciar Node-RED**: `node-red`
3. **Limpar fluxos**: Delete todos os nós no Node-RED
4. **Importar fluxo**: Cole `node_red_complete.json` completo
5. **Deploy**
6. **Verificar debug**: Veja se dados aparecem no debug
7. **Executar Python**: `python main.py`
8. **Abrir dashboard**: http://localhost:1880/ui

## Checklist Final

- [ ] Node-RED está rodando (http://localhost:1880 abre)
- [ ] Node-RED Dashboard está instalado
- [ ] Fluxo foi importado e deploy feito
- [ ] `node_red.enabled = true` no config.yaml
- [ ] URL está correta: `http://localhost:1880/drone-data`
- [ ] Python está enviando dados (verificar debug do Node-RED)
- [ ] Dashboard está acessível: http://localhost:1880/ui
- [ ] Simulação está rodando (`python main.py`)

Se todos os itens estão OK e ainda não funciona, verifique os logs do Node-RED no console onde ele está rodando.

