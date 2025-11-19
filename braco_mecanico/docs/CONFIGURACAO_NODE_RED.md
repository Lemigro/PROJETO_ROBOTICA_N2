# Configuração do Node-RED

Este guia explica como configurar o Node-RED para receber e visualizar as métricas dos sistemas robóticos.

## Pré-requisitos

1. **Node.js e npm** instalados
2. **Mosquitto MQTT Broker** instalado e rodando
3. **Node-RED** instalado

## Passo 1: Instalar Node-RED

```bash
npm install -g node-red
```

## Passo 2: Instalar Paleta do Dashboard

O dashboard requer o pacote `node-red-dashboard`:

```bash
npm install -g node-red-dashboard
```

Ou dentro do Node-RED:
1. Menu → Gerenciar Paleta
2. Aba "Instalar"
3. Buscar: `node-red-dashboard`
4. Instalar

## Passo 3: Iniciar Node-RED

```bash
node-red
```

Acesse: http://localhost:1880

## Passo 4: Importar Fluxo

### Opção A: Importar arquivo JSON

1. No Node-RED, clique no menu (☰) → **Importar**
2. Selecione o arquivo `node_red_flow.json`
3. Clique em **Importar**

### Opção B: Copiar e colar

1. Abra o arquivo `node_red_flow.json`
2. Copie todo o conteúdo
3. No Node-RED, menu → **Importar**
4. Cole o JSON na área de texto
5. Clique em **Importar**

## Passo 5: Configurar Broker MQTT

1. Clique duas vezes no nó **"Local MQTT"** (broker)
2. Verifique as configurações:
   - **Broker**: `localhost`
   - **Porta**: `1883`
3. Clique em **Atualizar** e depois **Implantar**

## Passo 6: Verificar Conexão

1. Certifique-se de que o Mosquitto está rodando:
   ```bash
   # Windows (PowerShell)
   Get-Service mosquitto
   
   # Linux
   sudo systemctl status mosquitto
   ```

2. No Node-RED, os nós MQTT devem mostrar status **Conectado** (ponto verde)

## Passo 7: Acessar Dashboard

1. Clique no ícone de menu (☰) → **Dashboard**
2. Ou acesse diretamente: http://localhost:1880/ui

## Estrutura do Dashboard

### Manipulador Planar
- **Gráfico**: Erro médio de posição ao longo do tempo
- **Gauges**:
  - Erro médio (rad)
  - Tempo de estabilização (s)
  - Energia total gasta (J)
  - Overshoot máximo (rad)
- **Status**: Indicador se está estabilizado

### Robô Móvel
- **Gráfico**: Distância percorrida ao longo do tempo
- **Métricas**:
  - Número de colisões
  - Tempo de reação médio (s)
  - Distância percorrida (m)
  - Erro médio lateral (m)

## Personalização

### Alterar Tópicos MQTT

Se você alterou os tópicos no código Python, atualize nos nós MQTT:

1. Clique duas vezes no nó **"Manipulador Planar"**
2. Altere o campo **Tópico** para: `seu_topico/manipulador_planar/metrics`
3. Faça o mesmo para o nó **"Robô Móvel"**

### Adicionar Mais Gráficos

1. Arraste um nó **chart** para o fluxo
2. Conecte após o nó de parse
3. Configure o grupo para aparecer no dashboard
4. Defina o tipo de gráfico (line, bar, etc.)

### Alterar Cores e Escalas

1. Clique duas vezes em qualquer gauge ou chart
2. Ajuste:
   - **Cores**: Para diferentes faixas de valores
   - **Min/Max**: Limites do gauge
   - **Seg1/Seg2**: Limites das cores

## Troubleshooting

### MQTT não conecta

1. **Verificar se o Mosquitto está rodando**:
   ```bash
   # Windows
   netstat -an | findstr 1883
   
   # Linux
   sudo netstat -tulpn | grep 1883
   ```

2. **Testar conexão manualmente**:
   ```bash
   # Publicar mensagem de teste
   mosquitto_pub -h localhost -t test/topic -m "Hello"
   
   # Subscrever
   mosquitto_sub -h localhost -t test/topic
   ```

3. **Verificar firewall**: Porta 1883 deve estar aberta

### Dashboard não aparece

1. Verifique se `node-red-dashboard` está instalado:
   ```bash
   npm list -g node-red-dashboard
   ```

2. Reinicie o Node-RED

3. Verifique o console do Node-RED para erros

### Dados não aparecem

1. Verifique se os scripts Python estão enviando dados:
   - Execute: `python exemplo_manipulador.py`
   - Verifique o console para mensagens MQTT

2. No Node-RED, adicione um nó **debug** após o MQTT para ver as mensagens recebidas

3. Verifique o formato JSON das mensagens

### Erro "Cannot find module"

Se aparecer erro sobre módulos faltando:

```bash
cd ~/.node-red
npm install node-red-dashboard
npm install node-red-contrib-ui
```

## Exemplo de Mensagem Recebida

```json
{
  "timestamp": 1703123456.789,
  "system": "manipulador_planar",
  "metrics": {
    "erro_medio_posicao": 0.05,
    "tempo_estabilizacao": 2.3,
    "energia_total_gasta": 15.7,
    "overshoot_maximo": 0.12,
    "estabilizado": true
  }
}
```

## Próximos Passos

1. **Adicionar alertas**: Configure notificações quando métricas ultrapassarem limites
2. **Histórico**: Configure armazenamento de dados (InfluxDB, MongoDB)
3. **Análise**: Adicione nós de análise estatística
4. **Controle remoto**: Adicione nós para enviar comandos aos sistemas

## Recursos Adicionais

- [Documentação Node-RED](https://nodered.org/docs/)
- [Node-RED Dashboard](https://github.com/node-red/node-red-dashboard)
- [MQTT Documentation](https://mqtt.org/documentation)

