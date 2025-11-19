"""
Robô Aspirador - Classe principal do robô diferencial
"""
import pybullet as p
import numpy as np
import math


class VacuumRobot:
    """Robô aspirador com base diferencial e sensores ultrassônicos"""
    
    def __init__(self, physics_client, start_pos=[0, 0, 0.1], start_orientation=[0, 0, 0]):
        """
        Inicializa o robô aspirador
        
        Args:
            physics_client: Cliente PyBullet
            start_pos: Posição inicial [x, y, z]
            start_orientation: Orientação inicial [roll, pitch, yaw] em radianos
        """
        self.p = physics_client
        self.start_pos = start_pos
        self.start_orientation = start_orientation
        
        # Parâmetros físicos do robô
        self.wheel_radius = 0.05  # raio da roda em metros
        self.wheel_base = 0.2  # distância entre rodas em metros
        self.max_velocity = 2.0  # velocidade máxima m/s
        self.max_angular_velocity = 3.0  # velocidade angular máxima rad/s
        
        # Estado atual
        self.position = np.array(start_pos[:2])  # [x, y]
        self.orientation = start_orientation[2]  # yaw
        self.velocity = [0.0, 0.0]  # [linear, angular]
        self.energy_consumed = 0.0  # energia total consumida
        
        # IDs das rodas (serão definidos ao carregar o URDF)
        self.left_wheel_id = None
        self.right_wheel_id = None
        self.robot_id = None
        
        # Carrega o modelo do robô
        self._load_robot()
    
    def _load_robot(self):
        """Carrega o modelo URDF do robô ou cria um modelo simples"""
        import os
        # Verifica se existe URDF antes de tentar carregar (evita aviso)
        if os.path.exists("robot.urdf"):
            try:
                start_quat = p.getQuaternionFromEuler(self.start_orientation)
                self.robot_id = p.loadURDF("robot.urdf", self.start_pos, start_quat)
                return
            except:
                pass  # Se falhar, cria modelo simples
        
        # Se não houver URDF, cria um modelo simples usando primitivas
        self._create_simple_robot()
    
    def _create_simple_robot(self):
        """Cria um robô simples usando primitivas do PyBullet"""
        # Corpo principal (caixa) - representa o robô completo
        # Para simulação simplificada, não precisamos de rodas físicas separadas
        base_mass = 1.0
        base_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.15, 0.12, 0.05])
        base_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.15, 0.12, 0.05], 
                                         rgbaColor=[0.2, 0.2, 0.8, 1.0])
        
        # Cria o corpo principal
        start_quat = p.getQuaternionFromEuler(self.start_orientation)
        self.robot_id = p.createMultiBody(
            baseMass=base_mass,
            baseCollisionShapeIndex=base_shape,
            baseVisualShapeIndex=base_visual,
            basePosition=self.start_pos,
            baseOrientation=start_quat
        )
        
        # Para simulação simplificada, aplicamos forças diretamente ao corpo
        # As "rodas" são virtuais - o controle de velocidade é aplicado via forças
        self.left_wheel_id = None
        self.right_wheel_id = None
    
    def set_velocity(self, linear, angular):
        """
        Define a velocidade do robô
        
        Args:
            linear: Velocidade linear (m/s)
            angular: Velocidade angular (rad/s)
        """
        # Atualiza orientação atual antes de usar
        pos, _, yaw = self.get_pose()
        
        # Limita as velocidades
        linear = np.clip(linear, -self.max_velocity, self.max_velocity)
        angular = np.clip(angular, -self.max_angular_velocity, self.max_angular_velocity)
        
        # Obtém velocidade atual
        current_linear, current_angular = p.getBaseVelocity(self.robot_id)
        current_vel_x = current_linear[0]
        current_vel_y = current_linear[1]
        current_angular_z = current_angular[2]
        
        # Calcula velocidade desejada no frame do mundo
        target_vel_x = linear * math.cos(yaw)
        target_vel_y = linear * math.sin(yaw)
        target_angular_z = angular
        
        # Calcula erro de velocidade (controle proporcional)
        error_x = target_vel_x - current_vel_x
        error_y = target_vel_y - current_vel_y
        error_angular = target_angular_z - current_angular_z
        
        # Ganhos do controlador
        kp_linear = 50.0
        kp_angular = 30.0
        
        # Calcula forças necessárias
        force_x = error_x * kp_linear
        force_y = error_y * kp_linear
        torque_z = error_angular * kp_angular
        
        # Limita forças máximas
        max_force = 100.0
        max_torque = 50.0
        force_x = np.clip(force_x, -max_force, max_force)
        force_y = np.clip(force_y, -max_force, max_force)
        torque_z = np.clip(torque_z, -max_torque, max_torque)
        
        # Aplica forças no centro de massa
        p.applyExternalForce(
            self.robot_id,
            -1,  # linkIndex: -1 significa base do corpo
            forceObj=[force_x, force_y, 0],
            posObj=[0, 0, 0],
            flags=p.WORLD_FRAME
        )
        
        p.applyExternalTorque(
            self.robot_id,
            -1,  # linkIndex: -1 significa base do corpo
            torqueObj=[0, 0, torque_z],
            flags=p.WORLD_FRAME
        )
        
        self.velocity = [linear, angular]
    
    def get_pose(self):
        """
        Retorna a pose atual do robô
        
        Returns:
            tuple: (x, y, yaw) - posição e orientação
        """
        pos, quat = p.getBasePositionAndOrientation(self.robot_id)
        euler = p.getEulerFromQuaternion(quat)
        
        self.position = np.array([pos[0], pos[1]])
        self.orientation = euler[2]  # yaw
        
        return (pos[0], pos[1], euler[2])
    
    def get_velocity(self):
        """Retorna a velocidade atual"""
        linear, angular = p.getBaseVelocity(self.robot_id)
        linear_speed = math.sqrt(linear[0]**2 + linear[1]**2)
        return linear_speed, self.velocity[1]
    
    def update_energy(self, dt):
        """
        Atualiza o consumo de energia baseado no torque aplicado
        
        Args:
            dt: Intervalo de tempo decorrido
        """
        # Estimativa simples: energia proporcional à velocidade e tempo
        linear, angular = self.velocity
        power = abs(linear) * 10 + abs(angular) * 5  # watts (estimativa)
        self.energy_consumed += power * dt
    
    def reset(self, pos=None, orientation=None):
        """Reseta o robô para a posição inicial"""
        if pos is None:
            pos = self.start_pos
        if orientation is None:
            orientation = self.start_orientation
        
        quat = p.getQuaternionFromEuler(orientation)
        p.resetBasePositionAndOrientation(self.robot_id, pos, quat)
        self.position = np.array(pos[:2])
        self.orientation = orientation[2]
        self.velocity = [0.0, 0.0]
        self.energy_consumed = 0.0

