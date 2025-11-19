"""
Arquivo de Configuração do Robô Aspirador
Ajuste os parâmetros aqui para personalizar o comportamento
"""
import os

# ============================================================================
# CONFIGURAÇÕES DO ROBÔ
# ============================================================================

# Parâmetros físicos
ROBOT_WHEEL_RADIUS = 0.05  # metros
ROBOT_WHEEL_BASE = 0.2     # metros
ROBOT_MAX_VELOCITY = 3.0   # m/s (aumentado de 2.0)
ROBOT_MAX_ANGULAR_VELOCITY = 4.0  # rad/s (aumentado de 3.0)
ROBOT_MASS = 1.0           # kg

# Controle
CONTROL_FORCE_MAGNITUDE = 10.0
CONTROL_TORQUE_MAGNITUDE = 5.0
CONTROL_KP_LINEAR = 50.0
CONTROL_KP_ANGULAR = 30.0
CONTROL_MAX_FORCE = 100.0
CONTROL_MAX_TORQUE = 50.0

# ============================================================================
# CONFIGURAÇÕES DOS SENSORES
# ============================================================================

SENSOR_NUM_SENSORS = 5      # Número de sensores (3-5 recomendado)
SENSOR_MAX_RANGE = 2.0      # metros
SENSOR_SAFE_DISTANCE = 0.35  # metros (reduzido para permitir movimento mais próximo)

# ============================================================================
# CONFIGURAÇÕES DO MAPA
# ============================================================================

MAP_WIDTH = 40             # células
MAP_HEIGHT = 40            # células
MAP_RESOLUTION = 0.1       # metros por célula
MAP_ORIGIN_X = -2.0        # metros
MAP_ORIGIN_Y = -2.0        # metros

# ============================================================================
# CONFIGURAÇÕES DA SIMULAÇÃO
# ============================================================================

SIM_TIME_STEP = 1.0/240.0  # segundos (240 Hz)
SIM_MAX_TIME = 300.0        # segundos (5 minutos)
SIM_LOG_INTERVAL = 5        # passos entre logs (reduzido para parecer mais rápido)
SIM_TARGET_COVERAGE = 95.0  # porcentagem para parar

# ============================================================================
# CONFIGURAÇÕES DO AMBIENTE
# ============================================================================

ENV_ADD_OBSTACLES = True
ENV_START_POS = [0, 0, 0.1]  # [x, y, z] em metros
ENV_START_ORIENTATION = [0, 0, 0]  # [roll, pitch, yaw] em radianos

# ============================================================================
# CONFIGURAÇÕES DO NODE-RED
# ============================================================================

NODERED_URL = "http://127.0.0.1:1880"
NODERED_ENDPOINT = "/robo-data"
NODERED_USE_MQTT = False
NODERED_MQTT_BROKER = "localhost"

# ============================================================================
# CONFIGURAÇÕES DE ARQUIVOS
# ============================================================================

MAPS_DIR = "maps"
MAPS_PREFIX = "map_exec_"

# ============================================================================
# CONFIGURAÇÕES DE APRENDIZADO
# ============================================================================

LEARNING_HIGH_COVERAGE_THRESHOLD = 5.0  # Número de visitas para considerar "alta cobertura"
LEARNING_SEARCH_RADIUS = 5              # Células para procurar áreas não visitadas

