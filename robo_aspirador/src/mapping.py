"""
Sistema de Mapeamento de Ocupação e Registro de Trajetória
"""
import numpy as np
import math
import json
import os
from datetime import datetime


class OccupancyMap:
    """Mapa de ocupação 2D para mapeamento do ambiente"""
    
    def __init__(self, width=20, height=20, resolution=0.1, origin_x=-10, origin_y=-10):
        """
        Inicializa o mapa de ocupação
        
        Args:
            width: Largura do mapa em células
            height: Altura do mapa em células
            resolution: Resolução do mapa (m por célula)
            origin_x: Coordenada x da origem do mapa (m)
            origin_y: Coordenada y da origem do mapa (m)
        """
        self.width = width
        self.height = height
        self.resolution = resolution
        self.origin_x = origin_x
        self.origin_y = origin_y
        
        # Mapa de ocupação: 0 = livre, 1 = ocupado, -1 = desconhecido
        self.occupancy = np.full((height, width), -1, dtype=np.int8)
        
        # Mapa de cobertura: número de vezes que cada célula foi visitada
        self.coverage = np.zeros((height, width), dtype=np.float32)
        
        # Mapa de tempo: tempo gasto em cada célula
        self.time_map = np.zeros((height, width), dtype=np.float32)
        
        # Trajetória registrada
        self.trajectory = []
        self.trajectory_timestamps = []
    
    def world_to_map(self, x, y):
        """
        Converte coordenadas do mundo para células do mapa
        
        Args:
            x, y: Coordenadas no mundo (m)
        
        Returns:
            tuple: (map_x, map_y) coordenadas da célula
        """
        map_x = int((x - self.origin_x) / self.resolution)
        map_y = int((y - self.origin_y) / self.resolution)
        return map_x, map_y
    
    def map_to_world(self, map_x, map_y):
        """
        Converte células do mapa para coordenadas do mundo
        
        Args:
            map_x, map_y: Coordenadas da célula
        
        Returns:
            tuple: (x, y) coordenadas no mundo (m)
        """
        x = map_x * self.resolution + self.origin_x
        y = map_y * self.resolution + self.origin_y
        return x, y
    
    def is_valid_cell(self, map_x, map_y):
        """Verifica se a célula está dentro dos limites do mapa"""
        return 0 <= map_x < self.width and 0 <= map_y < self.height
    
    def update_occupancy(self, x, y, sensor_readings, sensor_angles, robot_orientation):
        """
        Atualiza o mapa de ocupação baseado nas leituras dos sensores
        
        Args:
            x, y: Posição do robô
            sensor_readings: Lista de distâncias dos sensores
            sensor_angles: Lista de ângulos dos sensores em relação ao robô
            robot_orientation: Orientação do robô (yaw)
        """
        map_x, map_y = self.world_to_map(x, y)
        
        if not self.is_valid_cell(map_x, map_y):
            return
        
        # Marca a posição atual como livre
        self.occupancy[map_y, map_x] = 0
        
        # Para cada sensor, marca células como livres ou ocupadas
        for distance, sensor_angle in zip(sensor_readings, sensor_angles):
            # Ângulo absoluto do raio
            ray_angle = robot_orientation + sensor_angle
            
            # Marca células ao longo do raio como livres
            max_cells = int(distance / self.resolution)
            for i in range(max_cells):
                cell_x = map_x + int(i * math.cos(ray_angle))
                cell_y = map_y + int(i * math.sin(ray_angle))
                
                if self.is_valid_cell(cell_x, cell_y):
                    if self.occupancy[cell_y, cell_x] == -1:  # Desconhecido
                        self.occupancy[cell_y, cell_x] = 0  # Marca como livre
            
            # Se o sensor detectou um obstáculo, marca a célula como ocupada
            if distance < 1.8:  # Se não está no máximo alcance
                obstacle_x = map_x + int(max_cells * math.cos(ray_angle))
                obstacle_y = map_y + int(max_cells * math.sin(ray_angle))
                
                if self.is_valid_cell(obstacle_x, obstacle_y):
                    self.occupancy[obstacle_y, obstacle_x] = 1  # Ocupado
    
    def update_coverage(self, x, y, dt=0.01):
        """
        Atualiza o mapa de cobertura (células visitadas)
        
        Args:
            x, y: Posição do robô
            dt: Intervalo de tempo decorrido
        """
        map_x, map_y = self.world_to_map(x, y)
        
        if self.is_valid_cell(map_x, map_y):
            self.coverage[map_y, map_x] += 1.0
            self.time_map[map_y, map_x] += dt
    
    def add_trajectory_point(self, x, y, yaw, timestamp=None):
        """
        Adiciona um ponto à trajetória
        
        Args:
            x, y, yaw: Pose do robô
            timestamp: Timestamp (opcional)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.trajectory.append((x, y, yaw))
        self.trajectory_timestamps.append(timestamp)
    
    def get_coverage(self, map_x, map_y):
        """Retorna o valor de cobertura de uma célula"""
        if self.is_valid_cell(map_x, map_y):
            return self.coverage[map_y, map_x]
        return 0
    
    def get_coverage_percentage(self):
        """
        Calcula a porcentagem de área coberta
        
        Returns:
            float: Porcentagem de área coberta (0-100)
        """
        # Considera apenas células livres (não ocupadas)
        free_cells = np.sum(self.occupancy == 0)
        total_free = np.sum(self.occupancy >= 0)  # Livres + ocupadas conhecidas
        
        if total_free == 0:
            return 0.0
        
        # Células visitadas pelo menos uma vez
        visited_cells = np.sum(self.coverage > 0)
        
        return (visited_cells / total_free) * 100.0 if total_free > 0 else 0.0
    
    def save(self, filepath):
        """
        Salva o mapa em arquivo JSON
        
        Args:
            filepath: Caminho do arquivo
        """
        data = {
            'width': self.width,
            'height': self.height,
            'resolution': self.resolution,
            'origin_x': self.origin_x,
            'origin_y': self.origin_y,
            'occupancy': self.occupancy.tolist(),
            'coverage': self.coverage.tolist(),
            'time_map': self.time_map.tolist(),
            'trajectory': self.trajectory,
            'trajectory_timestamps': self.trajectory_timestamps
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath):
        """
        Carrega o mapa de um arquivo JSON
        
        Args:
            filepath: Caminho do arquivo
        """
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.width = data['width']
        self.height = data['height']
        self.resolution = data['resolution']
        self.origin_x = data['origin_x']
        self.origin_y = data['origin_y']
        self.occupancy = np.array(data['occupancy'], dtype=np.int8)
        self.coverage = np.array(data['coverage'], dtype=np.float32)
        self.time_map = np.array(data['time_map'], dtype=np.float32)
        self.trajectory = data['trajectory']
        self.trajectory_timestamps = data.get('trajectory_timestamps', [])
        
        return True

