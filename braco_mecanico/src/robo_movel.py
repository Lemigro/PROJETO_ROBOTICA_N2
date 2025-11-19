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
            direction: 'front', 'left', 'right'
            obstacles: Lista de IDs dos obstáculos
        """
        # Converter orientação para euler
        euler = p.getEulerFromQuaternion(robot_orn)
        yaw = euler[2]  # Rotação em Z
        
        # Direção do sensor
        if direction == 'front':
            angle = yaw
        elif direction == 'left':
            angle = yaw + math.pi/2
        elif direction == 'right':
            angle = yaw - math.pi/2
        else:
            angle = yaw
        
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
    
    def __init__(self, use_gui: bool = True):
        """
        Inicializa o robô móvel
        
        Args:
            use_gui: Se True, mostra a visualização
        """
        self.use_gui = use_gui
        
        # Conectar ao PyBullet
        if use_gui:
            self.physics_client = p.connect(p.GUI)
        else:
            self.physics_client = p.connect(p.DIRECT)
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        
        # Criar o plano
        self.plane_id = p.loadURDF("plane.urdf")
        
        # Parâmetros do robô (inicializar antes de criar o robô)
        self.wheel_radius = 0.1  # Raio da roda (metros)
        self.base_width = 0.3   # Largura da base (metros)
        self.max_velocity = 5.0  # Velocidade máxima (rad/s)
        
        # Métricas (inicializar antes de criar o robô)
        self.metrics = {
            'numero_colisoes': 0,
            'tempo_reacao': [],
            'distancia_percorrida': 0.0,
            'erro_medio_lateral': [],
            'posicao_anterior': None,
            'ultima_colisao': None
        }
        
        # Criar o robô
        self.create_robot()
        
        # Criar ambiente com obstáculos
        self.create_environment()
        
        # Sensores ultrassônicos
        self.sensors = {
            'front': UltrasonicSensor(max_range=2.0, noise_std=0.02),
            'left': UltrasonicSensor(max_range=1.5, noise_std=0.02),
            'right': UltrasonicSensor(max_range=1.5, noise_std=0.02)
        }
        
        # Controlador PID para desvio (ajustado)
        self.pid_controller = PIDController(kp=3.0, ki=0.15, kd=0.5)
        
        # Interface Node-RED
        self.node_red = NodeRedInterface()
        
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
        
        self.robot_id = p.createMultiBody(
            baseMass=2.0,
            baseCollisionShapeIndex=robot_collision,
            baseVisualShapeIndex=robot_visual,
            basePosition=[0, 0, 0.1],
            baseOrientation=[0, 0, 0, 1]
        )
        
        # Rodas (visual apenas)
        wheel_visual = p.createVisualShape(
            shapeType=p.GEOM_CYLINDER,
            radius=self.wheel_radius,
            length=0.05,
            rgbaColor=[0.3, 0.3, 0.3, 1]
        )
        
        # Roda esquerda
        self.wheel_left_id = p.createMultiBody(
            baseMass=0,
            baseVisualShapeIndex=wheel_visual,
            basePosition=[0, self.base_width/2, 0.1]
        )
        p.createConstraint(
            self.robot_id, -1,
            self.wheel_left_id, -1,
            jointType=p.JOINT_FIXED,
            jointAxis=[0, 0, 0],
            parentFramePosition=[0, self.base_width/2, 0],
            childFramePosition=[0, 0, 0]
        )
        
        # Roda direita
        self.wheel_right_id = p.createMultiBody(
            baseMass=0,
            baseVisualShapeIndex=wheel_visual,
            basePosition=[0, -self.base_width/2, 0.1]
        )
        p.createConstraint(
            self.robot_id, -1,
            self.wheel_right_id, -1,
            jointType=p.JOINT_FIXED,
            jointAxis=[0, 0, 0],
            parentFramePosition=[0, -self.base_width/2, 0],
            childFramePosition=[0, 0, 0]
        )
        
        # Inicializar posição anterior
        pos, _ = p.getBasePositionAndOrientation(self.robot_id)
        self.metrics['posicao_anterior'] = pos
        
    def create_environment(self):
        """Cria o ambiente com obstáculos"""
        self.obstacles = []
        
        # Criar alguns obstáculos aleatórios
        rng = np.random.default_rng(42)  # Seed para reprodutibilidade
        num_obstacles = 8
        for _ in range(num_obstacles):
            # Posição aleatória
            x = rng.uniform(-3, 3)
            y = rng.uniform(-3, 3)
            
            # Tamanho aleatório
            size = rng.uniform(0.2, 0.5)
            
            obstacle_visual = p.createVisualShape(
                shapeType=p.GEOM_BOX,
                halfExtents=[size, size, 0.5],
                rgbaColor=[0.8, 0.2, 0.2, 1]
            )
            obstacle_collision = p.createCollisionShape(
                shapeType=p.GEOM_BOX,
                halfExtents=[size, size, 0.5]
            )
            
            obstacle_id = p.createMultiBody(
                baseMass=0,  # Estático
                baseCollisionShapeIndex=obstacle_collision,
                baseVisualShapeIndex=obstacle_visual,
                basePosition=[x, y, 0.5]
            )
            
            self.obstacles.append(obstacle_id)
    
    def get_sensor_readings(self) -> dict:
        """Obtém leituras dos sensores ultrassônicos"""
        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        
        readings = {}
        for direction, sensor in self.sensors.items():
            readings[direction] = sensor.measure(pos, orn, direction)
        
        return readings
    
    def check_collision(self) -> bool:
        """Verifica se houve colisão"""
        contacts = p.getContactPoints(self.robot_id)
        
        for contact in contacts:
            # Ignorar contato com o plano
            if contact[2] != self.plane_id:
                return True
        
        return False
    
    def compute_velocities(self, sensor_readings: dict, dt: float) -> Tuple[float, float]:
        """
        Calcula as velocidades das rodas baseado nos sensores
        
        Args:
            sensor_readings: Leituras dos sensores
            dt: Intervalo de tempo
            
        Returns:
            (velocidade_esquerda, velocidade_direita)
        """
        # Distâncias
        dist_front = sensor_readings['front']
        dist_left = sensor_readings['left']
        dist_right = sensor_readings['right']
        
        # Velocidade base (avançar) - aumentada para melhor movimento
        base_velocity = 4.0
        
        # Se muito próximo na frente, reduzir velocidade
        if dist_front < 0.5:
            base_velocity *= 0.2
        elif dist_front < 1.0:
            base_velocity *= 0.5
        elif dist_front < 1.5:
            base_velocity *= 0.8
        
        # Calcular erro lateral (diferença entre esquerda e direita)
        error_lateral = dist_left - dist_right
        
        # Atualizar métricas
        self.metrics['erro_medio_lateral'].append(abs(error_lateral))
        
        # Controlador PID para desvio
        correction = self.pid_controller.compute(error_lateral, dt)
        
        # Limitar correção
        correction = np.clip(correction, -2.0, 2.0)
        
        # Calcular velocidades das rodas
        # Se obstáculo à esquerda (dist_left < dist_right), virar à direita
        # Se obstáculo à direita (dist_right < dist_left), virar à esquerda
        vel_left = base_velocity - correction
        vel_right = base_velocity + correction
        
        # Limitar velocidades
        vel_left = np.clip(vel_left, -self.max_velocity, self.max_velocity)
        vel_right = np.clip(vel_right, -self.max_velocity, self.max_velocity)
        
        return vel_left, vel_right
    
    def apply_velocities(self, vel_left: float, vel_right: float):
        """Aplica velocidades às rodas (simulação de PWM)"""
        # Calcular velocidade linear e angular
        v = (vel_right + vel_left) * self.wheel_radius / 2.0
        omega = (vel_right - vel_left) * self.wheel_radius / self.base_width
        
        # Obter orientação atual
        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        euler = p.getEulerFromQuaternion(orn)
        yaw = euler[2]
        
        # Calcular velocidade no espaço global
        vx = v * math.cos(yaw)
        vy = v * math.sin(yaw)
        
        # Aplicar velocidade linear
        p.resetBaseVelocity(
            self.robot_id,
            linearVelocity=[vx, vy, 0],
            angularVelocity=[0, 0, omega]
        )
    
    def update_metrics(self):
        """Atualiza as métricas"""
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
        # Ler sensores
        sensor_readings = self.get_sensor_readings()
        
        # Calcular velocidades
        vel_left, vel_right = self.compute_velocities(sensor_readings, dt)
        
        # Aplicar velocidades
        self.apply_velocities(vel_left, vel_right)
        
        # Atualizar métricas
        self.update_metrics()
        
        # Passo de simulação
        p.stepSimulation()
        
        return sensor_readings, (vel_left, vel_right)
    
    def run_simulation(self, duration: float = 30.0):
        """Executa a simulação"""
        start_time = time.time()
        step_count = 0
        
        print("=== Robô Móvel Diferencial com Evasão de Obstáculos ===\n")
        print("Iniciando simulação...\n")
        
        while time.time() - start_time < duration:
            current_time = time.time() - start_time
            dt = 1.0/240.0
            
            # Executar passo
            sensor_readings, _ = self.step(dt)
            
            # Exibir informações a cada segundo
            if step_count % 240 == 0:
                self.send_metrics_to_node_red()
                print(f"Tempo: {current_time:.2f}s | "
                      f"Front: {sensor_readings['front']:.2f}m | "
                      f"Left: {sensor_readings['left']:.2f}m | "
                      f"Right: {sensor_readings['right']:.2f}m | "
                      f"Colisões: {self.metrics['numero_colisoes']}")
            
            step_count += 1
            
            if self.use_gui:
                time.sleep(dt)
        
        # Enviar métricas finais
        self.send_metrics_to_node_red()
        print("\n=== Métricas Finais ===")
        print(self.get_metrics())
    
    def cleanup(self):
        """Limpa recursos"""
        p.disconnect(self.physics_client)
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

