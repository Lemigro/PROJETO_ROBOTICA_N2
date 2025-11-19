"""
Simulador PyBullet para o drone de entregas.
"""
import pybullet as p
import pybullet_data
import numpy as np
from typing import List, Optional, Tuple
import os

from src.sensor import DeliveryPoint


class DroneSimulator:
    """Simulador PyBullet do drone e ambiente."""
    
    def __init__(self, config: dict):
        """
        Inicializa o simulador.
        
        Args:
            config: Configurações da simulação
        """
        self.config = config
        # Garantir que timestep seja um número
        timestep_value = config['simulation']['timestep']
        if isinstance(timestep_value, str):
            # Tentar avaliar expressão como "1/240"
            try:
                self.timestep = eval(timestep_value)
            except:
                self.timestep = float(timestep_value)
        else:
            self.timestep = float(timestep_value)
        self.base_position = np.array(config['simulation']['base_position'])
        # Garantir que o drone comece em uma altitude segura
        if self.base_position[2] < 1.0:
            self.base_position[2] = 1.0
        
        # Inicializar PyBullet
        self.client_id = p.connect(p.GUI)  # ou p.DIRECT para headless
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, config['simulation']['gravity'])
        p.setTimeStep(self.timestep)
        
        # Carregar plano
        plane_id = p.loadURDF("plane.urdf")
        
        # Criar drone (usando modelo simplificado ou racecar/husky)
        self.drone_model = config['drone'].get('model', 'quadrotor')
        self.drone_id = self._create_drone()
        
        # Estado do drone
        self.position = self.base_position.copy()
        self.velocity = np.zeros(3)
        self.orientation = np.array([0, 0, 0, 1])  # quaternion
        self.angular_velocity = np.zeros(3)
        
        # Pontos de entrega
        self.delivery_points: List[DeliveryPoint] = []
        self._create_delivery_points()
        
        # Visualização
        self.target_marker = None
        self.route_lines = []
        
    def _create_drone(self):
        """Cria o modelo do drone no PyBullet."""
        if self.drone_model == "racecar":
            # Usar racecar como substituto terrestre
            drone_id = p.loadURDF("racecar/racecar.urdf", 
                                 basePosition=self.base_position.tolist(),
                                 baseOrientation=[0, 0, 0, 1])
        elif self.drone_model == "husky":
            # Usar husky como substituto terrestre
            drone_id = p.loadURDF("husky/husky.urdf",
                                 basePosition=self.base_position.tolist(),
                                 baseOrientation=[0, 0, 0, 1])
        else:
            # Criar drone quadrotor simplificado (caixa com propulsores)
            drone_id = self._create_simple_quadrotor()
        
        return drone_id
    
    def _create_simple_quadrotor(self):
        """Cria um quadrotor simplificado usando caixas."""
        # Corpo principal
        base_visual = p.createVisualShape(
            shapeType=p.GEOM_BOX,
            halfExtents=[0.2, 0.2, 0.05],
            rgbaColor=[0.3, 0.3, 0.8, 1.0]
        )
        base_collision = p.createCollisionShape(
            shapeType=p.GEOM_BOX,
            halfExtents=[0.2, 0.2, 0.05]
        )
        
        drone_id = p.createMultiBody(
            baseMass=self.config['drone'].get('mass', 1.0),
            baseCollisionShapeIndex=base_collision,
            baseVisualShapeIndex=base_visual,
            basePosition=self.base_position.tolist(),
            baseOrientation=[0, 0, 0, 1]
        )
        
        # Configurar propriedades físicas do drone para movimento suave
        # Reduzir damping linear e angular para permitir movimento
        p.changeDynamics(
            drone_id,
            -1,  # linkIndex: -1 para base
            linearDamping=0.0,      # Sem amortecimento linear
            angularDamping=0.0,    # Sem amortecimento angular
            lateralFriction=0.0,   # Sem fricção lateral
            spinningFriction=0.0,  # Sem fricção rotacional
            rollingFriction=0.0,   # Sem fricção de rolamento
            restitution=0.0,       # Sem restituição (sem quique)
            mass=self.config['drone'].get('mass', 1.0)
        )
        
        # Desabilitar colisão com o chão temporariamente para teste
        # p.setCollisionFilterPair(drone_id, plane_id, -1, -1, 0)
        
        return drone_id
    
    def _create_delivery_points(self):
        """Cria pontos de entrega no ambiente."""
        area_size = self.config['environment']['area_size']
        num_points = self.config['environment']['num_delivery_points']
        spacing = self.config['environment'].get('point_spacing', 5.0)
        
        # Gerar pontos distribuídos na área
        points = []
        np.random.seed(42)  # Para reprodutibilidade
        
        for i in range(num_points):
            # Distribuir pontos de forma que não fiquem muito próximos
            attempts = 0
            while attempts < 100:
                x = np.random.uniform(-area_size[0]/2, area_size[0]/2)
                y = np.random.uniform(-area_size[1]/2, area_size[1]/2)
                z = 0.1  # Altura do ponto no chão
                
                pos = np.array([x, y, z])
                
                # Verificar distância mínima dos outros pontos
                too_close = False
                for existing_point in points:
                    if np.linalg.norm(pos - existing_point.position) < spacing:
                        too_close = True
                        break
                
                if not too_close:
                    point = DeliveryPoint(pos, i)
                    points.append(point)
                    
                    # Criar marcador visual no PyBullet
                    marker = p.createVisualShape(
                        shapeType=p.GEOM_CYLINDER,
                        radius=0.3,
                        length=0.1,
                        rgbaColor=[1.0, 0.0, 0.0, 0.8]
                    )
                    marker_id = p.createMultiBody(
                        baseMass=0,
                        baseVisualShapeIndex=marker,
                        basePosition=pos.tolist()
                    )
                    point.marker_id = marker_id
                    break
                
                attempts += 1
        
        self.delivery_points = points
    
    def update_drone_state(self):
        """Atualiza estado do drone a partir da simulação."""
        pos, orn = p.getBasePositionAndOrientation(self.drone_id)
        vel, ang_vel = p.getBaseVelocity(self.drone_id)
        
        self.position = np.array(pos)
        self.velocity = np.array(vel)
        self.orientation = np.array(orn)
        self.angular_velocity = np.array(ang_vel)
    
    def get_euler_angles(self) -> np.ndarray:
        """Retorna ângulos de Euler (roll, pitch, yaw) do drone."""
        euler = p.getEulerFromQuaternion(self.orientation)
        return np.array(euler)
    
    def apply_control(self, force: np.ndarray, torque: np.ndarray, use_velocity_control: bool = False):
        """
        Aplica força e torque ao drone.
        
        Args:
            force: Força linear [fx, fy, fz] ou velocidade desejada se use_velocity_control=True
            torque: Torque angular [tx, ty, tz]
            use_velocity_control: Se True, usa controle direto de velocidade (não recomendado)
        """
        # Garantir que force e torque sejam arrays numpy
        if not isinstance(force, np.ndarray):
            force = np.array(force)
        if not isinstance(torque, np.ndarray):
            torque = np.array(torque)
        
        # SEMPRE usar forças físicas reais (não controle de velocidade)
        # O controle de velocidade não funciona bem com gravidade no PyBullet
        
        # Garantir que as forças sejam aplicadas corretamente
        # Verificar se a força Z é suficiente para compensar gravidade
        mass = self.config['drone'].get('mass', 1.0)
        gravity = abs(self.config['simulation']['gravity'])
        min_required_thrust = mass * gravity * 0.9  # 90% da gravidade como mínimo
        
        # Garantir que a força Z nunca seja menor que o mínimo necessário
        if force[2] < min_required_thrust:
            force[2] = min_required_thrust
        
        force_list = force.tolist()
        torque_list = torque.tolist()
        
        # Aplicar força no centro de massa
        p.applyExternalForce(
            self.drone_id,
            -1,  # linkIndex: -1 para base
            force_list,
            [0, 0, 0],  # posição relativa (centro de massa)
            p.WORLD_FRAME
        )
        
        # Aplicar torque
        p.applyExternalTorque(
            self.drone_id,
            -1,  # linkIndex: -1 para base/root link
            torque_list,
            p.WORLD_FRAME
        )
    
    def set_drone_position(self, position: np.ndarray, orientation: Optional[np.ndarray] = None):
        """
        Define posição do drone (útil para reset).
        
        Args:
            position: Nova posição [x, y, z]
            orientation: Nova orientação (quaternion) ou None
        """
        if orientation is None:
            orientation = [0, 0, 0, 1]
        
        p.resetBasePositionAndOrientation(
            self.drone_id,
            position.tolist(),
            orientation
        )
        self.update_drone_state()
    
    def step_simulation(self):
        """Executa um passo da simulação."""
        p.stepSimulation()
        self.update_drone_state()
    
    def update_point_visualization(self, point: DeliveryPoint, delivered: bool = False):
        """
        Atualiza visualização de um ponto de entrega.
        
        Args:
            point: Ponto de entrega
            delivered: Se foi entregue
        """
        if hasattr(point, 'marker_id'):
            if delivered:
                # Mudar cor para verde quando entregue
                p.changeVisualShape(
                    point.marker_id,
                    -1,
                    rgbaColor=[0.0, 1.0, 0.0, 0.8]
                )
    
    def draw_target_marker(self, target_pos: Optional[np.ndarray]):
        """
        Desenha marcador no alvo atual.
        
        Args:
            target_pos: Posição do alvo ou None
        """
        # Remover marcador anterior
        if self.target_marker is not None:
            p.removeUserDebugItem(self.target_marker)
            self.target_marker = None
        
        if target_pos is not None:
            # Desenhar linha do drone ao alvo
            # Garantir que as posições sejam listas
            pos_from = self.position.tolist() if hasattr(self.position, 'tolist') else list(self.position)
            pos_to = target_pos.tolist() if hasattr(target_pos, 'tolist') else list(target_pos)
            self.target_marker = p.addUserDebugLine(
                pos_from,
                pos_to,
                lineColorRGB=[1.0, 1.0, 0.0],
                lineWidth=3
            )
    
    def draw_route(self, route: List[DeliveryPoint], current_pos: np.ndarray):
        """
        Desenha rota planejada.
        
        Args:
            route: Rota planejada
            current_pos: Posição atual do drone
        """
        # Remover linhas anteriores
        for line_id in self.route_lines:
            p.removeUserDebugItem(line_id)
        self.route_lines = []
        
        if not route:
            return
        
        # Desenhar linha do drone ao primeiro ponto
        if route:
            pos_from = current_pos.tolist() if hasattr(current_pos, 'tolist') else list(current_pos)
            pos_to = route[0].position.tolist() if hasattr(route[0].position, 'tolist') else list(route[0].position)
            line_id = p.addUserDebugLine(
                pos_from,
                pos_to,
                lineColorRGB=[0.0, 1.0, 1.0],
                lineWidth=2
            )
            self.route_lines.append(line_id)
        
        # Desenhar linhas entre pontos da rota
        for i in range(len(route) - 1):
            pos_from = route[i].position.tolist() if hasattr(route[i].position, 'tolist') else list(route[i].position)
            pos_to = route[i+1].position.tolist() if hasattr(route[i+1].position, 'tolist') else list(route[i+1].position)
            line_id = p.addUserDebugLine(
                pos_from,
                pos_to,
                lineColorRGB=[0.0, 1.0, 1.0],
                lineWidth=2
            )
            self.route_lines.append(line_id)
    
    def get_all_delivery_points(self) -> List[DeliveryPoint]:
        """Retorna todos os pontos de entrega."""
        return self.delivery_points
    
    def close(self):
        """Fecha a simulação."""
        p.disconnect(self.client_id)

