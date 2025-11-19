"""
Ambiente de Simulação com Obstáculos
"""
import pybullet as p
import pybullet_data
import numpy as np


class VacuumEnvironment:
    """Ambiente de simulação para o robô aspirador"""
    
    def __init__(self, physics_client, add_obstacles=True):
        """
        Inicializa o ambiente
        
        Args:
            physics_client: Cliente PyBullet
            add_obstacles: Se True, adiciona obstáculos ao ambiente
        """
        self.p = physics_client
        self.obstacle_ids = []
        
        # Configura o ambiente
        self._setup_environment()
        
        if add_obstacles:
            self._add_obstacles()
    
    def _setup_environment(self):
        """Configura o ambiente básico"""
        # Adiciona caminho de dados
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        
        # Carrega o chão
        plane_id = p.loadURDF("plane.urdf")
        
        # Configura gravidade
        p.setGravity(0, 0, -9.81)
    
    def _add_obstacles(self):
        """Adiciona obstáculos ao ambiente"""
        # Cria obstáculos usando caixas
        obstacles = [
            # Parede frontal
            {'pos': [3, 0, 0.5], 'size': [0.1, 4, 1]},
            # Parede traseira
            {'pos': [-3, 0, 0.5], 'size': [0.1, 4, 1]},
            # Parede esquerda
            {'pos': [0, 3, 0.5], 'size': [6, 0.1, 1]},
            # Parede direita
            {'pos': [0, -3, 0.5], 'size': [6, 0.1, 1]},
            # Obstáculos internos
            {'pos': [1, 1, 0.3], 'size': [0.5, 0.5, 0.6]},
            {'pos': [-1, -1, 0.3], 'size': [0.5, 0.5, 0.6]},
            {'pos': [0, 0, 0.3], 'size': [0.3, 0.3, 0.6]},
        ]
        
        for obs in obstacles:
            obstacle_id = self._create_box_obstacle(
                obs['pos'],
                obs['size'],
                color=[0.8, 0.2, 0.2, 1.0]  # Vermelho
            )
            self.obstacle_ids.append(obstacle_id)
    
    def _create_box_obstacle(self, position, half_extents, color=[0.5, 0.5, 0.5, 1.0]):
        """
        Cria um obstáculo em forma de caixa
        
        Args:
            position: Posição [x, y, z]
            half_extents: Meias dimensões [x, y, z]
            color: Cor RGBA
        
        Returns:
            int: ID do obstáculo
        """
        collision_shape = p.createCollisionShape(
            p.GEOM_BOX,
            halfExtents=half_extents
        )
        
        visual_shape = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=half_extents,
            rgbaColor=color
        )
        
        obstacle_id = p.createMultiBody(
            baseMass=0,  # Estático
            baseCollisionShapeIndex=collision_shape,
            baseVisualShapeIndex=visual_shape,
            basePosition=position
        )
        
        return obstacle_id
    
    def add_custom_obstacle(self, position, half_extents, color=None):
        """
        Adiciona um obstáculo customizado
        
        Args:
            position: Posição [x, y, z]
            half_extents: Meias dimensões [x, y, z]
            color: Cor RGBA (opcional)
        
        Returns:
            int: ID do obstáculo
        """
        if color is None:
            color = [0.5, 0.5, 0.5, 1.0]
        
        obstacle_id = self._create_box_obstacle(position, half_extents, color)
        self.obstacle_ids.append(obstacle_id)
        return obstacle_id
    
    def check_collision(self, robot_id, threshold=0.1):
        """
        Verifica se o robô colidiu com algum obstáculo
        
        Args:
            robot_id: ID do robô
            threshold: Distância mínima para considerar colisão
        
        Returns:
            bool: True se houve colisão
        """
        # Obtém contatos do robô
        contacts = p.getContactPoints(robot_id)
        
        for contact in contacts:
            # Verifica se o contato é com um obstáculo (não o chão)
            contact_id = contact[2]  # ID do objeto em contato
            if contact_id in self.obstacle_ids:
                return True
        
        return False

