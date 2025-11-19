"""
Sistema de Controle do Robô Aspirador
Algoritmos de evasão de obstáculos e navegação
"""
import numpy as np
import math


class ObstacleAvoidanceController:
    """Controlador de evasão de obstáculos usando potencial fields"""
    
    def __init__(self, safe_distance=0.3, max_speed=2.5, max_angular_speed=3.0):
        """
        Inicializa o controlador
        
        Args:
            safe_distance: Distância mínima segura até obstáculos (m)
            max_speed: Velocidade linear máxima (m/s)
            max_angular_speed: Velocidade angular máxima (rad/s)
        """
        self.safe_distance = safe_distance
        self.max_speed = max_speed
        self.max_angular_speed = max_angular_speed
    
    def compute_velocity(self, sensor_readings, target_direction=None):
        """
        Calcula as velocidades linear e angular baseado nas leituras dos sensores
        
        Args:
            sensor_readings: Lista de distâncias dos sensores
            target_direction: Direção alvo em radianos (opcional)
        
        Returns:
            tuple: (velocidade_linear, velocidade_angular)
        """
        num_sensors = len(sensor_readings)
        
        # Calcula ângulos dos sensores (assumindo distribuição padrão)
        if num_sensors == 5:
            sensor_angles = [0, -math.pi/4, math.pi/4, -math.pi/2, math.pi/2]
        elif num_sensors == 3:
            sensor_angles = [0, -math.pi/3, math.pi/3]
        else:
            sensor_angles = [i * 2 * math.pi / num_sensors - math.pi/2 
                           for i in range(num_sensors)]
        
        # Força repulsiva dos obstáculos (potential field)
        repulsive_force_x = 0.0
        repulsive_force_y = 0.0
        
        for i, (distance, angle) in enumerate(zip(sensor_readings, sensor_angles)):
            if distance < self.safe_distance * 2:  # Zona de influência
                # Força repulsiva inversamente proporcional à distância
                force_magnitude = (self.safe_distance * 2 - distance) / self.safe_distance
                force_magnitude = min(force_magnitude, 2.0)  # Limita a força
                
                # Direção oposta ao obstáculo
                repulsive_force_x -= force_magnitude * math.cos(angle)
                repulsive_force_y -= force_magnitude * math.sin(angle)
        
        # Força atrativa (direção alvo ou frente)
        if target_direction is not None:
            attractive_force_x = math.cos(target_direction) * 0.5
            attractive_force_y = math.sin(target_direction) * 0.5
        else:
            # Se não há direção alvo, vai em frente
            attractive_force_x = 1.0
            attractive_force_y = 0.0
        
        # Soma das forças
        total_force_x = repulsive_force_x + attractive_force_x
        total_force_y = repulsive_force_y + attractive_force_y
        
        # Converte força em velocidade
        force_magnitude = math.sqrt(total_force_x**2 + total_force_y**2)
        
        if force_magnitude > 0:
            # Normaliza e escala
            direction = math.atan2(total_force_y, total_force_x)
            
            # Velocidade linear baseada na distância mínima
            min_distance = min(sensor_readings)
            if min_distance < self.safe_distance:
                # Em vez de parar, recua levemente e gira
                linear_speed = -0.1  # Recua menos (aumentado de -0.2)
            elif min_distance < self.safe_distance * 1.5:
                linear_speed = self.max_speed * 0.6  # Reduz velocidade (aumentado de 0.4)
            else:
                linear_speed = self.max_speed * 1.0  # Velocidade máxima (aumentado de 0.9)
            
            # Velocidade angular para seguir a direção calculada
            # Assume que o robô está sempre apontando para frente (yaw = 0)
            angular_speed = direction * 3.0  # Ganho proporcional aumentado (de 2.0 para 3.0)
            angular_speed = np.clip(angular_speed, -self.max_angular_speed, self.max_angular_speed)
        else:
            linear_speed = self.max_speed * 0.5
            angular_speed = 0.0
        
        return linear_speed, angular_speed


class ExplorationController:
    """Controlador para exploração do ambiente"""
    
    def __init__(self, avoidance_controller):
        """
        Inicializa o controlador de exploração
        
        Args:
            avoidance_controller: Instância de ObstacleAvoidanceController
        """
        self.avoidance_controller = avoidance_controller
        self.exploration_state = "forward"  # forward, turn, avoid
        self.turn_direction = 1  # 1 para direita, -1 para esquerda
        self.turn_time = 0
        self.stuck_time = 0
        self.last_position = None
    
    def compute_velocity(self, sensor_readings, current_pose, coverage_map=None, optimization_suggestions=None):
        """
        Calcula velocidade para exploração
        
        Args:
            sensor_readings: Leituras dos sensores
            current_pose: (x, y, yaw) pose atual
            coverage_map: Mapa de cobertura (opcional, para otimização)
            optimization_suggestions: Sugestões do otimizador (opcional)
        
        Returns:
            tuple: (velocidade_linear, velocidade_angular)
        """
        x, y, _ = current_pose
        min_distance = min(sensor_readings)
        
        # Detecta se está preso (não se moveu)
        if self.last_position is not None:
            dist_moved = math.sqrt(
                (x - self.last_position[0])**2 + 
                (y - self.last_position[1])**2
            )
            if dist_moved < 0.05:  # Não se moveu significativamente
                self.stuck_time += 1
            else:
                self.stuck_time = 0
        
        self.last_position = (x, y)
        
        # Se preso OU muito próximo de obstáculo, tenta manobra de escape
        if self.stuck_time > 30 or min_distance < 0.25:
            self.exploration_state = "escape"
            if self.stuck_time > 30:
                self.stuck_time = 0
        
        # Máquina de estados simples
        if self.exploration_state == "escape":
            # Manobra de escape: recua e gira
            if self.turn_time < 30:
                return -0.5, self.turn_direction * 2.5
            elif self.turn_time < 90:
                return 0.0, self.turn_direction * 3.0
            else:
                self.exploration_state = "forward"
                self.turn_time = 0
                self.turn_direction *= -1
        
        # Evasão de obstáculos
        if min_distance < 0.5:
            self.exploration_state = "avoid"
            linear, angular = self.avoidance_controller.compute_velocity(sensor_readings)
            if min_distance < 0.3:
                angular *= 1.5
                linear *= 0.5
            return linear, angular
        
        # Exploração normal
        self.exploration_state = "forward"
        
        # NOVO: Usa sugestões do otimizador para evitar áreas já limpas
        target_direction = None
        skip_current_area = False
        
        if optimization_suggestions and coverage_map:
            # Verifica se deve pular a área atual
            # Usa método estático para verificar se deve pular área
            map_x, map_y = coverage_map.world_to_map(x, y)
            if coverage_map.is_valid_cell(map_x, map_y):
                coverage = coverage_map.get_coverage(map_x, map_y)
                skip_current_area = coverage > 5.0  # Threshold de alta cobertura
            else:
                skip_current_area = False
            
            # Se deve pular, força direção para área não explorada
            if skip_current_area:
                # Prioriza áreas com baixa cobertura
                target_direction = self._find_unexplored_direction(current_pose, coverage_map, 
                                                                  avoid_high_coverage=True,
                                                                  suggestions=optimization_suggestions)
            else:
                # Usa direção preferida do histórico se disponível
                if optimization_suggestions.get('preferred_directions') is not None:
                    preferred = optimization_suggestions['preferred_directions']
                    # Combina direção preferida com áreas não exploradas
                    unexplored_dir = self._find_unexplored_direction(current_pose, coverage_map)
                    if unexplored_dir is not None:
                        # Média ponderada: 70% área não explorada, 30% direção preferida
                        target_direction = 0.7 * unexplored_dir + 0.3 * preferred
                    else:
                        target_direction = preferred
                else:
                    target_direction = self._find_unexplored_direction(current_pose, coverage_map)
        elif coverage_map is not None:
            target_direction = self._find_unexplored_direction(current_pose, coverage_map)
        
        # Ajusta velocidade baseado em se está em área já limpa
        linear, angular = self.avoidance_controller.compute_velocity(
            sensor_readings, target_direction
        )
        
        # Se está em área já limpa, aumenta velocidade para passar mais rápido
        if skip_current_area:
            linear *= 1.5  # 50% mais rápido (aumentado de 1.3)
            angular *= 0.7  # Menos rotação (vai direto, reduzido de 0.8)
        
        self.turn_time += 1
        return linear, angular
    
    def _find_unexplored_direction(self, current_pose, coverage_map, avoid_high_coverage=False, suggestions=None):
        """
        Encontra direção para área não explorada
        
        Args:
            current_pose: (x, y, yaw) pose atual
            coverage_map: Mapa de cobertura
            avoid_high_coverage: Se True, evita áreas de alta cobertura
            suggestions: Sugestões do otimizador (opcional)
        
        Returns:
            float: Direção em radianos ou None
        """
        x, y, yaw = current_pose
        
        # Converte posição para células do mapa
        map_x = int((x - coverage_map.origin_x) / coverage_map.resolution)
        map_y = int((y - coverage_map.origin_y) / coverage_map.resolution)
        
        # Procura células não visitadas nas proximidades
        search_radius = 8  # Aumentado de 5 para 8 para melhor busca
        best_direction = None
        skip_areas_set = set()
        
        # Se há sugestões, marca áreas para evitar
        if suggestions and suggestions.get('skip_areas'):
            skip_areas_set = set(suggestions['skip_areas'])
        
        candidates = []
        
        for dx in range(-search_radius, search_radius + 1):
            for dy in range(-search_radius, search_radius + 1):
                if dx == 0 and dy == 0:
                    continue
                    
                cell_x = map_x + dx
                cell_y = map_y + dy
                
                if coverage_map.is_valid_cell(cell_x, cell_y):
                    # Pula áreas marcadas para evitar
                    if (cell_x, cell_y) in skip_areas_set:
                        continue
                    
                    coverage = coverage_map.get_coverage(cell_x, cell_y)
                    
                    # Se deve evitar alta cobertura, penaliza áreas muito visitadas
                    if avoid_high_coverage and coverage > 3.0:
                        continue
                    
                    # Considera também se a célula é livre (não ocupada)
                    if coverage_map.occupancy[cell_y, cell_x] == 0:  # Livre
                        distance = math.sqrt(dx**2 + dy**2)
                        # Prioriza células próximas com baixa cobertura
                        score = coverage - 0.1 * distance  # Penaliza distância
                        candidates.append((score, coverage, dx, dy))
        
        if candidates:
            # Ordena por score (menor cobertura e mais próximo = melhor)
            candidates.sort(key=lambda x: x[0])
            best = candidates[0]
            best_direction = math.atan2(best[3], best[2])
        else:
            # Se não encontrou candidatos, usa direção aleatória baseada em yaw
            best_direction = yaw + math.pi / 4
        
        return best_direction

