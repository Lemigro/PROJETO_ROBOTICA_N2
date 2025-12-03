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
        self.max_torque = 15.0  # Limite de torque
        
    def compute(self, error: float, dt: float) -> float:
        """Calcula o torque baseado no erro"""
        # Termo proporcional
        p_term = self.kp * error
        
        # Termo integral
        self.integral += error * dt
        # Limitar integral para evitar windup
        self.integral = np.clip(self.integral, -2.0, 2.0)
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
            # Configurar câmera para melhor visualização
            p.resetDebugVisualizerCamera(
                cameraDistance=2.5,
                cameraYaw=45,
                cameraPitch=-30,
                cameraTargetPosition=[0, 0, 0.5]
            )
        else:
            self.physics_client = p.connect(p.DIRECT)
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        
        # Criar o plano
        self.plane_id = p.loadURDF("plane.urdf")
        
        # Ângulos de referência
        self.target_angles = [0.0] * self.num_joints
        
        # Criar o manipulador
        self.create_manipulator()
        
        # Controladores PID para cada junta
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
        """Cria o manipulador planar estilo Fanuc usando MultiBody com juntas rotacionais"""
        # Parâmetros do manipulador (estilo Fanuc - mais robusto)
        link_length = 0.5  # Comprimento de cada elo (metros)
        link_mass = 1.5    # Massa de cada elo (kg) - mais pesado
        link_radius = 0.08 # Raio do elo (metros) - mais espesso
        base_height = 0.25  # Altura da base - mais alta
        base_radius = 0.15  # Raio da base - mais larga
        
        # Cores Fanuc: Amarelo (#FFD700) e Cinza escuro (#2C2C2C)
        fanuc_yellow = [1.0, 0.843, 0.0, 1.0]  # Amarelo Fanuc
        fanuc_gray = [0.17, 0.17, 0.17, 1.0]   # Cinza escuro Fanuc
        fanuc_dark = [0.1, 0.1, 0.1, 1.0]      # Preto para juntas
        
        # Listas para armazenar shapes e juntas dos LINKS (não inclui a base)
        link_masses = []
        link_collision_indices = []
        link_visual_indices = []
        link_positions = []
        link_orientations = []
        link_inertias = []
        link_parent_indices = []
        link_joint_types = []
        link_joint_axes = []
        
        # ===== BASE (fixa) - Estilo Fanuc (mais robusta) =====
        base_visual = p.createVisualShape(
            shapeType=p.GEOM_CYLINDER,
            radius=base_radius,
            length=base_height,
            rgbaColor=fanuc_gray  # Base cinza escura
        )
        base_collision = p.createCollisionShape(
            shapeType=p.GEOM_CYLINDER,
            radius=base_radius,
            height=base_height
        )
        
        # ===== ELOS ARTICULADOS - Estilo Fanuc =====
        for i in range(self.num_joints):
            # Criar shape visual e de colisão para o elo (estilo Fanuc)
            # Alternar entre amarelo e cinza (estilo Fanuc)
            link_color = fanuc_yellow if i % 2 == 0 else fanuc_gray
            
            # Usar cilindro para parecer mais industrial (estilo Fanuc)
            link_visual = p.createVisualShape(
                shapeType=p.GEOM_CYLINDER,
                radius=link_radius,
                length=link_length,
                rgbaColor=link_color
            )
            link_collision = p.createCollisionShape(
                shapeType=p.GEOM_CYLINDER,
                radius=link_radius,
                height=link_length
            )
            
            link_visual_indices.append(link_visual)
            link_collision_indices.append(link_collision)
            link_masses.append(link_mass)
            
            # Posição do centro do elo relativa ao parent
            # O elo começa na junta anterior e se estende por link_length
            if i == 0:
                # Primeiro elo: conectado à base
                # Centro do elo está a link_length/2 da base no eixo X
                link_positions.append([link_length/2, 0, base_height])
            else:
                # Elos subsequentes: conectados ao final do elo anterior
                link_positions.append([link_length/2, 0, 0])
            
            # Orientação: cilindro ao longo do eixo X (rotação de 90° em Y)
            link_orientations.append(p.getQuaternionFromEuler([0, math.pi/2, 0]))
            
            # Inércia do elo (cilindro)
            # Para cilindro de raio r e comprimento l, massa m:
            # Ixx = (1/12) * m * (3*r^2 + l^2)
            # Iyy = Izz = (1/2) * m * r^2
            inertia_xx = (1/12) * link_mass * (3 * link_radius**2 + link_length**2)
            inertia_yy = (1/2) * link_mass * link_radius**2
            inertia_zz = (1/2) * link_mass * link_radius**2
            link_inertias.append([inertia_xx, inertia_yy, inertia_zz])
            
            # Parent é o link anterior (ou base para o primeiro)
            if i == 0:
                link_parent_indices.append(-1)  # Primeiro elo conectado à base
            else:
                link_parent_indices.append(i - 1)  # Elos subsequentes conectados ao anterior
            
            # Junta rotacional no eixo Z (rotação no plano XY)
            link_joint_types.append(p.JOINT_REVOLUTE)
            link_joint_axes.append([0, 0, 1])  # Eixo Z para rotação no plano
        
        # ===== EFETUADOR - Estilo Fanuc (gripper) =====
        # Criar um gripper mais robusto (caixa retangular)
        efetuador_visual = p.createVisualShape(
            shapeType=p.GEOM_BOX,
            halfExtents=[0.08, 0.06, 0.04],
            rgbaColor=fanuc_yellow  # Amarelo Fanuc
        )
        efetuador_collision = p.createCollisionShape(
            shapeType=p.GEOM_BOX,
            halfExtents=[0.08, 0.06, 0.04]
        )
        
        link_visual_indices.append(efetuador_visual)
        link_collision_indices.append(efetuador_collision)
        link_masses.append(0.3)  # Massa do efetuador
        link_positions.append([link_length, 0, 0])  # No final do último elo (ponta)
        link_orientations.append([0, 0, 0, 1])
        link_inertias.append([0.001, 0.001, 0.001])
        link_parent_indices.append(self.num_joints - 1)  # Conectado ao último elo (índice do link, 0-based)
        link_joint_types.append(p.JOINT_FIXED)  # Fixo ao último elo
        link_joint_axes.append([0, 0, 0])
        
        # Criar o MultiBody
        # A base é criada como baseMass/baseCollisionShapeIndex
        # Os links são os elos + efetuador
        num_links = len(link_masses)  # Todos os links (elos + efetuador)
        self.robot_id = p.createMultiBody(
            baseMass=0,  # Base fixa (sem massa)
            baseCollisionShapeIndex=base_collision,
            baseVisualShapeIndex=base_visual,
            basePosition=[0, 0, 0],
            baseOrientation=[0, 0, 0, 1],
            linkMasses=link_masses,  # Todos os links
            linkCollisionShapeIndices=link_collision_indices,
            linkVisualShapeIndices=link_visual_indices,
            linkPositions=link_positions,
            linkOrientations=link_orientations,
            linkInertialFramePositions=[[0, 0, 0]] * num_links,
            linkInertialFrameOrientations=[[0, 0, 0, 1]] * num_links,
            linkParentIndices=link_parent_indices,
            linkJointTypes=link_joint_types,
            linkJointAxis=link_joint_axes
        )
        
        # Verificar quantas juntas realmente existem
        num_joints_actual = p.getNumJoints(self.robot_id)
        # Deve ser igual a num_joints (juntas rotacionais) + 1 (junta fixa do efetuador)
        if num_joints_actual != self.num_joints + 1:
            print(f"Aviso: Número de juntas criadas: {num_joints_actual}, esperado: {self.num_joints + 1} (rotacionais + fixa)")
        
        # Configurar juntas para controle de torque
        # Desabilitar controle automático das juntas (vamos controlar manualmente)
        # No PyBullet, as juntas são numeradas a partir de 0
        # Apenas configurar as juntas rotacionais (não a fixa do efetuador)
        for i in range(self.num_joints):
            if i < num_joints_actual:
                p.setJointMotorControl2(
                    self.robot_id,
                    i,  # Juntas começam no índice 0
                    controlMode=p.VELOCITY_CONTROL,
                    targetVelocity=0,
                    force=0
                )
                # Permitir movimento livre
                p.changeDynamics(
                    self.robot_id,
                    i,
                    jointLowerLimit=-3.14,
                    jointUpperLimit=3.14,
                    jointDamping=0.15  # Amortecimento um pouco maior (estilo industrial)
                )
        
        # Desabilitar colisão entre links do mesmo robô
        # Base é -1, links são 0, 1, 2, ...
        num_total_bodies = self.num_joints + 1  # Elos + efetuador (base não conta)
        for i in range(-1, num_total_bodies):  # -1 é a base
            for j in range(i + 1, num_total_bodies):
                if i == -1:
                    # Base com links
                    p.setCollisionFilterPair(self.robot_id, self.robot_id, -1, j, 0)
                else:
                    # Links entre si
                    p.setCollisionFilterPair(self.robot_id, self.robot_id, i, j, 0)
        
        # Armazenar índices das juntas (0, 1, 2, ...)
        # Apenas as juntas rotacionais (excluindo a fixa do efetuador)
        self.joint_indices = list(range(min(self.num_joints, num_joints_actual)))
    
    def get_joint_angles(self) -> List[float]:
        """Obtém os ângulos atuais das juntas"""
        angles = []
        for joint_idx in self.joint_indices:
            joint_state = p.getJointState(self.robot_id, joint_idx)
            angles.append(joint_state[0])  # Posição da junta (ângulo)
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
            
            # Aplicar torque na junta usando TORQUE_CONTROL
            p.setJointMotorControl2(
                self.robot_id,
                self.joint_indices[i],
                controlMode=p.TORQUE_CONTROL,
                force=torque
            )
            
            # Calcular energia (aproximação: torque^2 * dt)
            total_energy += (torque ** 2) * dt
            
            # Calcular overshoot
            if abs(error) > max_overshoot:
                max_overshoot = abs(error)
            
            # Atualizar métricas
            self.metrics['erro_medio'].append(abs(error))
        
        # Atualizar energia total
        self.metrics['energia_total'] += total_energy
        
        # Verificar estabilização
        if not self.metrics['estabilizado']:
            erro_atual = np.mean([abs(a - t) for a, t in zip(current_angles, self.target_angles)])
            # Tolerância de 0.05 rad
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
        
        # Converter valores numpy para float nativo
        return {
            'erro_medio_posicao': float(erro_medio),
            'tempo_estabilizacao': float(self.metrics['tempo_estabilizacao'] or 0.0),
            'energia_total_gasta': float(self.metrics['energia_total']),
            'overshoot_maximo': float(self.metrics['overshoot_maximo']),
            'estabilizado': bool(self.metrics['estabilizado'])
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
            
            # Enviar métricas a cada segundo (apenas uma vez por segundo)
            if step_count % 240 == 0:
                self.send_metrics_to_node_red()
                # Exibir informações no console
                erro_medio = np.mean(self.metrics['erro_medio']) if self.metrics['erro_medio'] else 0.0
                print(f"Tempo: {current_time:.2f}s | Ângulos: {[f'{a:.3f}' for a in angles]} | "
                      f"Target: {[f'{t:.3f}' for t in self.target_angles]} | "
                      f"Erro médio: {erro_medio:.4f} rad")
            
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
