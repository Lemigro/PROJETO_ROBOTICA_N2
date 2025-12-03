"""
Controlador PID para estabilização do drone.
"""
import numpy as np
from typing import List, Tuple


class PIDController:
    """Controlador PID para controle de posição e atitude."""
    
    def __init__(self, kp: List[float], ki: List[float], kd: List[float]):
        """
        Inicializa o controlador PID.
        
        Args:
            kp: Ganhos proporcionais [x, y, z] ou [roll, pitch, yaw]
            ki: Ganhos integrais
            kd: Ganhos derivativos
        """
        self.kp = np.array(kp)
        self.ki = np.array(ki)
        self.kd = np.array(kd)
        
        self.integral = np.zeros(3)
        self.last_error = np.zeros(3)
        self.last_time = None
        
    def update(self, error: np.ndarray, dt: float) -> np.ndarray:
        """
        Atualiza o controlador e retorna o sinal de controle.
        
        Args:
            error: Erro atual [x, y, z] ou [roll, pitch, yaw]
            dt: Intervalo de tempo desde a última atualização
            
        Returns:
            Sinal de controle calculado
        """
        error = np.array(error)
        
        # Termo proporcional
        p_term = self.kp * error
        
        # Termo integral (com anti-windup)
        self.integral += error * dt
        # Limitação do integral para evitar windup
        self.integral = np.clip(self.integral, -10.0, 10.0)
        i_term = self.ki * self.integral
        
        # Termo derivativo
        if self.last_time is not None and dt > 0:
            derivative = (error - self.last_error) / dt
        else:
            derivative = np.zeros(3)
        d_term = self.kd * derivative
        
        # Sinal de controle total
        control = p_term + i_term + d_term
        
        self.last_error = error
        self.last_time = (self.last_time or 0) + dt
        
        return control
    
    def reset(self):
        """Reseta o estado do controlador."""
        self.integral = np.zeros(3)
        self.last_error = np.zeros(3)
        self.last_time = None


class DroneController:
    """Controlador completo do drone com PID para posição e atitude."""
    
    def __init__(self, config: dict):
        """
        Inicializa o controlador do drone.
        
        Args:
            config: Configurações do controle (PID gains)
        """
        pid_pos = config['pid']['position']
        pid_att = config['pid']['attitude']
        
        self.position_pid = PIDController(
            pid_pos['kp'], pid_pos['ki'], pid_pos['kd']
        )
        self.attitude_pid = PIDController(
            pid_att['kp'], pid_att['ki'], pid_att['kd']
        )
        
        self.max_velocity = config.get('max_velocity', 5.0)
        self.max_acceleration = config.get('max_acceleration', 2.0)
        
        # Multiplicador de velocidade (para reduzir velocidade durante patrulha)
        self.speed_multiplier = 1.0
        
    def compute_control(
        self,
        current_pos: np.ndarray,
        target_pos: np.ndarray,
        current_vel: np.ndarray,
        current_attitude: np.ndarray,
        dt: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula os comandos de controle do drone.
        
        Args:
            current_pos: Posição atual [x, y, z]
            target_pos: Posição alvo [x, y, z]
            current_vel: Velocidade atual [vx, vy, vz]
            current_attitude: Atitude atual [roll, pitch, yaw]
            dt: Intervalo de tempo
            
        Returns:
            Tupla (força_thrust, torque) para aplicar ao drone
        """
        # Erro de posição
        pos_error = target_pos - current_pos
        
        # Controle de posição (gera velocidade desejada)
        desired_velocity = self.position_pid.update(pos_error, dt)
        
        # Aplicar multiplicador de velocidade (para reduzir durante patrulha)
        desired_velocity = desired_velocity * self.speed_multiplier
        
        # Limitação de velocidade (com suavização)
        # Reduzir velocidade desejada para movimento mais suave
        desired_velocity = desired_velocity * 0.5  # Reduzir 50% para suavizar mais
        
        # Limitação de velocidade
        desired_velocity = np.clip(
            desired_velocity,
            -self.max_velocity,
            self.max_velocity
        )
        
        # Erro de velocidade
        vel_error = desired_velocity - current_vel
        
        # Calcular forças horizontais diretamente baseadas no erro de posição e velocidade
        # Usar controle proporcional-derivativo para movimento suave
        kp_pos = 2.0  # Ganho proporcional de posição (reduzido ainda mais)
        kd_vel = 1.5  # Ganho derivativo de velocidade (reduzido)
        
        force_x = pos_error[0] * kp_pos + vel_error[0] * kd_vel
        force_y = pos_error[1] * kp_pos + vel_error[1] * kd_vel
        
        # Limitar forças horizontais (reduzido significativamente)
        max_horizontal_force = 4.0  # Reduzido para movimento muito mais controlado
        force_x = np.clip(force_x, -max_horizontal_force, max_horizontal_force)
        force_y = np.clip(force_y, -max_horizontal_force, max_horizontal_force)
        
        # CORREÇÃO: Controle de atitude melhorado - sempre tenta manter drone plano
        # Quando não há movimento significativo, força roll e pitch a zero
        if np.linalg.norm(desired_velocity[:2]) > 0.2:
            # Há movimento: permite inclinação leve para direção do movimento
            direction = desired_velocity[:2] / np.linalg.norm(desired_velocity[:2])
            desired_roll = -direction[1] * 0.15  # CORREÇÃO: Inclinação reduzida (0.15 ao invés de 0.3)
            desired_pitch = direction[0] * 0.15   # CORREÇÃO: Inclinação reduzida
        else:
            # Sem movimento: força roll e pitch a zero para manter plano
            desired_roll = 0.0
            desired_pitch = 0.0
        
        # CORREÇÃO: Yaw FIXO - não rotaciona, mantém orientação inicial
        # O drone não precisa rotacionar para se mover, pode usar forças horizontais
        desired_yaw = current_attitude[2]  # SEMPRE mantém yaw atual (não muda)
        
        # Atitude desejada
        desired_attitude = np.array([desired_roll, desired_pitch, desired_yaw])
        att_error = desired_attitude - current_attitude
        
        # CORREÇÃO: Normaliza erro de yaw
        while att_error[2] > np.pi:
            att_error[2] -= 2 * np.pi
        while att_error[2] < -np.pi:
            att_error[2] += 2 * np.pi
        
        # Controle de atitude
        torque = self.attitude_pid.update(att_error, dt)
        
        # CORREÇÃO: Zera torque de yaw para evitar rotação no próprio eixo
        # O torque de yaw será corrigido no apply_control com amortecimento
        torque[2] = 0.0  # SEMPRE zera torque de yaw do PID (não rotaciona)
        
        # CORREÇÃO: Limita torque para evitar rotações descontroladas
        max_torque = 15.0  # Limite de torque
        torque = np.clip(torque, -max_torque, max_torque)
        
        # Força vertical (thrust) baseado na altitude desejada
        # Controle simples e direto
        mass = 1.0  # Massa do drone
        gravity = 9.81  # Gravidade (m/s²)
        
        # Força base para compensar gravidade (sempre aplicar)
        base_thrust = mass * gravity  # ~9.81 N para hover
        
        # Ganhos mais conservadores para estabilidade e movimento suave
        kp_alt = 12.0  # Ganho proporcional de altitude (reduzido)
        kd_vel_z = 8.0  # Ganho derivativo de velocidade vertical (reduzido)
        
        altitude_error = pos_error[2]
        vel_z_error = vel_error[2]
        
        # Thrust: base (hover) + correção proporcional + amortecimento
        # A base já compensa a gravidade, então adicionamos correções
        thrust_correction = altitude_error * kp_alt + vel_z_error * kd_vel_z
        thrust = base_thrust + thrust_correction
        
        # Limitar thrust (garantir mínimo para não cair)
        min_thrust = mass * gravity * 0.8  # Mínimo: 80% da gravidade (não pode cair)
        max_thrust = mass * gravity * 4.0   # Máximo: 4x a gravidade
        thrust = np.clip(thrust, min_thrust, max_thrust)
        
        # Força total: horizontal (X, Y) + vertical (Z)
        force = np.array([force_x, force_y, thrust])
        
        return force, torque
    
    def set_speed_multiplier(self, multiplier: float):
        """
        Define multiplicador de velocidade (útil para reduzir velocidade durante patrulha).
        
        Args:
            multiplier: Multiplicador (0.0 a 1.0). 1.0 = velocidade normal, 0.5 = metade da velocidade
        """
        self.speed_multiplier = np.clip(multiplier, 0.1, 1.0)  # Limitar entre 10% e 100%
    
    def reset(self):
        """Reseta os controladores."""
        self.position_pid.reset()
        self.attitude_pid.reset()
        self.speed_multiplier = 1.0

