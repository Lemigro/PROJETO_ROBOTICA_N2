"""
Sistema de planejamento dinâmico de rotas (TSP dinâmico).
"""
import numpy as np
from typing import List, Tuple, Optional
from src.sensor import DeliveryPoint
import math


class RoutePlanner:
    """Planejador de rotas dinâmico para otimização de entregas."""
    
    def __init__(self, config: dict):
        """
        Inicializa o planejador de rotas.
        
        Args:
            config: Configurações do planejamento
        """
        self.algorithm = config.get('algorithm', 'nearest_neighbor')
        self.min_distance_threshold = config.get('min_distance_threshold', 0.5)
        self.replan_count = 0
        
    def calculate_distance(self, pos1: np.ndarray, pos2: np.ndarray) -> float:
        """Calcula distância euclidiana entre duas posições."""
        return np.linalg.norm(pos1 - pos2)
    
    def nearest_neighbor_route(
        self,
        start_pos: np.ndarray,
        points: List[DeliveryPoint],
        return_to_base: bool = True,
        base_pos: Optional[np.ndarray] = None
    ) -> List[DeliveryPoint]:
        # return_to_base e base_pos reservados para uso futuro
        _ = return_to_base, base_pos
        """
        Algoritmo Nearest Neighbor para planejamento de rota.
        
        Args:
            start_pos: Posição inicial
            points: Lista de pontos a visitar
            return_to_base: Se deve retornar à base ao final
            base_pos: Posição da base (se return_to_base=True)
            
        Returns:
            Lista ordenada de pontos para visita
        """
        if not points:
            return []
        
        # Filtrar apenas pontos não entregues
        unvisited = [p for p in points if not p.delivered]
        if not unvisited:
            return []
        
        route = []
        current_pos = start_pos.copy()
        remaining = unvisited.copy()
        
        # Construir rota usando nearest neighbor
        while remaining:
            # Encontrar ponto mais próximo
            min_dist = float('inf')
            nearest_idx = 0
            
            for i, point in enumerate(remaining):
                dist = self.calculate_distance(current_pos, point.position)
                if dist < min_dist:
                    min_dist = dist
                    nearest_idx = i
            
            # Adicionar à rota
            next_point = remaining.pop(nearest_idx)
            route.append(next_point)
            current_pos = next_point.position.copy()
        
        return route
    
    def greedy_route(
        self,
        start_pos: np.ndarray,
        points: List[DeliveryPoint],
        return_to_base: bool = True,
        base_pos: Optional[np.ndarray] = None
    ) -> List[DeliveryPoint]:
        """
        Algoritmo Greedy melhorado para planejamento de rota.
        
        Args:
            start_pos: Posição inicial
            points: Lista de pontos a visitar
            return_to_base: Se deve retornar à base ao final
            base_pos: Posição da base
            
        Returns:
            Lista ordenada de pontos para visita
        """
        unvisited = [p for p in points if not p.delivered]
        if not unvisited:
            return []
        
        # Se há poucos pontos, usar nearest neighbor
        if len(unvisited) <= 3:
            return self.nearest_neighbor_route(start_pos, unvisited, return_to_base, base_pos)
        
        # Algoritmo greedy: escolher próximo ponto que minimiza
        # a razão distância_atual / distância_média_restante
        route = []
        current_pos = start_pos.copy()
        remaining = unvisited.copy()
        
        while remaining:
            if len(remaining) == 1:
                route.append(remaining[0])
                break
            
            # Calcular distâncias médias entre pontos restantes
            avg_distances = {}
            for point in remaining:
                distances = [
                    self.calculate_distance(point.position, p.position)
                    for p in remaining if p != point
                ]
                avg_distances[point] = np.mean(distances) if distances else 1.0
            
            # Escolher ponto que minimiza distância_atual / distância_média
            best_score = float('inf')
            best_idx = 0
            
            for i, point in enumerate(remaining):
                dist_to_point = self.calculate_distance(current_pos, point.position)
                avg_dist = avg_distances[point]
                score = dist_to_point / (avg_dist + 0.1)  # Evitar divisão por zero
                
                if score < best_score:
                    best_score = score
                    best_idx = i
            
            next_point = remaining.pop(best_idx)
            route.append(next_point)
            current_pos = next_point.position.copy()
        
        return route
    
    def calculate_total_distance(self, route: List[DeliveryPoint], start_pos: np.ndarray, 
                                 base_pos: Optional[np.ndarray] = None) -> float:
        """Calcula distância total de uma rota."""
        if not route:
            return 0.0
        
        total = 0.0
        current_pos = start_pos.copy()
        
        for point in route:
            total += self.calculate_distance(current_pos, point.position)
            current_pos = point.position.copy()
        
        if base_pos is not None:
            total += self.calculate_distance(current_pos, base_pos)
        
        return total
    
    def plan_route(
        self,
        current_pos: np.ndarray,
        detected_points: List[DeliveryPoint],
        base_pos: Optional[np.ndarray] = None,
        return_to_base: bool = True
    ) -> List[DeliveryPoint]:
        """
        Planeja rota otimizada para os pontos detectados.
        
        Args:
            current_pos: Posição atual do drone
            detected_points: Lista de pontos detectados
            base_pos: Posição da base
            return_to_base: Se deve retornar à base
            
        Returns:
            Lista ordenada de pontos para visita
        """
        # Filtrar pontos não entregues
        unvisited = [p for p in detected_points if not p.delivered]
        
        if not unvisited:
            return []
        
        # Escolher algoritmo baseado na configuração
        if self.algorithm == 'nearest_neighbor':
            route = self.nearest_neighbor_route(current_pos, unvisited, return_to_base, base_pos)
        elif self.algorithm == 'greedy':
            route = self.greedy_route(current_pos, unvisited, return_to_base, base_pos)
        else:
            # Default: nearest neighbor
            route = self.nearest_neighbor_route(current_pos, unvisited, return_to_base, base_pos)
        
        self.replan_count += 1
        return route
    
    def replan_route(
        self,
        current_pos: np.ndarray,
        current_route: List[DeliveryPoint],
        new_points: List[DeliveryPoint],
        base_pos: Optional[np.ndarray] = None
    ) -> List[DeliveryPoint]:
        """
        Replaneja rota incorporando novos pontos detectados.
        
        Args:
            current_pos: Posição atual do drone
            current_route: Rota atual (pode estar parcialmente executada)
            new_points: Novos pontos detectados
            base_pos: Posição da base
            
        Returns:
            Nova rota replanejada
        """
        # Combinar pontos da rota atual (não entregues) com novos pontos
        all_points = list(current_route) + new_points
        
        # Remover duplicatas mantendo ordem
        seen = set()
        unique_points = []
        for point in all_points:
            if point.id not in seen and not point.delivered:
                seen.add(point.id)
                unique_points.append(point)
        
        # Replanejar com todos os pontos
        return self.plan_route(current_pos, unique_points, base_pos)
    
    def get_next_target(
        self,
        current_pos: np.ndarray,
        route: List[DeliveryPoint]
    ) -> Optional[DeliveryPoint]:
        # current_pos reservado para uso futuro (pode ser usado para escolher melhor próximo alvo)
        _ = current_pos
        """
        Retorna o próximo alvo da rota.
        
        Args:
            current_pos: Posição atual
            route: Rota planejada
            
        Returns:
            Próximo ponto alvo ou None
        """
        if not route:
            return None
        
        # Retornar primeiro ponto não entregue
        for point in route:
            if not point.delivered:
                return point
        
        return None

