"""
Sistema de Sensores Ultrassônicos para o Robô Aspirador
"""
import pybullet as p
import numpy as np
import math


class UltrasonicSensor:
    """Sensor ultrassônico simulado usando ray casting do PyBullet"""
    
    def __init__(self, physics_client, max_range=2.0, angle=0.0):
        """
        Inicializa um sensor ultrassônico
        
        Args:
            physics_client: Cliente PyBullet
            max_range: Alcance máximo em metros
            angle: Ângulo do sensor em relação à frente do robô (radianos)
        """
        self.p = physics_client
        self.max_range = max_range
        self.angle = angle
        self.last_reading = max_range
    
    def read(self, robot_id, robot_pos, robot_orientation):
        """
        Lê a distância até o obstáculo mais próximo
        
        Args:
            robot_id: ID do robô no PyBullet
            robot_pos: Posição do robô [x, y, z]
            robot_orientation: Orientação do robô (yaw em radianos)
        
        Returns:
            float: Distância até o obstáculo (m), ou max_range se não houver obstáculo
        """
        # Calcula a direção do raio baseado na orientação do robô + ângulo do sensor
        ray_angle = robot_orientation + self.angle
        ray_direction = [
            math.cos(ray_angle),
            math.sin(ray_angle),
            0.0
        ]
        
        # Posição inicial do raio (ligeiramente acima do chão)
        ray_start = [robot_pos[0], robot_pos[1], robot_pos[2] + 0.05]
        
        # Posição final do raio
        ray_end = [
            ray_start[0] + ray_direction[0] * self.max_range,
            ray_start[1] + ray_direction[1] * self.max_range,
            ray_start[2]
        ]
        
        # Executa o ray cast
        result = p.rayTest(ray_start, ray_end)
        
        if result[0][0] != -1:  # Se houve colisão
            hit_pos = result[0][3]
            distance = math.sqrt(
                (hit_pos[0] - ray_start[0])**2 +
                (hit_pos[1] - ray_start[1])**2
            )
            self.last_reading = min(distance, self.max_range)
        else:
            self.last_reading = self.max_range
        
        return self.last_reading


class SensorArray:
    """Array de sensores ultrassônicos ao redor do robô"""
    
    def __init__(self, physics_client, num_sensors=5, max_range=2.0):
        """
        Inicializa um array de sensores
        
        Args:
            physics_client: Cliente PyBullet
            num_sensors: Número de sensores (recomendado: 3-5)
            max_range: Alcance máximo de cada sensor (m)
        """
        self.p = physics_client
        self.num_sensors = num_sensors
        self.max_range = max_range
        
        # Distribui os sensores ao redor do robô
        # Sensor 0: frente, depois distribuídos simetricamente
        if num_sensors == 3:
            angles = [0, -math.pi/3, math.pi/3]  # Frente, esquerda, direita
        elif num_sensors == 5:
            angles = [0, -math.pi/4, math.pi/4, -math.pi/2, math.pi/2]  # Frente, diagonais, laterais
        else:
            # Distribuição uniforme
            angles = [i * 2 * math.pi / num_sensors for i in range(num_sensors)]
            angles = [a - math.pi/2 for a in angles]  # Ajusta para ter um sensor na frente
        
        self.sensors = [
            UltrasonicSensor(physics_client, max_range, angle)
            for angle in angles
        ]
    
    def read_all(self, robot_id, robot_pos, robot_orientation):
        """
        Lê todos os sensores
        
        Args:
            robot_id: ID do robô
            robot_pos: Posição do robô [x, y, z]
            robot_orientation: Orientação do robô (yaw)
        
        Returns:
            list: Lista de distâncias lidas por cada sensor
        """
        return [sensor.read(robot_id, robot_pos, robot_orientation) 
                for sensor in self.sensors]
    
    def get_front_distance(self):
        """Retorna a distância do sensor frontal"""
        return self.sensors[0].last_reading
    
    def get_min_distance(self):
        """Retorna a menor distância detectada"""
        return min(sensor.last_reading for sensor in self.sensors)
    
    def has_obstacle_ahead(self, threshold=0.5):
        """Verifica se há obstáculo à frente"""
        return self.get_front_distance() < threshold

