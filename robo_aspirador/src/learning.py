"""
Sistema de Aprendizado e Otimização de Rotas
"""
import numpy as np
import math


class RouteOptimizer:
    """Otimizador de rotas baseado em histórico de execuções"""
    
    def __init__(self):
        """Inicializa o otimizador"""
        self.execution_history = []  # Histórico de execuções
        self.learned_routes = []  # Rotas aprendidas
    
    def add_execution(self, trajectory, coverage_percentage, time_taken, energy_consumed):
        """
        Adiciona uma execução ao histórico
        
        Args:
            trajectory: Lista de pontos (x, y, yaw)
            coverage_percentage: Porcentagem de área coberta
            time_taken: Tempo total da execução
            energy_consumed: Energia total consumida
        """
        self.execution_history.append({
            'trajectory': trajectory,
            'coverage': coverage_percentage,
            'time': time_taken,
            'energy': energy_consumed,
            'efficiency': coverage_percentage / energy_consumed if energy_consumed > 0 else 0
        })
    
    def get_optimization_suggestions(self, current_map):
        """
        Retorna sugestões de otimização baseadas no histórico
        
        Args:
            current_map: Mapa de ocupação atual
        
        Returns:
            dict: Sugestões de otimização
        """
        if len(self.execution_history) == 0:
            return {
                'avoid_high_coverage': False,
                'preferred_directions': None,
                'skip_areas': []
            }
        
        # Analisa o histórico para encontrar padrões
        # Áreas com alta cobertura devem ser evitadas
        high_coverage_threshold = 5.0  # Número de visitas
        
        skip_areas = []
        for y in range(current_map.height):
            for x in range(current_map.width):
                if current_map.coverage[y, x] > high_coverage_threshold:
                    skip_areas.append((x, y))
        
        return {
            'avoid_high_coverage': len(skip_areas) > 0,
            'preferred_directions': self._analyze_directions(),
            'skip_areas': skip_areas
        }
    
    def _analyze_directions(self):
        """Analisa direções mais eficientes do histórico"""
        if len(self.execution_history) < 2:
            return None
        
        # Calcula direções médias das trajetórias mais eficientes
        best_executions = sorted(
            self.execution_history,
            key=lambda x: x['efficiency'],
            reverse=True
        )[:3]  # Top 3
        
        directions = []
        for exec_data in best_executions:
            traj = exec_data['trajectory']
            if len(traj) > 1:
                # Calcula direção média
                dx = traj[-1][0] - traj[0][0]
                dy = traj[-1][1] - traj[0][1]
                if dx != 0 or dy != 0:
                    directions.append(math.atan2(dy, dx))
        
        if directions:
            # Retorna direção média
            avg_direction = np.mean(directions)
            return avg_direction
        
        return None
    
    def should_skip_area(self, x, y, current_map, suggestions):
        """
        Decide se deve pular uma área baseado nas sugestões
        
        Args:
            x, y: Posição atual
            current_map: Mapa atual
            suggestions: Sugestões de otimização
        
        Returns:
            bool: True se deve pular a área
        """
        if not suggestions['avoid_high_coverage']:
            return False
        
        map_x, map_y = current_map.world_to_map(x, y)
        
        # Verifica se está em uma área de alta cobertura
        if current_map.is_valid_cell(map_x, map_y):
            coverage = current_map.get_coverage(map_x, map_y)
            return coverage > 5.0  # Threshold de alta cobertura
        
        return False
    
    def get_efficiency_improvement(self):
        """
        Calcula a melhoria de eficiência entre execuções
        
        Returns:
            dict: Estatísticas de melhoria
        """
        if len(self.execution_history) < 2:
            return {
                'improvement': 0,
                'time_reduction': 0,
                'energy_reduction': 0
            }
        
        first = self.execution_history[0]
        last = self.execution_history[-1]
        
        time_reduction = ((first['time'] - last['time']) / first['time']) * 100
        energy_reduction = ((first['energy'] - last['energy']) / first['energy']) * 100
        efficiency_improvement = last['efficiency'] - first['efficiency']
        
        return {
            'improvement': efficiency_improvement,
            'time_reduction': time_reduction,
            'energy_reduction': energy_reduction,
            'first_efficiency': first['efficiency'],
            'last_efficiency': last['efficiency']
        }

