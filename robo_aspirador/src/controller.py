"""
Sistema de Controle do Robô Aspirador
Algoritmos de evasão de obstáculos e navegação
"""
import numpy as np
import math


class ObstacleAvoidanceController:
    """Controlador de evasão de obstáculos usando potencial fields"""
    
    def __init__(self, safe_distance=0.25, max_speed=10.0, max_angular_speed=12.0):
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
                # Em vez de recuar, para e gira (mais eficiente)
                linear_speed = 0.0  # Para ao invés de recuar
            elif min_distance < self.safe_distance * 1.5:
                linear_speed = self.max_speed * 0.7  # Reduz velocidade quando próximo
            else:
                linear_speed = self.max_speed * 1.0  # Velocidade máxima quando seguro
            
            # Velocidade angular para seguir a direção calculada
            # Assume que o robô está sempre apontando para frente (yaw = 0)
            # Se muito próximo de obstáculo, gira mais rápido
            if min_distance < self.safe_distance:
                angular_speed = direction * 10.0  # Gira mais rápido quando próximo
            else:
                angular_speed = direction * 6.0  # Gira normalmente quando seguro
            angular_speed = np.clip(angular_speed, -self.max_angular_speed, self.max_angular_speed)
        else:
            linear_speed = self.max_speed * 0.8  # Aumentado de 0.5 para 0.8
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
        self.exploration_state = "forward"  # forward, turn, avoid, escape
        self.turn_direction = 1  # 1 para direita, -1 para esquerda
        self.turn_time = 0
        self.stuck_time = 0
        self.last_position = None
        self.escape_count = 0  # Contador de tentativas de escape
    
    def compute_velocity(self, sensor_readings, current_pose, coverage_map=None, optimization_suggestions=None, collision=False):
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
        
        # Detecta se está em canto (múltiplos sensores detectando obstáculos muito próximos)
        # CORREÇÃO: Detecção mais sensível de canto
        close_sensors = sum(1 for d in sensor_readings if d < 0.25)  # Aumentado threshold
        very_close_sensors = sum(1 for d in sensor_readings if d < 0.15)  # Muito próximo
        is_corner = close_sensors >= 2 or very_close_sensors >= 1  # Mais sensível
        
        # Detecta se está "colado" no obstáculo (muito próximo de múltiplos lados)
        stuck_on_wall = min_distance < 0.15 and close_sensors >= 3
        
        # Se há colisão, está em canto ou colado na parede, força manobra de escape IMEDIATA
        if collision or is_corner or stuck_on_wall:
            self.exploration_state = "escape"
            self.stuck_time = 0  # Reset contador
            self.escape_count += 1  # Incrementa contador de escape
            self.turn_time = 0  # Reset tempo de escape para começar imediatamente
            
            # CORREÇÃO: Manobra mais agressiva - recua mais para sair do obstáculo
            if stuck_on_wall or is_corner:
                # Colado na parede ou em canto: recua mais e gira muito rápido
                return -1.5, self.turn_direction * 12.0  # Recua mais e gira muito rápido
            else:
                # Colisão simples: recua e gira
                return -1.0, self.turn_direction * 10.0  # Recua e gira
        
        # Detecta se está preso (não se moveu)
        # CORREÇÃO: Detecção muito mais rápida e eficiente
        if self.last_position is not None:
            dist_moved = math.sqrt(
                (x - self.last_position[0])**2 + 
                (y - self.last_position[1])**2
            )
            # Se não se moveu E está muito próximo de obstáculo, está preso
            if dist_moved < 0.015 and min_distance < 0.3:  # Muito sensível quando próximo
                self.stuck_time += 1
            elif dist_moved < 0.03:  # Sensível quando longe também
                self.stuck_time += 1
            else:
                self.stuck_time = 0
                # Se se moveu, reduz contador de escape
                if self.escape_count > 0:
                    self.escape_count = max(0, self.escape_count - 1)
        
        self.last_position = (x, y)
        
        # CORREÇÃO: Se preso OU muito próximo de obstáculo, força escape IMEDIATO
        # Threshold muito reduzido para detectar mais rápido
        if self.stuck_time > 5 or (min_distance < 0.2 and self.stuck_time > 2):  # Muito mais rápido
            self.exploration_state = "escape"
            self.turn_time = 0  # Reset para começar escape imediatamente
            if self.stuck_time > 5:
                self.stuck_time = 0
                self.escape_count += 1
        
        # Máquina de estados simples
        if self.exploration_state == "escape":
            # CORREÇÃO: Escape mais direto - gira uma vez e segue, não fica dando voltas
            is_very_stuck = is_corner or stuck_on_wall or self.escape_count > 2
            
            # Verifica se ainda está preso durante o escape
            still_stuck = min_distance < 0.25
            
            if self.turn_time < 20:  # Primeiros 20 passos: recua e gira
                # Recua para sair do obstáculo e gira
                recue_speed = -1.5 if is_very_stuck else -1.0
                turn_speed = 8.0 if is_very_stuck else 6.0
                return recue_speed, self.turn_direction * turn_speed
            elif self.turn_time < 40:  # Próximos 20 passos: gira no lugar para mudar direção
                # Gira no lugar para garantir mudança de direção
                turn_speed = 6.0 if still_stuck else 5.0
                return 0.0, self.turn_direction * turn_speed
            elif self.turn_time < 60:  # Próximos 20 passos: avança testando
                # Avança testando se saiu da parede
                if still_stuck:
                    # Se ainda preso, recua um pouco mais
                    return -0.5, self.turn_direction * 4.0
                # Se saiu, avança normalmente
                return 2.0, 0.0  # Avança reto, sem girar
            else:
                # Reset estado e volta para exploração normal
                self.exploration_state = "forward"
                self.turn_time = 0
                # Muda direção para próxima vez (alterna)
                self.turn_direction *= -1
                if self.escape_count > 3:  # Se tentou muito, reseta contador
                    self.escape_count = 0
        
        # Evasão de obstáculos
        # CORREÇÃO: Se está em canto ou colado, força escape direto
        if is_corner or stuck_on_wall:
            self.exploration_state = "escape"
            self.turn_time = 0  # Reset tempo de escape
            # Recua e gira para sair, mas não muito rápido
            return -1.0, self.turn_direction * 8.0
        
        # CORREÇÃO: Quando próximo de parede, segue a parede ao invés de ficar girando
        if min_distance < 0.5:
            self.exploration_state = "avoid"
            
            # Se está muito próximo de uma parede, tenta seguir a parede
            if min_distance < 0.3:
                # Encontra qual sensor está mais próximo (parede à frente, esquerda ou direita)
                front_dist = sensor_readings[0] if len(sensor_readings) > 0 else 2.0
                left_dist = sensor_readings[3] if len(sensor_readings) > 3 else 2.0
                right_dist = sensor_readings[4] if len(sensor_readings) > 4 else 2.0
                
                # Se parede à frente, gira para o lado com mais espaço
                if front_dist < 0.3:
                    if right_dist > left_dist:
                        # Mais espaço à direita, gira para direita e segue
                        return 1.5, -4.0  # Avança e gira para direita
                    else:
                        # Mais espaço à esquerda, gira para esquerda e segue
                        return 1.5, 4.0  # Avança e gira para esquerda
                # Se parede ao lado, segue reto ou ajusta levemente
                elif left_dist < 0.3:
                    # Parede à esquerda, ajusta levemente para direita
                    return 2.0, -2.0
                elif right_dist < 0.3:
                    # Parede à direita, ajusta levemente para esquerda
                    return 2.0, 2.0
            
            # Evasão normal usando potential field
            linear, angular = self.avoidance_controller.compute_velocity(sensor_readings)
            if min_distance < 0.25:  # Muito próximo
                angular *= 1.2  # Ajuste suave
                linear *= 0.7  # Reduz velocidade
            return linear, angular
        
        # Exploração normal
        self.exploration_state = "forward"
        
        # CORREÇÃO: Melhor exploração para cobrir todo o mapa
        target_direction = None
        skip_current_area = False
        
        if optimization_suggestions and coverage_map:
            # Verifica se deve pular a área atual
            map_x, map_y = coverage_map.world_to_map(x, y)
            if coverage_map.is_valid_cell(map_x, map_y):
                coverage = coverage_map.get_coverage(map_x, map_y)
                skip_current_area = coverage > 4.0  # Threshold reduzido para explorar mais
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
                        # Média ponderada: 80% área não explorada, 20% direção preferida (ajustado)
                        target_direction = 0.8 * unexplored_dir + 0.2 * preferred
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
        
        # CORREÇÃO: Movimento mais fluido e constante
        # Se está em área já limpa, aumenta velocidade para passar mais rápido
        if skip_current_area:
            linear *= 2.5  # Mais rápido mas não tanto (reduzido de 3.0)
            angular *= 0.5  # Menos rotação (ajustado)
        
        # Se não há obstáculos próximos, aumenta velocidade para exploração mais rápida
        min_sensor = min(sensor_readings) if sensor_readings else 2.0
        safe_dist = self.avoidance_controller.safe_distance
        if min_sensor > safe_dist * 3:
            linear *= 1.3  # Aumento moderado (reduzido de 1.5) para movimento mais fluido
            angular *= 0.8  # Reduz rotação quando seguro para movimento mais direto
        
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

