# Guia Rápido - Node-RED

## Instalação Rápida (Windows)

### 1. Instalar Node.js
- Baixe de: https://nodejs.org/
- Instale a versão LTS

### 2. Instalar Node-RED e Dashboard
```bash
# Execute o script
instalar_node_red.bat

# Ou manualmente:
npm install -g node-red
npm install -g node-red-dashboard
```

### 3. Instalar Mosquitto (Broker MQTT)
- Baixe de: https://mosquitto.org/download/
- Instale e inicie o serviço:
  ```powershell
  net start mosquitto
  ```

### 4. Iniciar Node-RED
```bash
node-red
```
Acesse: http://localhost:1880

### 5. Importar Fluxo
1. No Node-RED: Menu (☰) → **Importar**
2. Selecione `node_red_flow.json`
3. Clique em **Implantar** (botão vermelho no canto superior direito)

### 6. Acessar Dashboard
- http://localhost:1880/ui

## Testar Conexão

```bash
python testar_mqtt.py
```

Este script verifica:
- ✓ Se o broker MQTT está rodando
- ✓ Se a conexão funciona
- ✓ Se os tópicos estão corretos
- ✓ Envia mensagens de teste

## Estrutura do Dashboard

### Manipulador Planar
- Gráfico de erro ao longo do tempo
- Gauges: Erro, Tempo, Energia, Overshoot
- Status de estabilização

### Robô Móvel
- Gráfico de distância percorrida
- Métricas: Colisões, Tempo de reação, Distância, Erro lateral

## Tópicos MQTT

- `robotica_n2/manipulador_planar/metrics`
- `robotica_n2/robo_movel/metrics`

## Troubleshooting

### MQTT não conecta
```bash
# Verificar se Mosquitto está rodando
Get-Service mosquitto

# Iniciar se necessário
net start mosquitto
```

### Dashboard não aparece
```bash
# Reinstalar dashboard
npm install -g node-red-dashboard
# Reiniciar Node-RED
```

### Dados não aparecem
1. Execute: `python testar_mqtt.py`
2. Verifique o console do Node-RED
3. Adicione um nó **debug** após o MQTT para ver mensagens

## Próximos Passos

1. Execute os sistemas:
   ```bash
   python exemplo_manipulador.py
   python exemplo_robo_movel.py
   ```

2. Observe as métricas no dashboard em tempo real

3. Personalize os gráficos e alertas conforme necessário

