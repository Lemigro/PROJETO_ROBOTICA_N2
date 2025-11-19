# Guia de Configuração

## 📝 Arquivo de Configuração

O arquivo `config.py` contém todas as configurações do projeto. Você pode ajustar:

### Parâmetros do Robô
- Velocidades máximas
- Tamanho das rodas
- Massa do robô
- Ganhos do controlador

### Sensores
- Número de sensores (3-5)
- Alcance máximo
- Distância segura

### Mapa
- Tamanho do mapa
- Resolução
- Origem

### Simulação
- Tempo máximo
- Intervalo de logs
- Cobertura alvo

### Node-RED
- URL do servidor
- Endpoint
- Configuração MQTT

## 🚀 Scripts Rápidos

### run.bat
Execute rapidamente:
```bash
# Primeira execução
run.bat 1

# Segunda execução com mapa
run.bat 2 map_exec_1.json
```

## ⚙️ Personalização

### Mudar Velocidade do Robô
Edite `config.py`:
```python
ROBOT_MAX_VELOCITY = 2.5  # Aumentar velocidade
```

### Mudar Número de Sensores
```python
SENSOR_NUM_SENSORS = 3  # Reduzir para 3 sensores
```

### Mudar Tamanho do Ambiente
```python
MAP_WIDTH = 60   # Aumentar mapa
MAP_HEIGHT = 60
```

## 🔧 Troubleshooting

### Robô muito lento
- Aumente `ROBOT_MAX_VELOCITY`
- Aumente `CONTROL_FORCE_MAGNITUDE`

### Robô muito rápido/instável
- Diminua `ROBOT_MAX_VELOCITY`
- Ajuste `CONTROL_KP_LINEAR` e `CONTROL_KP_ANGULAR`

### Mapa muito pequeno
- Aumente `MAP_WIDTH` e `MAP_HEIGHT`
- Ajuste `MAP_ORIGIN_X` e `MAP_ORIGIN_Y`

### Sensores não detectam
- Aumente `SENSOR_MAX_RANGE`
- Verifique se há obstáculos muito próximos

