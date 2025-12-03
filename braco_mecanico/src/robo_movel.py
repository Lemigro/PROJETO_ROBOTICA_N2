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
        
        # CORREÇÃO: Adicionar um leve deslocamento em Z no destino do raio
        # Isso evita que o raio bata no chão se o robô inclinar um pouco para frente ao frear
        ray_to = [
            robot_pos[0] + self.max_range * math.cos(angle),
            robot_pos[1] + self.max_range * math.sin(angle),
            robot_pos[2] + 0.05  # Levanta levemente a ponta do raio
        ]
        
        # Realizar raycast
        hit = p.rayTest(ray_from, ray_to)
        
        if hit[0][0] != -1:  # Colisão detectada
            hit_pos = hit[0][3]
            
            # Filtro extra: Ignorar colisão se for o próprio chão (plane)
            # Se bateu muito baixo, é chão/ruído - ignorar
            if hit_pos[2] < 0.05:  # Muito baixo, provavelmente é o chão
                distance = self.max_range
            else:
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
        self.max_velocity = 12.0  # Velocidade máxima linear (m/s) - aumentado para movimento mais rápido
        self.max_angular_velocity = 15.0  # Velocidade angular máxima (rad/s) - aumentado para giros mais rápidos
        
        # Trajetórias
        self.reference_trajectory = []  # Trajetória de referência (ideal)
        self.actual_trajectory = []     # Trajetória real (com evasão)
        self.current_trajectory_index = 0  # Índice do ponto atual na trajetória (sempre avança)
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
        
        # Resetar índice da trajetória
        self.current_trajectory_index = 0
        
        # Inicializar linha dos "olhos" do robô (visualização do foco no goal)
        self.eyes_line_id = None
        
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
        
        # Resetar índice da trajetória
        self.current_trajectory_index = 0
        
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
        # Criar pontos ao longo da linha reta do START para o GOAL
        num_points = 50
        for i in range(num_points + 1):
            t = i / num_points
            # Garantir que vai do START para o GOAL (nunca ao contrário)
            x = self.start_point[0] + t * (self.goal_point[0] - self.start_point[0])
            y = self.start_point[1] + t * (self.goal_point[1] - self.start_point[1])
            z = self.start_point[2] + t * (self.goal_point[2] - self.start_point[2])
            self.reference_trajectory.append([x, y, z])
        
        # Garantir que o índice inicial está no início
        self.current_trajectory_index = 0
    
    def draw_robot_eyes(self):
        """
        Desenha os 'olhos' do robô - uma linha amarela que aponta para o goal
        A linha PARA quando encontra um obstáculo (não ultrapassa)
        """
        if not self.use_gui:
            return
        
        # Limpar linha anterior
        if self.eyes_line_id is not None:
            try:
                p.removeUserDebugItem(self.eyes_line_id)
            except:
                pass
        
        # Obter posição e orientação do robô
        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        
        # Calcular direção para o goal
        goal_dx = self.goal_point[0] - pos[0]
        goal_dy = self.goal_point[1] - pos[1]
        goal_dist = math.sqrt(goal_dx**2 + goal_dy**2)
        
        if goal_dist > 0.01:
            goal_dir_x = goal_dx / goal_dist
            goal_dir_y = goal_dy / goal_dist
            
            # Ponto inicial (centro do robô, ligeiramente acima)
            start_point = [pos[0], pos[1], pos[2] + 0.15]
            
            # Fazer raycast para detectar obstáculos na direção do goal
            # A linha para quando encontra um obstáculo
            max_look_length = min(3.0, goal_dist)
            ray_from = start_point
            ray_to = [
                pos[0] + goal_dir_x * max_look_length,
                pos[1] + goal_dir_y * max_look_length,
                pos[2] + 0.15
            ]
            
            # Raycast para detectar obstáculos
            hit = p.rayTest(ray_from, ray_to)
            
            if hit[0][0] != -1:  # Colisão detectada
                hit_pos = hit[0][3]
                # Calcular distância até o obstáculo
                obstacle_dist = math.sqrt(
                    (hit_pos[0] - pos[0])**2 + 
                    (hit_pos[1] - pos[1])**2
                )
                # A linha para um pouco antes do obstáculo (0.2m de margem)
                look_length = max(0.3, obstacle_dist - 0.2)
            else:
                # Sem obstáculo, linha vai até o goal ou 3.0m
                look_length = max_look_length
            
            # Ponto final (na direção do goal, mas para antes de obstáculos)
            end_point = [
                pos[0] + goal_dir_x * look_length,
                pos[1] + goal_dir_y * look_length,
                pos[2] + 0.15
            ]
            
            # Desenhar linha amarela brilhante
            try:
                self.eyes_line_id = p.addUserDebugLine(
                    start_point,
                    end_point,
                    lineColorRGB=[1.0, 1.0, 0.0],  # Amarelo brilhante
                    lineWidth=6,
                    lifeTime=0.1  # Atualizar a cada frame
                )
            except:
                pass
    
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
    
    def find_gaps(self, sensor_readings: dict) -> List[dict]:
        """
        Identifica brechas/passagens entre obstáculos escaneando ao redor
        
        Returns:
            Lista de brechas encontradas, ordenadas por qualidade (melhor primeiro)
        """
        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        euler = p.getEulerFromQuaternion(orn)
        current_yaw = euler[2]
        
        # Direção para o goal
        dx = self.goal_point[0] - pos[0]
        dy = self.goal_point[1] - pos[1]
        goal_yaw = math.atan2(dy, dx)
        
        # Ângulos de cada direção de sensor (apenas à frente - nunca para trás)
        directions = {
            'front': 0.0,
            'front_left': math.pi/4,
            'front_right': -math.pi/4,
            'left': math.pi/2,
            'right': -math.pi/2
        }
        
        gaps = []
        
        # Analisar pares de sensores adjacentes para encontrar brechas
        # Brechas são espaços entre obstáculos onde o robô pode passar
        sensor_pairs = [
            ('front_left', 'front'),
            ('front', 'front_right'),
            ('left', 'front_left'),
            ('front_right', 'right'),
            ('front_left', 'left'),  # Brecha entre esquerda e frente-esquerda
            ('front_right', 'right')  # Brecha entre direita e frente-direita
        ]
        
        for dir1, dir2 in sensor_pairs:
            if dir1 not in sensor_readings or dir2 not in sensor_readings:
                continue
            
            dist1 = sensor_readings[dir1]
            dist2 = sensor_readings[dir2]
            
            # Uma brecha existe se ambos os sensores mostram espaço suficiente
            min_dist = min(dist1, dist2)
            avg_dist = (dist1 + dist2) / 2.0
            
            # CONSIDERAR BRECHAS MENORES: Aceitar brechas mais estreitas para passar entre obstáculos
            # Reduzir limite mínimo para 0.25m (robô tem ~0.3m de largura, então precisa de pelo menos 0.25m)
            # E média de pelo menos 0.4m (brecha mínima para passar)
            if min_dist > 0.25 and avg_dist > 0.4:
                # Calcular direção média da brecha
                angle1 = current_yaw + directions.get(dir1, 0.0)
                angle2 = current_yaw + directions.get(dir2, 0.0)
                gap_angle = (angle1 + angle2) / 2.0
                
                # Normalizar ângulo
                gap_angle = math.atan2(math.sin(gap_angle), math.cos(gap_angle))
                
                # Erro angular em relação ao goal
                error_to_goal = goal_yaw - gap_angle
                error_to_goal = math.atan2(math.sin(error_to_goal), math.cos(error_to_goal))
                
                # Score da brecha baseado em:
                # - Alinhamento com goal - MUITO IMPORTANTE (prioridade máxima)
                # - Largura da brecha (avg_dist) - importante mas secundário
                # - Distância mínima (garantir que passa) - importante
                # PRIORIZAR brechas alinhadas com goal mesmo que sejam estreitas
                alignment_score = (1.0 - abs(error_to_goal) / math.pi) * 10.0  # Alinhamento com goal (PRIORIDADE MÁXIMA)
                width_score = avg_dist * 2.0  # Largura (importante mas secundária)
                safety_score = min_dist * 1.5  # Segurança (garantir que passa)
                
                # Bônus extra se a brecha está diretamente na direção do goal
                if abs(error_to_goal) < math.pi/6:  # Menos de 30° de diferença
                    alignment_score *= 1.5  # Bônus de 50% para brechas muito alinhadas
                
                gap_score = alignment_score + width_score + safety_score
                
                gaps.append({
                    'direction': f"{dir1}_{dir2}",
                    'angle': gap_angle,
                    'width': avg_dist,
                    'min_distance': min_dist,
                    'score': gap_score,
                    'error_to_goal': error_to_goal
                })
        
        # Ordenar brechas por score (melhor primeiro)
        gaps.sort(key=lambda x: x['score'], reverse=True)
        
        return gaps
    
    def scan_environment(self, sensor_readings: dict) -> dict:
        """
        Escaneia o ambiente e avalia qual direção é melhor para seguir
        MELHORADO: Identifica brechas entre obstáculos ao invés de apenas evitar
        
        Returns:
            dict com informações sobre o melhor caminho
        """
        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        euler = p.getEulerFromQuaternion(orn)
        current_yaw = euler[2]
        
        # Direção para o goal
        dx = self.goal_point[0] - pos[0]
        dy = self.goal_point[1] - pos[1]
        goal_yaw = math.atan2(dy, dx)
        goal_distance = math.sqrt(dx**2 + dy**2)
        
        # Primeiro, tentar encontrar brechas (passagens entre obstáculos)
        gaps = self.find_gaps(sensor_readings)
        
        # Se encontrou brechas, usar a melhor (ACEITAR BRECHAS MENORES)
        if gaps and gaps[0]['min_distance'] > 0.25:
            best_gap = gaps[0]
            return {
                'best_direction': 'gap',
                'best_score': best_gap['score'],
                'best_angle': best_gap['angle'],
                'gap_info': best_gap,
                'gaps': gaps,
                'goal_yaw': goal_yaw,
                'current_yaw': current_yaw
            }
        
        # Se não encontrou brechas, usar lógica de evasão tradicional
        # Mas SEMPRE priorizando direções à frente
        directions = {
            'front': 0.0,
            'front_left': math.pi/4,
            'front_right': -math.pi/4,
            'left': math.pi/2,
            'right': -math.pi/2
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
            # - Alinhamento com goal (menor erro = melhor) - PRIORIDADE ALTA
            # - Penalizar direções muito desalinhadas
            
            space_score = distance  # Quanto mais espaço, melhor
            alignment_score = (1.0 - abs(error_to_goal) / math.pi) * 5.0  # Aumentado para priorizar goal
            distance_bonus = 1.0 / (1.0 + goal_distance * 0.1)  # Bônus se goal está longe
            
            # Score combinado (prioriza alinhamento com goal)
            if distance < 0.3:
                # Muito próximo - score muito baixo, mas ainda possível se for direção do goal
                if abs(error_to_goal) < math.pi / 6:  # Se está alinhado com goal (30°)
                    score = space_score * 0.5 + alignment_score * 0.5  # Ainda tenta
                else:
                    score = -10.0
            elif distance < 0.6:
                # Próximo - score baseado principalmente em alinhamento
                score = space_score * 0.2 + alignment_score * 0.8
            else:
                # Espaço suficiente - score baseado em espaço e alinhamento
                score = space_score * 0.4 + alignment_score * 0.6 + distance_bonus * 0.1
            
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
            'current_yaw': current_yaw,
            'gaps': gaps
        }
    
    def check_collision(self) -> bool:
        """Verifica se houve colisão"""
        contacts = p.getContactPoints(self.robot_id)
        
        for contact in contacts:
            # Ignorar contato com o plano
            if contact[2] != self.plane_id:
                return True
        
        return False
    
    def get_closest_point_on_trajectory(self, current_pos: List[float], look_ahead: float = 0.8) -> Tuple[List[float], int]:
        """
        Encontra o ponto alvo na trajetória de referência.
        CORREÇÃO: Busca o ponto mais próximo globalmente no segmento futuro para evitar ficar preso.
        Isso resolve o problema do "Waypoint Esquecido" onde o robô dava meia-volta.
        
        Args:
            current_pos: Posição atual do robô [x, y, z]
            look_ahead: Distância à frente para buscar o ponto alvo (m)
            
        Returns:
            (target_point, closest_idx): Ponto alvo na trajetória e índice do ponto mais próximo
        """
        if not self.reference_trajectory:
            return self.goal_point, 0
        
        # 1. Encontrar o ponto da trajetória mais próximo da posição ATUAL do robô
        # Procuramos num horizonte de índices para otimizar (ex: verificar os próximos 50 pontos)
        # Se o robô avançou muito, isso vai "pular" os pontos que ficaram para trás
        closest_dist = float('inf')
        closest_idx = self.current_trajectory_index
        
        # Otimização: Procura apenas até 50 pontos à frente ou até o fim
        # Mas sempre a partir do índice atual (nunca volta muito)
        search_start = max(0, self.current_trajectory_index - 5)  # Permitir pequeno retrocesso se necessário
        search_end = min(len(self.reference_trajectory), self.current_trajectory_index + 50)
        
        for i in range(search_start, search_end):
            p_traj = self.reference_trajectory[i]
            # Distância Euclidiana ignorando Z
            d = (p_traj[0] - current_pos[0])**2 + (p_traj[1] - current_pos[1])**2
            # Bônus para pontos à frente do índice atual (prioriza avanço)
            if i >= self.current_trajectory_index:
                d *= 0.9  # 10% de bônus para pontos à frente
            if d < closest_dist:
                closest_dist = d
                closest_idx = i
        
        # Garantir que nunca volta muito (máximo 5 pontos para trás)
        if closest_idx < self.current_trajectory_index - 5:
            closest_idx = self.current_trajectory_index
        
        # Atualiza o índice atual para o mais próximo encontrado
        # Isso garante que se o robô passou do ponto, o índice avança junto
        self.current_trajectory_index = closest_idx
        
        # 2. Aplicar o Look-Ahead (Olhar à frente)
        # A partir do ponto mais próximo, projeta uma distância à frente para suavizar a curva
        target_idx = closest_idx
        accumulated_dist = 0.0
        
        for i in range(closest_idx, len(self.reference_trajectory) - 1):
            p1 = self.reference_trajectory[i]
            p2 = self.reference_trajectory[i + 1]
            segment_dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            accumulated_dist += segment_dist
            
            if accumulated_dist >= look_ahead:
                target_idx = i + 1
                break
        
        # Se chegou ao fim da lista
        if target_idx >= len(self.reference_trajectory):
            return self.goal_point, len(self.reference_trajectory) - 1
            
        return self.reference_trajectory[target_idx], self.current_trajectory_index
    
    def get_direction_to_trajectory(self) -> float:
        """Retorna o ângulo necessário para seguir a trajetória de referência"""
        try:
            pos, orn = p.getBasePositionAndOrientation(self.robot_id)
            euler = p.getEulerFromQuaternion(orn)
            current_yaw = euler[2]
            
            # Calcular direção para o goal primeiro (para verificação)
            goal_dx = self.goal_point[0] - pos[0]
            goal_dy = self.goal_point[1] - pos[1]
            goal_yaw = math.atan2(goal_dy, goal_dx)
            
            # Encontrar ponto alvo na trajetória (sempre à frente)
            target_point, _ = self.get_closest_point_on_trajectory(pos, look_ahead=0.8)
            
            # Direção para o ponto alvo na trajetória
            dx = target_point[0] - pos[0]
            dy = target_point[1] - pos[1]
            
            dist_to_target = math.sqrt(dx**2 + dy**2)
            if dist_to_target < 0.1:
                # Muito próximo do ponto alvo, usar goal
                return self.get_direction_to_goal()
            
            target_yaw = math.atan2(dy, dx)
            
            # VERIFICAÇÃO CRÍTICA: Se a direção da trajetória está muito diferente do goal (> 45°),
            # usar goal diretamente para evitar ir na direção errada
            angle_diff = abs(target_yaw - goal_yaw)
            angle_diff = min(angle_diff, 2 * math.pi - angle_diff)  # Normalizar para [0, pi]
            
            if angle_diff > math.pi / 4:  # Mais de 45° de diferença
                # Trajetória está apontando na direção errada, usar goal
                return self.get_direction_to_goal()
            
            # Erro angular (normalizar para [-pi, pi])
            error_yaw = target_yaw - current_yaw
            error_yaw = math.atan2(math.sin(error_yaw), math.cos(error_yaw))
            
            # VERIFICAÇÃO DE SEGURANÇA: Se o erro é muito grande (> 90°), usar goal diretamente
            if abs(error_yaw) > math.pi / 2:
                return self.get_direction_to_goal()
            
            return error_yaw
        except:
            return self.get_direction_to_goal()  # Fallback para goal
    
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
            
            # DEBUG: Verificar se está indo na direção errada
            # Se o erro é muito grande (> 135°), pode estar invertido
            if abs(error_yaw) > 3 * math.pi / 4:
                # Erro muito grande, verificar se precisa inverter
                # Se o erro está próximo de 180°, significa que está olhando na direção oposta
                if abs(error_yaw) > math.pi - 0.1:
                    # Está olhando na direção oposta, corrigir
                    error_yaw = error_yaw - math.pi if error_yaw > 0 else error_yaw + math.pi
            error_yaw = math.atan2(math.sin(error_yaw), math.cos(error_yaw))
            
            return error_yaw
        except:
            return 0.0  # Retornar zero em caso de erro
    
    def compute_velocities(self, sensor_readings: dict, dt: float) -> Tuple[float, float]:
        """
        LÓGICA ULTRA SIMPLES: SEMPRE seguir a visão (goal)
        Só desviar se obstáculo muito próximo, mas sempre mantendo direção do goal
        """
        # Ler sensores
        dist_front = sensor_readings.get('front', 2.0)
        dist_left = sensor_readings.get('left', 2.0)
        dist_right = sensor_readings.get('right', 2.0)
        dist_front_left = sensor_readings.get('front_left', 2.0)
        dist_front_right = sensor_readings.get('front_right', 2.0)
        
        # Posição e orientação
        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        euler = p.getEulerFromQuaternion(orn)
        current_yaw = euler[2]
        
        # Direção para o goal (SEGUIR A VISÃO - linha amarela)
        goal_dx = self.goal_point[0] - pos[0]
        goal_dy = self.goal_point[1] - pos[1]
        goal_yaw = math.atan2(goal_dy, goal_dx)
        error_yaw_goal = goal_yaw - current_yaw
        error_yaw_goal = math.atan2(math.sin(error_yaw_goal), math.cos(error_yaw_goal))
        
        # PROTEÇÃO ABSOLUTA: Se erro > 90°, forçar correção direta
        # NUNCA permitir dar a volta
        if abs(error_yaw_goal) > math.pi / 2:
            total_turn = self.path_controller.compute(error_yaw_goal, dt) * 2.5
            base_velocity = 2.0  # Muito lento para corrigir
        else:
            # Verificar obstáculo na frente
            min_dist = min(dist_front, dist_front_left, dist_front_right)
            
            # Se há obstáculo muito próximo na frente, procurar brecha
            if min_dist < 0.4:
                # Procurar brechas (espaços entre sensores)
                gaps = []
                
                # Brecha entre front_left e front
                if dist_front_left > 0.3 and dist_front > 0.3:
                    gap_angle = current_yaw + math.pi/12
                    gap_error_to_goal = abs(goal_yaw - gap_angle)
                    gap_error_to_goal = min(gap_error_to_goal, 2*math.pi - gap_error_to_goal)
                    if gap_error_to_goal < math.pi/2:  # Brecha não muito afastada do goal
                        gaps.append((gap_angle, min(dist_front_left, dist_front), gap_error_to_goal))
                
                # Brecha entre front e front_right
                if dist_front > 0.3 and dist_front_right > 0.3:
                    gap_angle = current_yaw - math.pi/12
                    gap_error_to_goal = abs(goal_yaw - gap_angle)
                    gap_error_to_goal = min(gap_error_to_goal, 2*math.pi - gap_error_to_goal)
                    if gap_error_to_goal < math.pi/2:
                        gaps.append((gap_angle, min(dist_front, dist_front_right), gap_error_to_goal))
                
                if gaps:
                    # Encontrou brecha - IR EM DIREÇÃO A ELA
                    best_gap = min(gaps, key=lambda x: x[2])  # Mais alinhada com goal
                    gap_angle = best_gap[0]
                    gap_error = gap_angle - current_yaw
                    gap_error = math.atan2(math.sin(gap_error), math.cos(gap_error))
                    
                    # 70% brecha + 30% goal - ir em direção à brecha
                    gap_turn = self.path_controller.compute(gap_error, dt) * 0.7
                    goal_turn = self.path_controller.compute(error_yaw_goal, dt) * 0.3
                    total_turn = gap_turn + goal_turn
                    base_velocity = 5.0
                else:
                    # Sem brechas - desviar MÍNIMO mantendo direção do goal
                    if error_yaw_goal > 0:  # Goal à esquerda
                        evasao = 0.3 if dist_left > dist_right else 0.1
                    else:  # Goal à direita
                        evasao = -0.3 if dist_right > dist_left else -0.1
                    
                    # 95% goal + 5% evasão - quase direto ao goal
                    goal_turn = self.path_controller.compute(error_yaw_goal, dt) * 0.95
                    evasao_turn = evasao * 0.05
                    total_turn = goal_turn + evasao_turn
                    base_velocity = 4.0
            elif min_dist < 0.7:
                # Obstáculo próximo - pequena correção
                if dist_left > dist_right:
                    evasao = 0.15
                else:
                    evasao = -0.15
                
                # 98% goal + 2% evasão - quase direto
                goal_turn = self.path_controller.compute(error_yaw_goal, dt) * 0.98
                evasao_turn = evasao * 0.02
                total_turn = goal_turn + evasao_turn
                base_velocity = 6.0
            else:
                # SEM OBSTÁCULOS - SEGUIR VISÃO DIRETO (100% GOAL)
                total_turn = self.path_controller.compute(error_yaw_goal, dt)
                base_velocity = 7.0
        
        # Atualizar métricas
        error_lateral = dist_left - dist_right
        self.metrics['erro_medio_lateral'].append(abs(error_lateral))
        
        # Calcular velocidades
        total_turn = np.clip(total_turn, -2.0, 2.0)
        vel_left = base_velocity - total_turn
        vel_right = base_velocity + total_turn
        
        linear_velocity = (vel_left + vel_right) * self.wheel_radius / 2.0
        angular_velocity = (vel_right - vel_left) * self.wheel_radius / self.base_width
        
        # Sempre ir para frente
        linear_velocity = abs(linear_velocity)
        linear_velocity = np.clip(linear_velocity, 0, self.max_velocity)
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
        
        # Limitar velocidades usando os valores máximos da classe
        linear_desired = np.clip(linear_desired, -self.max_velocity, self.max_velocity)
        angular_desired = np.clip(angular_desired, -self.max_angular_velocity, self.max_angular_velocity)
        
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
        
        # Ganhos do controlador (aumentados para movimento mais rápido e responsivo)
        kp_linear = 150.0  # Ganho proporcional linear (aumentado para resposta mais rápida)
        kd_linear = 20.0   # Amortecimento linear (ajustado)
        kp_angular = 100.0  # Ganho proporcional angular (aumentado)
        kd_angular = 15.0  # Amortecimento angular (ajustado)
        kp_orientation = 100.0  # Ganho para manter plano
        
        # Calcular forças (termo proporcional + derivativo)
        force_x = error_x * kp_linear - current_vel_x * kd_linear
        force_y = error_y * kp_linear - current_vel_y * kd_linear
        torque_z = error_angular * kp_angular - current_angular_z * kd_angular
        
        # Correção de orientação para manter plano (roll e pitch = 0)
        torque_roll = -roll * kp_orientation
        torque_pitch = -pitch * kp_orientation
        
        # Limitar forças e torques (aumentados para movimento mais rápido)
        max_force = 600.0  # Aumentado de 400.0
        max_torque = 300.0  # Aumentado de 200.0
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
            
            # Desenhar "olhos" do robô (linha amarela apontando para o goal)
            if self.use_gui:
                try:
                    self.draw_robot_eyes()
                except:
                    pass  # Ignorar erros de desenho
            
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
    
    def run_simulation(self, duration: float = 120.0):
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
                try:
                    p.stepSimulation()
                    time.sleep(0.01)
                except:
                    break
        
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
                    try:
                        time.sleep(dt)
                    except:
                        pass
                        
        except KeyboardInterrupt:
            print("\nSimulação interrompida pelo usuário")
        except Exception as e:
            print(f"\nErro na simulação: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Sempre tentar enviar métricas finais e limpar
            try:
                if goal_reached:
                    print("\n✓ Goal alcançado!")
                else:
                    print("\nTempo limite atingido")
                
                # Enviar métricas finais
                self.send_metrics_to_node_red()
                print("\n=== Métricas Finais ===")
                print(self.get_metrics())
            except:
                pass
    
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
    robo = None
    try:
        robo = RoboMovel(use_gui=True)
        # Executar simulação por 120 segundos (tempo suficiente)
        robo.run_simulation(duration=120.0)
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário")
    except Exception as e:
        print(f"\nErro fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if robo is not None:
            try:
                robo.cleanup()
            except:
                pass


if __name__ == "__main__":
    main()

