"""
Arquivo de configuração para o Robô Móvel
"""

# Configurações MQTT/Node-RED
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "robotica_n2"

# Configurações do Robô Móvel
ROBO_MOVEL_CONFIG = {
    'wheel_radius': 0.1,     # Raio da roda (metros)
    'base_width': 0.3,       # Largura da base (metros)
    'max_velocity': 5.0,     # Velocidade máxima (rad/s)
    'sensor_max_range': 2.0, # Alcance máximo do sensor (metros)
    'sensor_noise_std': 0.02, # Desvio padrão do ruído do sensor
    'pid_kp': 3.0,           # Ganho proporcional (aumentado)
    'pid_ki': 0.15,          # Ganho integral (aumentado)
    'pid_kd': 0.5,           # Ganho derivativo (aumentado)
    'num_obstacles': 8       # Número de obstáculos no ambiente
}

