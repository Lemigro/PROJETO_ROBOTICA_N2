"""
Manipulador Planar 2/3 DOF com Controle de Posição
Simula um braço robótico articulado em plano com controle PID
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
    """Controlador PID para uma junta"""
    
    def __init__(self, kp: float = 1.0, ki: float = 0.0, kd: float = 0.1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0
        self.max_torque = 15.0  # Limite de torque aumentado
        
    def compute(self, error: float, dt: float) -> float:
        """Calcula o torque baseado no erro"""
        # Termo proporcional
        p_term = self.kp * error
        
        # Termo integral
        self.integral += error * dt
        i_term = self.ki * self.integral
        
        # Termo derivativo
        d_term = self.kd * (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error
        
        # Torque total
        torque = p_term + i_term + d_term
        
        # Limitar torque
        torque = np.clip(torque, -self.max_torque, self.max_torque)
        
        return torque
    
    def reset(self):
        """Reseta o controlador"""
        self.integral = 0.0
        self.prev_error = 0.0


class ManipuladorPlanar:
    """Manipulador planar 2/3 DOF com controle PID"""
    
    def __init__(self, num_joints: int = 2, use_gui: bool = True):
        """
        Inicializa o manipulador
        
        Args:
            num_joints: Número de juntas (2 ou 3)
            use_gui: Se True, mostra a visualização
        """
        self.num_joints = num_joints
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
        
        # Ângulos de referência (inicializar antes de criar o manipulador)
        self.target_angles = [0.0] * self.num_joints
        
        # Criar o manipulador
        self.create_manipulator()
        
        # Controladores PID para cada junta (ajustados para melhor desempenho)
        self.controllers = [PIDController(kp=5.0, ki=0.2, kd=1.0) for _ in range(self.num_joints)]
        
        # Métricas
        self.metrics = {
            'erro_medio': [],
            'tempo_estabilizacao': None,
            'energia_total': 0.0,
            'overshoot_maximo': 0.0,
            'tempo_inicio': None,
            'estabilizado': False
        }
        
        # Interface Node-RED
        self.node_red = NodeRedInterface()
        
    def create_manipulator(self):
        """Cria o manipulador planar usando abordagem simplificada"""
        # Parâmetros do manipulador
        link_length = 0.5  # Comprimento de cada elo (metros)
        link_mass = 1.0    # Massa de cada elo (kg)
        link_radius = 0.05 # Raio do elo (metros)
        
        # Criar base fixa
        base_visual = p.createVisualShape(
            shapeType=p.GEOM_CYLINDER,
            radius=0.1,
            length=0.2,
            rgbaColor=[0.5, 0.5, 0.5, 1]
        )
        base_collision = p.createCollisionShape(
            shapeType=p.GEOM_CYLINDER,
            radius=0.1,
            height=0.2
        )
        self.base_id = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=base_collision,
            baseVisualShapeIndex=base_visual,
            basePosition=[0, 0, 0.1]
        )
        
        # Criar juntas e elos
        self.link_ids = []
        self.joint_pivot_positions = []  # Posições dos pivôs das juntas
        
        prev_body = self.base_id
        prev_pos = [0, 0, 0.1]
        cumulative_angle = 0.0
        
        for i in range(self.num_joints):
            cumulative_angle += self.target_angles[i]
            
            # Criar elo
            link_visual = p.createVisualShape(
                shapeType=p.GEOM_BOX,
                halfExtents=[link_length/2, link_radius, link_radius],
                rgbaColor=[0.2, 0.6, 0.8, 1]
            )
            link_collision = p.createCollisionShape(
                shapeType=p.GEOM_BOX,
                halfExtents=[link_length/2, link_radius, link_radius]
            )
            
            # Posição do elo (centro do elo)
            if i == 0:
                # Primeiro elo conectado à base
                link_pos = [
                    prev_pos[0] + (link_length/2) * math.cos(cumulative_angle),
                    prev_pos[1] + (link_length/2) * math.sin(cumulative_angle),
                    prev_pos[2]
                ]
                pivot_pos = prev_pos
            else:
                # Elos subsequentes
                prev_link_pos, _ = p.getBasePositionAndOrientation(self.link_ids[i-1])
                pivot_pos = [
                    prev_link_pos[0] + link_length * math.cos(sum(self.target_angles[:i])),
                    prev_link_pos[1] + link_length * math.sin(sum(self.target_angles[:i])),
                    prev_link_pos[2]
                ]
                link_pos = [
                    pivot_pos[0] + (link_length/2) * math.cos(cumulative_angle),
                    pivot_pos[1] + (link_length/2) * math.sin(cumulative_angle),
                    pivot_pos[2]
                ]
            
            link_id = p.createMultiBody(
                baseMass=link_mass,
                baseCollisionShapeIndex=link_collision,
                baseVisualShapeIndex=link_visual,
                basePosition=link_pos,
                baseOrientation=p.getQuaternionFromEuler([0, 0, cumulative_angle])
            )
            
            # Garantir que link_id é um inteiro
            if not isinstance(link_id, int):
                link_id = int(link_id)
            
            # Conectar elo ao corpo anterior usando constraint de ponto
            # Isso permite rotação livre em torno do eixo Z
            constraint_id = p.createConstraint(
                prev_body,
                -1,
                link_id,
                -1,
                jointType=p.JOINT_POINT2POINT,
                jointAxis=[0, 0, 0],
                parentFramePosition=[0, 0, 0],
                childFramePosition=[0, 0, 0]
            )
            
            # Configurar constraint para permitir rotação
            p.changeConstraint(constraint_id, maxForce=100, erp=1.0)
            
            self.link_ids.append(link_id)
            self.joint_pivot_positions.append(pivot_pos)
            
            prev_body = link_id
            prev_pos = link_pos
        
        # Criar efetuador (pode adicionar peso)
        efetuador_visual = p.createVisualShape(
            shapeType=p.GEOM_SPHERE,
            radius=0.05,
            rgbaColor=[1.0, 0.0, 0.0, 1]
        )
        efetuador_collision = p.createCollisionShape(
            shapeType=p.GEOM_SPHERE,
            radius=0.05
        )
        
        # Posição do efetuador no final do último elo
        last_link_pos, _ = p.getBasePositionAndOrientation(self.link_ids[-1])
        total_angle = sum(self.target_angles)
        efetuador_pos = [
            last_link_pos[0] + link_length/2 * math.cos(total_angle),
            last_link_pos[1] + link_length/2 * math.sin(total_angle),
            last_link_pos[2]
        ]
        
        self.efetuador_id = p.createMultiBody(
            baseMass=0.5,  # Peso do efetuador (pode variar para testar perturbações)
            baseCollisionShapeIndex=efetuador_collision,
            baseVisualShapeIndex=efetuador_visual,
            basePosition=efetuador_pos
        )
        
        # Conectar efetuador ao último elo
        p.createConstraint(
            self.link_ids[-1],
            -1,
            self.efetuador_id,
            -1,
            jointType=p.JOINT_FIXED,
            jointAxis=[0, 0, 0],
            parentFramePosition=[link_length/2, 0, 0],
            childFramePosition=[0, 0, 0]
        )
    
    def get_joint_angles(self) -> List[float]:
        """Obtém os ângulos atuais das juntas (encoder virtual)"""
        angles = []
        
        for i, link_id in enumerate(self.link_ids):
            # Obter orientação do elo
            _, orn = p.getBasePositionAndOrientation(link_id)
            euler = p.getEulerFromQuaternion(orn)
            # Ângulo no plano XY (rotação em Z)
            angle = euler[2]
            
            if i > 0:
                # Ângulo relativo ao elo anterior
                _, prev_orn = p.getBasePositionAndOrientation(self.link_ids[i-1])
                prev_euler = p.getEulerFromQuaternion(prev_orn)
                angle = angle - prev_euler[2]
            
            angles.append(angle)
        
        return angles
    
    def set_target_angles(self, angles: List[float]):
        """Define os ângulos de referência"""
        self.target_angles = angles[:self.num_joints]
        self.metrics['estabilizado'] = False
        self.metrics['tempo_inicio'] = time.time()
        # Resetar contador de estabilização
        if hasattr(self, '_estabilizacao_inicio'):
            delattr(self, '_estabilizacao_inicio')
        # Resetar controladores
        for controller in self.controllers:
            controller.reset()
    
    def step(self, dt: float = 1.0/240.0):
        """Executa um passo de simulação"""
        # Obter ângulos atuais
        current_angles = self.get_joint_angles()
        
        # Calcular erros e aplicar controle PID
        total_energy = 0.0
        max_overshoot = 0.0
        
        for i, (current, target, controller) in enumerate(zip(current_angles, self.target_angles, self.controllers)):
            # Erro angular
            error = target - current
            # Normalizar erro para [-pi, pi]
            error = math.atan2(math.sin(error), math.cos(error))
            
            # Calcular torque via PID
            torque = controller.compute(error, dt)
            
            # Aplicar torque diretamente no elo
            if i < len(self.link_ids):
                link_id = self.link_ids[i]
                # Garantir que link_id é um inteiro
                if not isinstance(link_id, int):
                    if isinstance(link_id, (list, tuple)) and len(link_id) > 0:
                        link_id = int(link_id[0])
                    else:
                        continue
                # Aplicar torque no eixo Z (rotação no plano XY)
                # applyExternalTorque(objectUniqueId, linkIndex, torque, flags)
                # linkIndex = -1 para o link base
                p.applyExternalTorque(link_id, -1, [0, 0, float(torque)], flags=p.WORLD_FRAME)
            
            # Calcular energia (aproximação: torque^2 * dt para melhor representação)
            total_energy += (torque ** 2) * dt
            
            # Calcular overshoot
            if abs(error) > max_overshoot:
                max_overshoot = abs(error)
            
            # Atualizar métricas
            self.metrics['erro_medio'].append(abs(error))
        
        # Atualizar energia total
        self.metrics['energia_total'] += total_energy
        
        # Verificar estabilização (com verificação de estabilidade contínua)
        if not self.metrics['estabilizado']:
            erro_atual = np.mean([abs(a - t) for a, t in zip(current_angles, self.target_angles)])
            # Tolerância de 0.05 rad (mais realista)
            # Verificar se está estável por pelo menos 0.5 segundos
            if erro_atual < 0.05:
                if not hasattr(self, '_estabilizacao_inicio'):
                    self._estabilizacao_inicio = time.time()
                elif time.time() - self._estabilizacao_inicio > 0.5:
                    if self.metrics['tempo_inicio']:
                        self.metrics['tempo_estabilizacao'] = time.time() - self.metrics['tempo_inicio']
                    self.metrics['estabilizado'] = True
            else:
                # Resetar contador se sair da tolerância
                if hasattr(self, '_estabilizacao_inicio'):
                    delattr(self, '_estabilizacao_inicio')
        
        # Atualizar overshoot máximo
        if max_overshoot > self.metrics['overshoot_maximo']:
            self.metrics['overshoot_maximo'] = max_overshoot
        
        # Passo de simulação
        p.stepSimulation()
        
        return current_angles
    
    def get_metrics(self) -> dict:
        """Retorna as métricas atuais"""
        erro_medio = np.mean(self.metrics['erro_medio']) if self.metrics['erro_medio'] else 0.0
        
        return {
            'erro_medio_posicao': erro_medio,
            'tempo_estabilizacao': self.metrics['tempo_estabilizacao'] or 0.0,
            'energia_total_gasta': self.metrics['energia_total'],
            'overshoot_maximo': self.metrics['overshoot_maximo'],
            'estabilizado': self.metrics['estabilizado']
        }
    
    def send_metrics_to_node_red(self):
        """Envia métricas para o Node-RED"""
        metrics = self.get_metrics()
        self.node_red.send_metrics('manipulador_planar', metrics)
    
    def run_simulation(self, duration: float = 10.0, target_angles: List[float] = None):
        """Executa a simulação"""
        if target_angles:
            self.set_target_angles(target_angles)
        
        start_time = time.time()
        step_count = 0
        
        while time.time() - start_time < duration:
            current_time = time.time() - start_time
            dt = 1.0/240.0
            
            # Executar passo
            angles = self.step(dt)
            
            # Enviar métricas a cada segundo
            if step_count % 240 == 0:
                self.send_metrics_to_node_red()
                print(f"Tempo: {current_time:.2f}s | Ângulos: {[f'{a:.3f}' for a in angles]} | "
                      f"Target: {[f'{t:.3f}' for t in self.target_angles]}")
            
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
    print("=== Manipulador Planar 2/3 DOF com Controle PID ===\n")
    
    # Criar manipulador com 2 juntas
    manipulator = ManipuladorPlanar(num_joints=2, use_gui=True)
    
    # Definir ângulos de referência (em radianos)
    target_angles = [math.pi/4, math.pi/6]  # 45° e 30°
    
    print(f"Ângulos de referência: {[math.degrees(a) for a in target_angles]}°")
    print("Iniciando simulação...\n")
    
    try:
        # Executar simulação por 10 segundos
        manipulator.run_simulation(duration=10.0, target_angles=target_angles)
        
        # Aguardar um pouco antes de mudar o target
        time.sleep(2)
        
        # Mudar para novos ângulos (teste de perturbação)
        print("\n=== Mudando ângulos de referência ===")
        new_targets = [math.pi/2, -math.pi/4]  # 90° e -45°
        manipulator.set_target_angles(new_targets)
        manipulator.run_simulation(duration=10.0)
        
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário")
    finally:
        manipulator.cleanup()


if __name__ == "__main__":
    main()
