"""
Robô Móvel Diferencial com Evasão de Obstáculos
Simula um robô com dois motores de tração e sensores ultrassônicos
"""

import pybullet as p
import pybullet_data
import numpy as np
import time
import math
from typing import List, Tuple
import sys
from pathlib import Path

# Import relativo ou absoluto dependendo do contexto
try:
    from .node_red_interface import NodeRedInterface
except ImportError:
    # Fallback para import absoluto
    sys.path.insert(0, str(Path(__file__).parent))
    from node_red_interface import NodeRedInterface


class PIDController:
    """Controlador PID simples"""
    
    def __init__(self, kp: float = 1.0, ki: float = 0.0, kd: float = 0.1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0
        
    def compute(self, error: float, dt: float) -> float:
        """Calcula a saída do controlador"""
        p_term = self.kp * error
        self.integral += error * dt
        i_term = self.ki * self.integral
        d_term = self.kd * (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error
        
        return p_term + i_term + d_term
    
    def reset(self):
        """Reseta o controlador"""
        self.integral = 0.0
        self.prev_error = 0.0


class UltrasonicSensor:
    """Sensor ultrassônico simulado"""
    
    def __init__(self, max_range: float = 2.0, noise_std: float = 0.02):
        self.max_range = max_range
        self.noise_std = noise_std
        
    def measure(self, robot_pos: List[float], robot_orn: List[float], 
                direction: str) -> float:
        """
        Mede a distância em uma direção
        
        Args:
            robot_pos: Posição do robô [x, y, z]
            robot_orn: Orientação do robô (quaternion)
            direction: 'front', 'front_left', 'front_right', 'left', 'right', 'back_left', 'back_right'
        """
        # Converter orientação para euler
        euler = p.getEulerFromQuaternion(robot_orn)
        yaw = euler[2]  # Rotação em Z
        
        # Direção do sensor (ângulos relativos à frente do robô)
        angle_offsets = {
            'front': 0.0,
            'front_left': math.pi/4,      # 45° à esquerda
            'front_right': -math.pi/4,    # 45° à direita
            'left': math.pi/2,            # 90° à esquerda
            'right': -math.pi/2,          # 90° à direita
            'back_left': 3*math.pi/4,     # 135° à esquerda
            'back_right': -3*math.pi/4    # 135° à direita
        }
        
        # Compatibilidade com direções antigas
        if direction == 'front':
            angle = yaw
        elif direction == 'left':
            angle = yaw + math.pi/2
        elif direction == 'right':
            angle = yaw - math.pi/2
        else:
            # Usar offset se disponível
            angle = yaw + angle_offsets.get(direction, 0.0)
        
        # Raycast para detectar obstáculos
        ray_from = robot_pos
        ray_to = [
            robot_pos[0] + self.max_range * math.cos(angle),
            robot_pos[1] + self.max_range * math.sin(angle),
            robot_pos[2]
        ]
        
        # Realizar raycast
        hit = p.rayTest(ray_from, ray_to)
        
        if hit[0][0] != -1:  # Colisão detectada
            hit_pos = hit[0][3]
            distance = math.sqrt(
                (hit_pos[0] - robot_pos[0])**2 +
                (hit_pos[1] - robot_pos[1])**2
            )
        else:
            distance = self.max_range
        
        # Adicionar ruído
        rng = np.random.default_rng()  # Gerador local para ruído
        noise = rng.normal(0, self.noise_std)
        distance = max(0.0, min(self.max_range, distance + noise))
        
        return distance


class RoboMovel:
    """Robô móvel diferencial com evasão de obstáculos"""
    
    def __init__(self, use_gui: bool = True, start_point: List[float] = None, goal_point: List[float] = None):
        """
        Inicializa o robô móvel
        
        Args:
            use_gui: Se True, mostra a visualização
            start_point: Ponto de partida [x, y, z]. Se None, usa padrão
            goal_point: Ponto de destino [x, y, z]. Se None, usa padrão
        """
        self.use_gui = use_gui
        
        # Conectar ao PyBullet
        if use_gui:
            self.physics_client = p.connect(p.GUI)
            # Configurar câmera para visualização top-down
            p.resetDebugVisualizerCamera(
                cameraDistance=8.0,
                cameraYaw=90,
                cameraPitch=-89.9,
                cameraTargetPosition=[0, 0, 0]
            )
        else:
            self.physics_client = p.connect(p.DIRECT)
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        
        # Criar o plano
        self.plane_id = p.loadURDF("plane.urdf")
        
        # Definir pontos de partida e destino
        if start_point is None:
            self.start_point = [-3.0, 3.0, 0.1]  # Canto superior esquerdo
        else:
            self.start_point = start_point
        
        if goal_point is None:
            self.goal_point = [3.0, -3.0, 0.1]  # Canto inferior direito
        else:
            self.goal_point = goal_point
        
        # Parâmetros do robô (inicializar antes de criar o robô)
        self.wheel_radius = 0.1  # Raio da roda (metros)
        self.base_width = 0.3   # Largura da base (metros)
        self.max_velocity = 8.0  # Velocidade máxima linear (m/s) - aumentado como robô aspirador
        self.max_angular_velocity = 10.0  # Velocidade angular máxima (rad/s)
        
        # Trajetórias
        self.reference_trajectory = []  # Trajetória de referência (ideal)
        self.actual_trajectory = []     # Trajetória real (com evasão)
        self.compute_reference_trajectory()
        
        # Métricas (inicializar antes de criar o robô)
        self.metrics = {
            'numero_colisoes': 0,
            'tempo_reacao': [],
            'distancia_percorrida': 0.0,
            'erro_medio_lateral': [],
            'posicao_anterior': None,
            'ultima_colisao': None
        }
        
        # Criar ambiente com obstáculos (antes do robô para não colidir)
        self.create_environment()
        
        # Criar o robô
        self.create_robot()
        
        # Sensores ultrassônicos - múltiplas direções para escaneamento
        self.sensors = {
            'front': UltrasonicSensor(max_range=2.0, noise_std=0.02),
            'front_left': UltrasonicSensor(max_range=1.5, noise_std=0.02),
            'front_right': UltrasonicSensor(max_range=1.5, noise_std=0.02),
            'left': UltrasonicSensor(max_range=1.5, noise_std=0.02),
            'right': UltrasonicSensor(max_range=1.5, noise_std=0.02),
            'back_left': UltrasonicSensor(max_range=1.0, noise_std=0.02),
            'back_right': UltrasonicSensor(max_range=1.0, noise_std=0.02)
        }
        
        # Controlador PID para desvio (ajustado para ser mais responsivo)
        self.pid_controller = PIDController(kp=2.0, ki=0.05, kd=0.3)
        
        # Controlador para seguir a trajetória de referência (aumentado para seguir melhor o goal)
        self.path_controller = PIDController(kp=2.5, ki=0.1, kd=0.3)
        
        # Interface Node-RED
        self.node_red = NodeRedInterface()
        
        # Desenhar trajetórias iniciais
        if self.use_gui:
            self.draw_trajectories()
        
    def create_robot(self):
        """Cria o robô móvel diferencial"""
        # Corpo do robô (caixa)
        robot_visual = p.createVisualShape(
            shapeType=p.GEOM_BOX,
            halfExtents=[0.2, 0.15, 0.1],
            rgbaColor=[0.2, 0.8, 0.2, 1]
        )
        robot_collision = p.createCollisionShape(
            shapeType=p.GEOM_BOX,
            halfExtents=[0.2, 0.15, 0.1]
        )
        
        # Calcular orientação inicial (olhando para o goal)
        dx = self.goal_point[0] - self.start_point[0]
        dy = self.goal_point[1] - self.start_point[1]
        initial_yaw = math.atan2(dy, dx)
        initial_orn = p.getQuaternionFromEuler([0, 0, initial_yaw])
        
        # Posicionar robô no ponto de partida com orientação correta
        self.robot_id = p.createMultiBody(
            baseMass=2.0,
            baseCollisionShapeIndex=robot_collision,
            baseVisualShapeIndex=robot_visual,
            basePosition=self.start_point,
            baseOrientation=initial_orn
        )
        
        # Configurar propriedades físicas (como robô aspirador)
        p.changeDynamics(
            self.robot_id,
            -1,
            lateralFriction=0.3,
            spinningFriction=0.1,
            rollingFriction=0.1,
            linearDamping=0.1,
            angularDamping=0.2,
            localInertiaDiagonal=[1, 1, 0.1]
        )
        
        # Garantir que o robô comece parado (sem velocidade)
        p.resetBaseVelocity(self.robot_id, [0, 0, 0], [0, 0, 0])
        
        # Forçar posição e orientação corretas após criação
        p.resetBasePositionAndOrientation(
            self.robot_id,
            self.start_point,
            initial_orn
        )
        
        # Estabilizar física antes de começar (mais passos para evitar pulo)
        for _ in range(50):
            p.stepSimulation()
            if self.use_gui:
                time.sleep(0.001)
        
        # Garantir que está parado após estabilização
        p.resetBaseVelocity(self.robot_id, [0, 0, 0], [0, 0, 0])
        
        # Verificar e corrigir posição final
        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        # Se o robô se moveu durante estabilização, reposicionar
        if abs(pos[0] - self.start_point[0]) > 0.01 or \
           abs(pos[1] - self.start_point[1]) > 0.01:
            p.resetBasePositionAndOrientation(
                self.robot_id,
                self.start_point,
                initial_orn
            )
            p.resetBaseVelocity(self.robot_id, [0, 0, 0], [0, 0, 0])
        
        # Inicializar posição anterior e trajetória
        pos, _ = p.getBasePositionAndOrientation(self.robot_id)
        self.metrics['posicao_anterior'] = pos
        self.actual_trajectory.append([pos[0], pos[1], pos[2]])
        
    def compute_reference_trajectory(self):
        """Calcula a trajetória de referência (linha reta do start ao goal)"""
        # Criar pontos ao longo da linha reta
        num_points = 50
        for i in range(num_points + 1):
            t = i / num_points
            x = self.start_point[0] + t * (self.goal_point[0] - self.start_point[0])
            y = self.start_point[1] + t * (self.goal_point[1] - self.start_point[1])
            z = self.start_point[2] + t * (self.goal_point[2] - self.start_point[2])
            self.reference_trajectory.append([x, y, z])
    
    def draw_trajectories(self):
        """Desenha as trajetórias visualmente"""
        # Desenhar trajetória de referência (linha vermelha tracejada)
        if len(self.reference_trajectory) > 1:
            for i in range(len(self.reference_trajectory) - 1):
                if i % 2 == 0:  # Tracejado: desenha apenas pontos pares
                    p.addUserDebugLine(
                        self.reference_trajectory[i],
                        self.reference_trajectory[i + 1],
                        lineColorRGB=[1.0, 0.0, 0.0],  # Vermelho
                        lineWidth=3,
                        lifeTime=0  # Permanente
                    )
        
        # Desenhar trajetória real (linha azul sólida) - será atualizada durante a simulação
        # Isso será feito no método step()
    
    def update_trajectory_drawing(self):
        """Atualiza o desenho da trajetória real (linha azul)"""
        if len(self.actual_trajectory) > 1:
            # Desenhar o último segmento adicionado
            # Ajustar altura Z para ficar visível acima do chão
            point1 = self.actual_trajectory[-2].copy()
            point2 = self.actual_trajectory[-1].copy()
            point1[2] = 0.05  # Pequena altura para ficar visível
            point2[2] = 0.05
            
            p.addUserDebugLine(
                point1,
                point2,
                lineColorRGB=[0.0, 0.0, 1.0],  # Azul sólido
                lineWidth=3,
                lifeTime=0  # Permanente
            )
    
    def create_environment(self):
        """Cria o ambiente com obstáculos posicionados estrategicamente"""
        self.obstacles = []
        
        # Obstáculos posicionados para criar um cenário interessante
        # (similar à imagem: alguns na trajetória de referência, outros ao redor)
        obstacle_positions = [
            [-1.0, 1.5, 0.5],   # Obstáculo 1
            [0.5, 0.0, 0.5],    # Obstáculo 2 (no meio do caminho)
            [-0.5, -1.0, 0.5],  # Obstáculo 3
            [1.5, 1.0, 0.5],    # Obstáculo 4
            [-1.5, -0.5, 0.5],  # Obstáculo 5
            [0.0, 2.0, 0.5],    # Obstáculo 6
            [2.0, -1.5, 0.5],   # Obstáculo 7
            [-2.0, -2.0, 0.5],  # Obstáculo 8
        ]
        
        # Tamanhos variados (retângulos, hexágonos simulados, círculo, etc.)
        obstacle_sizes = [
            [0.3, 0.3, 0.5],   # Quadrado
            [0.4, 0.25, 0.5],  # Retângulo
            [0.25, 0.4, 0.5],  # Retângulo vertical
            [0.35, 0.35, 0.5], # Quadrado
            [0.3, 0.3, 0.5],   # Quadrado
            [0.2, 0.2, 0.5],   # Pequeno
            [0.3, 0.3, 0.5],   # Quadrado
            [0.25, 0.25, 0.5], # Quadrado
        ]
        
        for i, (pos, size) in enumerate(zip(obstacle_positions, obstacle_sizes)):
            # Cores cinza para os obstáculos
            obstacle_visual = p.createVisualShape(
                shapeType=p.GEOM_BOX,
                halfExtents=size,
                rgbaColor=[0.5, 0.5, 0.5, 1]  # Cinza
            )
            obstacle_collision = p.createCollisionShape(
                shapeType=p.GEOM_BOX,
                halfExtents=size
            )
            
            obstacle_id = p.createMultiBody(
                baseMass=0,  # Estático
                baseCollisionShapeIndex=obstacle_collision,
                baseVisualShapeIndex=obstacle_visual,
                basePosition=pos
            )
            
            self.obstacles.append(obstacle_id)
        
        # Criar marcadores de start e goal
        # Start point (quadrado vermelho com centro branco)
        start_marker = p.createVisualShape(
            shapeType=p.GEOM_BOX,
            halfExtents=[0.15, 0.15, 0.01],
            rgbaColor=[1.0, 0.0, 0.0, 1]  # Vermelho
        )
        p.createMultiBody(
            baseMass=0,
            baseVisualShapeIndex=start_marker,
            basePosition=[self.start_point[0], self.start_point[1], 0.01]
        )
        
        # Goal point (círculo vermelho)
        goal_marker = p.createVisualShape(
            shapeType=p.GEOM_SPHERE,
            radius=0.1,
            rgbaColor=[1.0, 0.0, 0.0, 1]  # Vermelho
        )
        p.createMultiBody(
            baseMass=0,
            baseVisualShapeIndex=goal_marker,
            basePosition=[self.goal_point[0], self.goal_point[1], 0.1]
        )
    
    def get_sensor_readings(self) -> dict:
        """Obtém leituras dos sensores ultrassônicos"""
        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        
        readings = {}
        for direction, sensor in self.sensors.items():
            readings[direction] = sensor.measure(pos, orn, direction)
        
        return readings
    
    def scan_environment(self, sensor_readings: dict) -> dict:
        """
        Escaneia o ambiente e avalia qual direção é melhor para seguir
        
        Returns:
            dict com informações sobre o melhor caminho
        """
        # Avaliar cada direção considerando:
        # 1. Espaço livre (distância até obstáculo)
        # 2. Direção em relação ao goal
        # 3. Custo de desvio
        
        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        euler = p.getEulerFromQuaternion(orn)
        current_yaw = euler[2]
        
        # Direção para o goal
        dx = self.goal_point[0] - pos[0]
        dy = self.goal_point[1] - pos[1]
        goal_yaw = math.atan2(dy, dx)
        goal_distance = math.sqrt(dx**2 + dy**2)
        
        # Ângulos de cada direção de sensor
        directions = {
            'front': 0.0,
            'front_left': math.pi/4,
            'front_right': -math.pi/4,
            'left': math.pi/2,
            'right': -math.pi/2,
            'back_left': 3*math.pi/4,
            'back_right': -3*math.pi/4
        }
        
        best_direction = None
        best_score = -float('inf')
        direction_scores = {}
        
        for dir_name, angle_offset in directions.items():
            if dir_name not in sensor_readings:
                continue
                
            # Distância até obstáculo nesta direção
            distance = sensor_readings[dir_name]
            
            # Ângulo absoluto desta direção
            direction_angle = current_yaw + angle_offset
            
            # Erro angular em relação ao goal
            error_to_goal = goal_yaw - direction_angle
            error_to_goal = math.atan2(math.sin(error_to_goal), math.cos(error_to_goal))
            
            # Score baseado em:
            # - Espaço livre (maior = melhor)
            # - Alinhamento com goal (menor erro = melhor)
            # - Penalizar direções muito desalinhadas
            
            space_score = distance  # Quanto mais espaço, melhor
            alignment_score = 1.0 - abs(error_to_goal) / math.pi  # Quanto mais alinhado, melhor
            distance_bonus = 1.0 / (1.0 + goal_distance * 0.1)  # Bônus se goal está longe
            
            # Score combinado (prioriza espaço, mas considera goal)
            if distance < 0.3:
                # Muito próximo - score muito baixo
                score = -10.0
            elif distance < 0.8:
                # Próximo - score baixo, mas ainda possível
                score = space_score * 0.3 + alignment_score * 0.2
            else:
                # Espaço suficiente - score baseado em espaço e alinhamento
                score = space_score * 0.6 + alignment_score * 0.4 + distance_bonus * 0.1
            
            direction_scores[dir_name] = {
                'score': score,
                'distance': distance,
                'angle': direction_angle,
                'error_to_goal': error_to_goal
            }
            
            if score > best_score:
                best_score = score
                best_direction = dir_name
        
        return {
            'best_direction': best_direction,
            'best_score': best_score,
            'scores': direction_scores,
            'goal_yaw': goal_yaw,
            'current_yaw': current_yaw
        }
    
    def check_collision(self) -> bool:
        """Verifica se houve colisão"""
        contacts = p.getContactPoints(self.robot_id)
        
        for contact in contacts:
            # Ignorar contato com o plano
            if contact[2] != self.plane_id:
                return True
        
        return False
    
    def get_direction_to_goal(self) -> float:
        """Retorna o ângulo necessário para ir em direção ao goal"""
        try:
            pos, orn = p.getBasePositionAndOrientation(self.robot_id)
            euler = p.getEulerFromQuaternion(orn)
            current_yaw = euler[2]
            
            # Direção para o goal
            dx = self.goal_point[0] - pos[0]
            dy = self.goal_point[1] - pos[1]
            
            # Se já está muito próximo do goal, ainda calcular direção (mas com peso menor)
            dist_to_goal = math.sqrt(dx**2 + dy**2)
            if dist_to_goal < 0.15:
                # Muito próximo - retornar erro zero para parar suavemente
                return 0.0
            
            goal_yaw = math.atan2(dy, dx)
            
            # Erro angular (normalizar para [-pi, pi])
            error_yaw = goal_yaw - current_yaw
            error_yaw = math.atan2(math.sin(error_yaw), math.cos(error_yaw))
            
            return error_yaw
        except:
            return 0.0  # Retornar zero em caso de erro
    
    def compute_velocities(self, sensor_readings: dict, dt: float) -> Tuple[float, float]:
        """
        Calcula as velocidades linear e angular baseado no escaneamento do ambiente
        Retorna (velocidade_linear, velocidade_angular) em m/s e rad/s
        
        Args:
            sensor_readings: Leituras dos sensores
            dt: Intervalo de tempo
            
        Returns:
            (velocidade_linear, velocidade_angular) em m/s e rad/s
        """
        # Escanear ambiente para encontrar melhor direção
        scan_result = self.scan_environment(sensor_readings)
        
        # Distâncias principais (para compatibilidade)
        dist_front = sensor_readings.get('front', 2.0)
        dist_left = sensor_readings.get('left', 2.0)
        dist_right = sensor_readings.get('right', 2.0)
        dist_front_left = sensor_readings.get('front_left', 2.0)
        dist_front_right = sensor_readings.get('front_right', 2.0)
        
        # Velocidade base (avançar)
        base_velocity = 3.0
        
        # Verificar se há obstáculo muito próximo (emergência)
        min_distance = min(dist_front, dist_left, dist_right, dist_front_left, dist_front_right)
        
        # Verificar distância ao goal
        pos, _ = p.getBasePositionAndOrientation(self.robot_id)
        dist_to_goal = math.sqrt(
            (pos[0] - self.goal_point[0])**2 + 
            (pos[1] - self.goal_point[1])**2
        )
        
        # Se muito próximo do goal, ignorar obstáculos e ir direto
        if dist_to_goal < 0.5:
            error_yaw = self.get_direction_to_goal()
            angular_correction = self.path_controller.compute(error_yaw, dt)
            angular_correction = np.clip(angular_correction, -1.5, 1.5)
            base_velocity = 2.0  # Velocidade reduzida quando próximo do goal
            vel_left = base_velocity - angular_correction
            vel_right = base_velocity + angular_correction
            linear_velocity = (vel_left + vel_right) * self.wheel_radius / 2.0
            angular_velocity = (vel_right - vel_left) * self.wheel_radius / self.base_width
            linear_velocity = np.clip(linear_velocity, -self.max_velocity, self.max_velocity)
            angular_velocity = np.clip(angular_velocity, -self.max_angular_velocity, self.max_angular_velocity)
            return linear_velocity, angular_velocity
        
        # Verificar se há obstáculo muito próximo (preso)
        very_close = min_distance < 0.3
        
        if very_close:
            # Modo de emergência: dar ré e virar, MAS sempre considerando goal
            if dist_front < 0.3:
                # Muito próximo na frente - dar ré e virar
                base_velocity = -1.5  # Ré
                
                # Calcular direção para o goal (mesmo dando ré, queremos ir na direção certa)
                error_yaw = self.get_direction_to_goal()
                goal_turn = self.path_controller.compute(error_yaw, dt) * 0.2  # 20% seguir goal
                
                # Virar na direção com mais espaço (evasão)
                if dist_left > dist_right:
                    # Mais espaço à esquerda, virar à esquerda
                    evasao_turn = 1.5  # Correção de evasão
                else:
                    # Mais espaço à direita, virar à direita
                    evasao_turn = -1.5  # Correção de evasão
                
                # Combinar: 80% evasão, 20% seguir goal
                total_turn = 0.8 * evasao_turn + 0.2 * goal_turn
                
                vel_left = base_velocity * (1.0 - total_turn * 0.5)
                vel_right = base_velocity * (1.0 + total_turn * 0.5)
            else:
                # Muito próximo nas laterais - virar agressivamente MAS considerando goal
                base_velocity = 1.0  # Reduzido para evitar colisão
                
                # Calcular direção para o goal
                error_yaw = self.get_direction_to_goal()
                goal_turn = self.path_controller.compute(error_yaw, dt) * 0.3  # 30% seguir goal
                
                # Evasão agressiva
                if dist_left < dist_right:
                    # Obstáculo à esquerda, virar à direita
                    evasao_turn = 1.8
                else:
                    # Obstáculo à direita, virar à esquerda
                    evasao_turn = -1.8
                
                # Combinar: 70% evasão, 30% seguir goal
                total_turn = 0.7 * evasao_turn + 0.3 * goal_turn
                
                vel_left = base_velocity * (1.0 - total_turn)
                vel_right = base_velocity * (1.0 + total_turn)
        elif min_distance < 0.8:
            # Obstáculo próximo - usar escaneamento para escolher melhor direção
            base_velocity = 2.0  # Reduzir velocidade quando próximo
            
            # Usar a melhor direção encontrada no escaneamento
            best_dir = scan_result['best_direction']
            best_info = scan_result['scores'][best_dir]
            
            # Calcular correção angular para ir na melhor direção
            target_angle = best_info['angle']
            current_yaw = scan_result['current_yaw']
            error_angle = target_angle - current_yaw
            error_angle = math.atan2(math.sin(error_angle), math.cos(error_angle))
            
            # Controlador para seguir a melhor direção
            angular_correction = self.path_controller.compute(error_angle, dt)
            angular_correction = np.clip(angular_correction, -1.5, 1.5)
            
            # Reduzir velocidade se muito próximo
            if min_distance < 0.5:
                base_velocity *= 0.6
            
            vel_left = base_velocity - angular_correction
            vel_right = base_velocity + angular_correction
        elif min_distance < 1.5:
            # Obstáculo moderado - usar escaneamento para escolher caminho otimizado
            base_velocity = 2.5
            
            # Usar melhor direção do escaneamento, mas com mais peso no goal
            best_dir = scan_result['best_direction']
            best_info = scan_result['scores'][best_dir]
            
            # Calcular direção para o goal
            error_yaw = self.get_direction_to_goal()
            
            # Calcular correção para melhor direção (60%) e goal (40%)
            target_angle = best_info['angle']
            current_yaw = scan_result['current_yaw']
            error_best = target_angle - current_yaw
            error_best = math.atan2(math.sin(error_best), math.cos(error_best))
            
            best_correction = self.path_controller.compute(error_best, dt) * 0.6
            goal_correction = self.path_controller.compute(error_yaw, dt) * 0.4
            
            total_correction = best_correction + goal_correction
            total_correction = np.clip(total_correction, -1.2, 1.2)
            
            # Atualizar métricas
            error_lateral = dist_left - dist_right
            self.metrics['erro_medio_lateral'].append(abs(error_lateral))
            
            # Reduzir velocidade se muito próximo
            if dist_front < 1.0:
                base_velocity *= 0.7
            
            vel_left = base_velocity - total_correction
            vel_right = base_velocity + total_correction
        else:
            # Sem obstáculos próximos - seguir em direção ao goal
            error_yaw = self.get_direction_to_goal()
            
            # Controlador para seguir a direção do goal
            angular_correction = self.path_controller.compute(error_yaw, dt)
            angular_correction = np.clip(angular_correction, -1.5, 1.5)
            
            # Velocidades para seguir a direção (aumentar velocidade quando seguro)
            # Ajustar velocidade baseada na distância ao goal
            pos, _ = p.getBasePositionAndOrientation(self.robot_id)
            dist_to_goal = math.sqrt(
                (pos[0] - self.goal_point[0])**2 + 
                (pos[1] - self.goal_point[1])**2
            )
            
            # Velocidade proporcional à distância (mais rápido quando longe, mais devagar quando perto)
            if dist_to_goal > 3.0:
                base_velocity = 4.5  # Máxima quando longe
            elif dist_to_goal > 1.5:
                base_velocity = 4.0  # Alta quando médio
            else:
                base_velocity = 3.0  # Reduzida quando perto
            
            vel_left = base_velocity - angular_correction
            vel_right = base_velocity + angular_correction
        
        # Converter velocidades das rodas para velocidade linear e angular
        linear_velocity = (vel_left + vel_right) * self.wheel_radius / 2.0
        angular_velocity = (vel_right - vel_left) * self.wheel_radius / self.base_width
        
        # Limitar velocidades
        linear_velocity = np.clip(linear_velocity, -self.max_velocity, self.max_velocity)
        angular_velocity = np.clip(angular_velocity, -self.max_angular_velocity, self.max_angular_velocity)
        
        return linear_velocity, angular_velocity
    
    def apply_velocities(self, linear_velocity: float, angular_velocity: float):
        """
        Aplica velocidades usando forças e torques (como o robô aspirador)
        Isso cria movimento mais suave e realista
        
        Args:
            linear_velocity: Velocidade linear desejada (m/s)
            angular_velocity: Velocidade angular desejada (rad/s)
        """
        # Velocidades já estão em m/s e rad/s
        linear_desired = linear_velocity
        angular_desired = angular_velocity
        
        # Limitar velocidades
        max_linear = 8.0  # m/s (aumentado para movimento mais rápido)
        max_angular = 10.0  # rad/s
        linear_desired = np.clip(linear_desired, -max_linear, max_linear)
        angular_desired = np.clip(angular_desired, -max_angular, max_angular)
        
        # Obter estado atual
        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        euler = p.getEulerFromQuaternion(orn)
        yaw = euler[2]
        roll, pitch, _ = euler
        
        # Obter velocidade atual
        current_linear, current_angular = p.getBaseVelocity(self.robot_id)
        current_vel_x = current_linear[0]
        current_vel_y = current_linear[1]
        current_angular_z = current_angular[2]
        
        # Calcular velocidade desejada no frame do mundo
        target_vel_x = linear_desired * math.cos(yaw)
        target_vel_y = linear_desired * math.sin(yaw)
        target_angular_z = angular_desired
        
        # Calcular erro de velocidade (controle PD)
        error_x = target_vel_x - current_vel_x
        error_y = target_vel_y - current_vel_y
        error_angular = target_angular_z - current_angular_z
        
        # Ganhos do controlador (similar ao robô aspirador, mas mais suaves)
        kp_linear = 100.0  # Ganho proporcional linear (reduzido para movimento mais suave)
        kd_linear = 15.0   # Amortecimento linear (aumentado para evitar oscilações)
        kp_angular = 70.0  # Ganho proporcional angular (reduzido)
        kd_angular = 12.0  # Amortecimento angular (aumentado)
        kp_orientation = 100.0  # Ganho para manter plano
        
        # Calcular forças (termo proporcional + derivativo)
        force_x = error_x * kp_linear - current_vel_x * kd_linear
        force_y = error_y * kp_linear - current_vel_y * kd_linear
        torque_z = error_angular * kp_angular - current_angular_z * kd_angular
        
        # Correção de orientação para manter plano (roll e pitch = 0)
        torque_roll = -roll * kp_orientation
        torque_pitch = -pitch * kp_orientation
        
        # Limitar forças e torques
        max_force = 400.0
        max_torque = 200.0
        max_torque_orientation = 500.0
        
        force_x = np.clip(force_x, -max_force, max_force)
        force_y = np.clip(force_y, -max_force, max_force)
        torque_z = np.clip(torque_z, -max_torque, max_torque)
        torque_roll = np.clip(torque_roll, -max_torque_orientation, max_torque_orientation)
        torque_pitch = np.clip(torque_pitch, -max_torque_orientation, max_torque_orientation)
        
        # Aplicar forças no centro de massa
        p.applyExternalForce(
            self.robot_id,
            -1,  # Base do corpo
            forceObj=[force_x, force_y, 0],
            posObj=[0, 0, 0],
            flags=p.WORLD_FRAME
        )
        
        # Aplicar torques: Z para rotação horizontal, X e Y para manter plano
        p.applyExternalTorque(
            self.robot_id,
            -1,  # Base do corpo
            torqueObj=[torque_roll, torque_pitch, torque_z],
            flags=p.WORLD_FRAME
        )
    
    def update_metrics(self) -> bool:
        """Atualiza as métricas e retorna True se chegou ao goal"""
        # Verificar colisão
        if self.check_collision():
            current_time = time.time()
            if (self.metrics['ultima_colisao'] is None or 
                current_time - self.metrics['ultima_colisao'] > 0.5):  # Debounce
                self.metrics['numero_colisoes'] += 1
                self.metrics['ultima_colisao'] = current_time
        
        # Calcular distância percorrida
        pos, _ = p.getBasePositionAndOrientation(self.robot_id)
        if self.metrics['posicao_anterior']:
            dx = pos[0] - self.metrics['posicao_anterior'][0]
            dy = pos[1] - self.metrics['posicao_anterior'][1]
            distance = math.sqrt(dx**2 + dy**2)
            self.metrics['distancia_percorrida'] += distance
        self.metrics['posicao_anterior'] = pos
        
        # Verificar se chegou ao goal
        dist_to_goal = math.sqrt(
            (pos[0] - self.goal_point[0])**2 + 
            (pos[1] - self.goal_point[1])**2
        )
        if dist_to_goal < 0.3:  # Tolerância para considerar que chegou
            return True  # Sinalizar que chegou ao destino
        return False
    
    def get_metrics(self) -> dict:
        """Retorna as métricas atuais"""
        erro_medio_lateral = (np.mean(self.metrics['erro_medio_lateral']) 
                            if self.metrics['erro_medio_lateral'] else 0.0)
        
        return {
            'numero_colisoes': self.metrics['numero_colisoes'],
            'tempo_reacao_medio': (np.mean(self.metrics['tempo_reacao']) 
                                  if self.metrics['tempo_reacao'] else 0.0),
            'distancia_percorrida_sem_impacto': self.metrics['distancia_percorrida'],
            'erro_medio_lateral': erro_medio_lateral
        }
    
    def send_metrics_to_node_red(self):
        """Envia métricas para o Node-RED"""
        metrics = self.get_metrics()
        self.node_red.send_metrics('robo_movel', metrics)
    
    def step(self, dt: float = 1.0/240.0):
        """Executa um passo de simulação"""
        try:
            # Ler sensores
            sensor_readings = self.get_sensor_readings()
            
            # Calcular velocidades (linear e angular)
            linear_vel, angular_vel = self.compute_velocities(sensor_readings, dt)
            
            # Aplicar velocidades usando forças e torques
            self.apply_velocities(linear_vel, angular_vel)
            
            # Atualizar trajetória real (linha azul) - desenhar dinamicamente
            pos, _ = p.getBasePositionAndOrientation(self.robot_id)
            # Adicionar ponto apenas se moveu significativamente (para não sobrecarregar)
            if len(self.actual_trajectory) == 0:
                # Primeiro ponto
                self.actual_trajectory.append([pos[0], pos[1], pos[2]])
            else:
                # Verificar se moveu o suficiente para adicionar novo ponto
                dist_moved = math.sqrt((pos[0] - self.actual_trajectory[-1][0])**2 + 
                                      (pos[1] - self.actual_trajectory[-1][1])**2)
                if dist_moved > 0.05:  # Adicionar ponto a cada 5cm de movimento
                    self.actual_trajectory.append([pos[0], pos[1], pos[2]])
                    # Desenhar o novo segmento da trajetória azul
                    if self.use_gui and len(self.actual_trajectory) > 1:
                        try:
                            self.update_trajectory_drawing()
                        except:
                            pass  # Ignorar erros de desenho
            
            # Atualizar métricas
            self.update_metrics()
            
            # Passo de simulação
            p.stepSimulation()
            
            return sensor_readings, (linear_vel, angular_vel)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Se o servidor foi desconectado (usuário fechou a janela)
            if "Not connected" in str(e) or "physics server" in str(e).lower():
                raise KeyboardInterrupt("Servidor de física desconectado")
            # Log do erro mas não quebra a simulação
            print(f"Erro no step: {e}")
            # Tentar continuar
            try:
                p.stepSimulation()
            except:
                raise KeyboardInterrupt("Erro crítico na simulação")
            return {}, (0.0, 0.0)
    
    def run_simulation(self, duration: float = 60.0):
        """Executa a simulação"""
        start_time = time.time()
        step_count = 0
        goal_reached = False
        
        print("=== Robô Móvel Diferencial com Evasão de Obstáculos ===\n")
        print(f"Start: {self.start_point[:2]} | Goal: {self.goal_point[:2]}")
        print("Iniciando simulação...\n")
        
        # Aguardar um pouco mais para garantir estabilização completa
        if self.use_gui:
            for _ in range(30):
                p.stepSimulation()
                time.sleep(0.01)
        
        try:
            while time.time() - start_time < duration and not goal_reached:
                current_time = time.time() - start_time
                dt = 1.0/240.0
                
                # Executar passo
                try:
                    sensor_readings, _ = self.step(dt)
                except KeyboardInterrupt:
                    print("\nSimulação interrompida pelo usuário")
                    break
                except Exception as e:
                    print(f"Erro durante simulação: {e}")
                    # Tentar continuar
                    continue
                
                # Verificar se chegou ao goal
                try:
                    goal_reached = self.update_metrics()
                except:
                    goal_reached = False
                
                # Exibir informações a cada segundo
                if step_count % 240 == 0:
                    try:
                        self.send_metrics_to_node_red()
                        current_pos, _ = p.getBasePositionAndOrientation(self.robot_id)
                        dist_to_goal = math.sqrt(
                            (current_pos[0] - self.goal_point[0])**2 + 
                            (current_pos[1] - self.goal_point[1])**2
                        )
                        print(f"Tempo: {current_time:.2f}s | "
                              f"Pos: [{current_pos[0]:.2f}, {current_pos[1]:.2f}] | "
                              f"Dist. Goal: {dist_to_goal:.2f}m | "
                              f"Front: {sensor_readings.get('front', 0):.2f}m | "
                              f"Colisões: {self.metrics['numero_colisoes']}")
                    except Exception as e:
                        print(f"Erro ao exibir informações: {e}")
                
                step_count += 1
                
                if self.use_gui:
                    time.sleep(dt)
        except KeyboardInterrupt:
            print("\nSimulação interrompida")
        except Exception as e:
            print(f"\nErro crítico na simulação: {e}")
            import traceback
            traceback.print_exc()
        
        if goal_reached:
            print("\n✓ Goal alcançado!")
        else:
            print("\nTempo limite atingido")
        
        # Enviar métricas finais
        self.send_metrics_to_node_red()
        print("\n=== Métricas Finais ===")
        print(self.get_metrics())
    
    def cleanup(self):
        """Limpa recursos"""
        try:
            if self.physics_client is not None:
                p.disconnect(self.physics_client)
        except:
            pass  # Já desconectado ou erro ao desconectar
        self.node_red.disconnect()


def main():
    """Função principal"""
    robo = RoboMovel(use_gui=True)
    
    try:
        # Executar simulação por 30 segundos
        robo.run_simulation(duration=30.0)
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário")
    finally:
        robo.cleanup()


if __name__ == "__main__":
    main()

