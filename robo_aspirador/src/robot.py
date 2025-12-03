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
        self.max_velocity = 10.0  # velocidade máxima m/s
        self.max_angular_velocity = 12.0  # velocidade angular máxima rad/s (aumentado de 10.0)
        
        # Estado atual
        self.position = np.array(start_pos[:2])  # [x, y]
        self.orientation = start_orientation[2]  # yaw
        self.velocity = [0.0, 0.0]  # [linear, angular]
        self.energy_consumed = 0.0  # energia total consumida
        self.last_vel_x = 0.0  # Para cálculo de derivada
        self.last_vel_y = 0.0
        self.last_angular_z = 0.0
        
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
        base_mass = 2.0  # Aumentado de 1.0 para mais estabilidade
        # Altura do robô: 0.05m (halfExtents Z = 0.05, então altura total = 0.10m)
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
        
        # Configura propriedades físicas para estabilidade
        # Reduz atrito para movimento mais suave
        p.changeDynamics(self.robot_id, -1, 
                       lateralFriction=0.3,  # Atrito lateral reduzido
                       spinningFriction=0.1,  # Atrito de rotação reduzido
                       rollingFriction=0.1,   # Atrito de rolamento reduzido
                       linearDamping=0.1,     # Amortecimento linear (ajuda estabilidade)
                       angularDamping=0.2,   # Amortecimento angular (ajuda estabilidade)
                       localInertiaDiagonal=[1, 1, 0.1])  # Inércia reduzida em Z para manter plano
        
        # Força orientação inicial correta (plano)
        p.resetBasePositionAndOrientation(
            self.robot_id,
            self.start_pos,
            p.getQuaternionFromEuler([0, 0, self.start_orientation[2]])  # Força roll=0, pitch=0
        )
        
        # Para simulação simplificada, aplicamos forças diretamente ao corpo
        # As "rodas" são virtuais - o controle de velocidade é aplicado via forças
        self.left_wheel_id = None
        self.right_wheel_id = None
    
    def set_velocity(self, linear, angular, collision=False, min_distance=None):
        """
        Define a velocidade do robô
        
        Args:
            linear: Velocidade linear (m/s)
            angular: Velocidade angular (rad/s)
        """
        # Atualiza orientação atual antes de usar
        _, _, yaw = self.get_pose()
        
        # Limita as velocidades
        linear_original = linear
        angular_original = angular
        linear = np.clip(linear, -self.max_velocity, self.max_velocity)
        angular = np.clip(angular, -self.max_angular_velocity, self.max_angular_velocity)
        
        # Debug: avisa se velocidade foi limitada
        if abs(linear_original) > self.max_velocity or abs(angular_original) > self.max_angular_velocity:
            print(f"[WARNING] Velocidade limitada! Linear: {linear_original:.2f} -> {linear:.2f}, Angular: {angular_original:.2f} -> {angular:.2f}")
        
        # Obtém velocidade atual
        current_linear, current_angular = p.getBaseVelocity(self.robot_id)
        current_vel_x = current_linear[0]
        current_vel_y = current_linear[1]
        current_angular_z = current_angular[2]
        
        # Calcula velocidade desejada no frame do mundo
        target_vel_x = linear * math.cos(yaw)
        target_vel_y = linear * math.sin(yaw)
        target_angular_z = angular
        
        # Calcula erro de velocidade (controle proporcional-derivativo)
        error_x = target_vel_x - current_vel_x
        error_y = target_vel_y - current_vel_y
        error_angular = target_angular_z - current_angular_z
        
        # Ganhos do controlador (ajustados para movimento muito mais fluido)
        # Similar ao robô móvel para consistência
        kp_linear = 150.0  # Mantido para movimento rápido
        kd_linear = 25.0   # Aumentado ainda mais para movimento mais suave
        kp_angular = 100.0  # Mantido
        kd_angular = 18.0   # Aumentado ainda mais para rotação mais suave
        
        # Obtém orientação atual e corrige se necessário (mantém robô plano)
        _, quat = p.getBasePositionAndOrientation(self.robot_id)
        euler = p.getEulerFromQuaternion(quat)
        roll, pitch, _ = euler
        
        # Força correção de orientação para manter plano (roll e pitch = 0)
        # Aumenta ganho quando há colisão ou muito próximo de obstáculos
        # Detecta se está em canto (muito próximo de múltiplos obstáculos)
        is_corner = min_distance is not None and min_distance < 0.15
        
        # Sempre aplica correção forte de orientação para manter plano
        if collision:
            kp_orientation = 300.0  # Muito alto quando colide (aumentado de 200.0)
        elif is_corner:
            kp_orientation = 200.0  # Alto quando em canto (aumentado de 150.0)
        elif min_distance is not None and min_distance < 0.3:
            kp_orientation = 150.0  # Médio quando próximo (aumentado de 100.0)
        else:
            kp_orientation = 100.0  # Normal (aumentado de 50.0 - sempre forte)
        
        torque_roll = -roll * kp_orientation
        torque_pitch = -pitch * kp_orientation
        
        # Sempre aplica correção adicional baseada no ângulo de inclinação
        # Quanto mais inclinado, mais forte a correção
        if abs(roll) > 0.05 or abs(pitch) > 0.05:  # Se está inclinado (reduzido threshold)
            # Correção proporcional à inclinação
            torque_roll *= (1.0 + abs(roll) * 10.0)  # Multiplica baseado no ângulo
            torque_pitch *= (1.0 + abs(pitch) * 10.0)
        
        # Se há colisão ou está em canto, força orientação para baixo (evita subir)
        if collision or is_corner:
            # Força adicional para manter plano quando colide ou em canto
            torque_roll *= 4.0  # Aumentado de 3.0 para 4.0
            torque_pitch *= 4.0  # Aumentado de 3.0 para 4.0
            
            # Força adicional baseada no ângulo de inclinação
            if abs(roll) > 0.05 or abs(pitch) > 0.05:  # Se está inclinado (reduzido threshold)
                torque_roll *= 3.0  # Triplica a correção (aumentado de 2.0)
                torque_pitch *= 3.0
        
        # Calcula forças necessárias (PD control)
        # Termo proporcional
        force_x = error_x * kp_linear
        force_y = error_y * kp_linear
        torque_z = error_angular * kp_angular
        
        # Termo derivativo (amortecimento) - usa velocidade atual como aproximação
        # Reduz oscilações aplicando força oposta à velocidade atual
        force_x -= current_vel_x * kd_linear
        force_y -= current_vel_y * kd_linear
        torque_z -= current_angular_z * kd_angular
        
        # Atualiza velocidades anteriores para próximo passo
        self.last_vel_x = current_vel_x
        self.last_vel_y = current_vel_y
        self.last_angular_z = current_angular_z
        
        # Limita forças máximas (aumentadas para permitir movimento extremamente rápido)
        max_force = 500.0  # Aumentado de 300.0 para movimento extremamente rápido
        max_torque = 250.0  # Aumentado de 150.0
        max_torque_orientation = 1000.0  # Torque máximo para correção de orientação (aumentado de 500.0)
        force_x = np.clip(force_x, -max_force, max_force)
        force_y = np.clip(force_y, -max_force, max_force)
        torque_z = np.clip(torque_z, -max_torque, max_torque)
        torque_roll = np.clip(torque_roll, -max_torque_orientation, max_torque_orientation)
        torque_pitch = np.clip(torque_pitch, -max_torque_orientation, max_torque_orientation)
        
        # Aplica forças no centro de massa
        p.applyExternalForce(
            self.robot_id,
            -1,  # linkIndex: -1 significa base do corpo
            forceObj=[force_x, force_y, 0],
            posObj=[0, 0, 0],
            flags=p.WORLD_FRAME
        )
        
        # Aplica torques: Z para rotação horizontal, X e Y para manter plano
        p.applyExternalTorque(
            self.robot_id,
            -1,  # linkIndex: -1 significa base do corpo
            torqueObj=[torque_roll, torque_pitch, torque_z],
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
    
    def draw_robot_vision(self, look_length=1.5):
        """
        Desenha uma linha visual simples (olhos) mostrando a direção do robô
        Versão simplificada e mais clara
        
        Args:
            look_length: Comprimento da linha visual em metros (reduzido para menos confusão)
        """
        pos, quat = p.getBasePositionAndOrientation(self.robot_id)
        euler = p.getEulerFromQuaternion(quat)
        yaw = euler[2]
        
        # Ponto inicial (centro do robô, mais alto para ficar visível)
        start_point = [pos[0], pos[1], pos[2] + 0.08]
        
        # Direção do robô (frente) - linha mais curta e simples
        end_point = [
            pos[0] + look_length * math.cos(yaw),
            pos[1] + look_length * math.sin(yaw),
            pos[2] + 0.08
        ]
        
        # Desenha linha verde (mais visível que amarelo) - sem raycast para simplicidade
        p.addUserDebugLine(
            start_point,
            end_point,
            lineColorRGB=[0.0, 1.0, 0.0],  # Verde (mais visível)
            lineWidth=5,  # Mais grossa para melhor visibilidade
            lifeTime=0.05  # Atualiza mais rápido
        )
    
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

