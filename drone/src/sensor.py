"""
Sistema de detecção de pontos de entrega.
"""
import numpy as np
from typing import List, Tuple, Set
import math


class DeliveryPoint:
    """Representa um ponto de entrega."""
    
    def __init__(self, position: np.ndarray, point_id: int):
        """
        Inicializa um ponto de entrega.
        
        Args:
            position: Posição 3D [x, y, z]
            point_id: ID único do ponto
        """
        self.position = np.array(position)
        self.id = point_id
        self.detected = False
        self.delivered = False
        self.detection_time = None
        self.delivery_time = None
        
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def distance_to(self, position: np.ndarray) -> float:
        """Calcula distância euclidiana até uma posição."""
        return np.linalg.norm(self.position - position)


class ProximitySensor:
    """Sensor de proximidade para detecção de pontos de entrega."""
    
    def __init__(self, detection_radius: float):
        """
        Inicializa o sensor de proximidade.
        
        Args:
            detection_radius: Raio de detecção em metros
        """
        self.detection_radius = detection_radius
        self.detected_points: Set[DeliveryPoint] = set()
        
    def detect_points(
        self,
        drone_position: np.ndarray,
        all_points: List[DeliveryPoint]
    ) -> List[DeliveryPoint]:
        """
        Detecta pontos dentro do raio de detecção.
        
        Args:
            drone_position: Posição atual do drone [x, y, z]
            all_points: Lista de todos os pontos de entrega
            
        Returns:
            Lista de pontos detectados (novos e já conhecidos)
        """
        detected = []
        drone_pos = np.array(drone_position)
        
        for point in all_points:
            if point.delivered:
                continue
                
            distance = point.distance_to(drone_pos)
            
            if distance <= self.detection_radius:
                if not point.detected:
                    point.detected = True
                    point.detection_time = None  # Será preenchido pelo logger
                detected.append(point)
                self.detected_points.add(point)
        
        return detected
    
    def check_delivery(
        self,
        drone_position: np.ndarray,
        point: DeliveryPoint,
        threshold: float = 0.5
    ) -> bool:
        """
        Verifica se o drone chegou ao ponto de entrega.
        
        Args:
            drone_position: Posição atual do drone
            point: Ponto de entrega a verificar
            threshold: Distância mínima para considerar entrega (horizontal)
            
        Returns:
            True se a entrega foi concluída
        """
        # Calcular distância horizontal (ignorar diferença de altura)
        horizontal_distance = np.linalg.norm(drone_position[:2] - point.position[:2])
        
        # Considerar entrega se estiver próximo horizontalmente
        # (o drone pode estar voando acima do ponto)
        if horizontal_distance <= threshold and not point.delivered:
            point.delivered = True
            return True
        return False
    
    def get_undelivered_points(self) -> List[DeliveryPoint]:
        """Retorna lista de pontos detectados mas não entregues."""
        return [p for p in self.detected_points if not p.delivered]
    
    def get_all_detected(self) -> List[DeliveryPoint]:
        """Retorna todos os pontos já detectados."""
        return list(self.detected_points)
    
    def reset(self):
        """Reseta o estado do sensor."""
        self.detected_points.clear()

