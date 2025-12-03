"""
Sistema de logging e integração com Node-RED.
"""
import json
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np
import requests
try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

from src.sensor import DeliveryPoint


class NodeRedLogger:
    """Logger para integração com Node-RED via HTTP ou MQTT."""
    
    def __init__(self, config: dict):
        """
        Inicializa o logger Node-RED.
        
        Args:
            config: Configurações do Node-RED
        """
        self.enabled = config.get('enabled', True)
        self.protocol = config.get('protocol', 'http')
        
        if self.protocol == 'http':
            self.http_url = config['http']['url']
            self.http_interval = config['http'].get('interval', 0.5)
            self.last_http_send = 0
        elif self.protocol == 'mqtt':
            if mqtt is None:
                raise ImportError("paho-mqtt não está instalado")
            self.mqtt_broker = config['mqtt']['broker']
            self.mqtt_port = config['mqtt'].get('port', 1883)
            self.mqtt_topic = config['mqtt']['topic']
            self.mqtt_interval = config['mqtt'].get('interval', 0.5)
            self.last_mqtt_send = 0
            
            # Configurar cliente MQTT
            self.mqtt_client = mqtt.Client()
            try:
                self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
                self.mqtt_client.loop_start()
            except Exception as e:
                logging.warning(f"Falha ao conectar MQTT: {e}")
                self.enabled = False
        
        self.data_buffer = []
        
    def send_data(self, data: dict):
        """
        Envia dados para Node-RED.
        
        Args:
            data: Dicionário com dados a enviar
        """
        if not self.enabled:
            return
        
        current_time = time.time()
        
        if self.protocol == 'http':
            if current_time - self.last_http_send >= self.http_interval:
                try:
                    requests.post(
                        self.http_url,
                        json=data,
                        timeout=1.0
                    )
                    self.last_http_send = current_time
                except Exception as e:
                    logging.debug(f"Erro ao enviar HTTP: {e}")
        
        elif self.protocol == 'mqtt':
            if current_time - self.last_mqtt_send >= self.mqtt_interval:
                try:
                    payload = json.dumps(data)
                    self.mqtt_client.publish(self.mqtt_topic, payload)
                    self.last_mqtt_send = current_time
                except Exception as e:
                    logging.debug(f"Erro ao enviar MQTT: {e}")
    
    def close(self):
        """Fecha conexões."""
        if self.protocol == 'mqtt' and hasattr(self, 'mqtt_client'):
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()


class SimulationLogger:
    """Logger principal da simulação."""
    
    def __init__(self, config: dict):
        """
        Inicializa o logger da simulação.
        
        Args:
            config: Configurações de logging
        """
        # Configurar logging Python
        log_level = getattr(logging, config.get('level', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.get('file', 'logs/drone_simulation.log')),
                logging.StreamHandler() if config.get('console', True) else logging.NullHandler()
            ]
        )
        
        self.logger = logging.getLogger('DroneSimulation')
        
        # Node-RED logger
        node_red_config = config.get('node_red', {})
        if node_red_config.get('enabled', False):
            self.node_red = NodeRedLogger(node_red_config)
        else:
            self.node_red = None
        
        # Métricas
        self.metrics = {
            'start_time': time.time(),
            'total_distance': 0.0,
            'replan_count': 0,
            'points_detected': 0,
            'points_delivered': 0,
            'delivery_times': [],
            'replan_events': [],
            'detection_events': [],
            'route_history': []
        }
        
        self.last_position = None
        
    def log_detection(self, point: DeliveryPoint, drone_pos: np.ndarray):
        """
        Registra detecção de um ponto.
        
        Args:
            point: Ponto detectado
            drone_pos: Posição do drone no momento da detecção
        """
        point.detection_time = time.time()
        self.metrics['points_detected'] += 1
        
        event = {
            'type': 'detection',
            'timestamp': time.time(),
            'point_id': point.id,
            'point_position': point.position.tolist(),
            'drone_position': drone_pos.tolist()
        }
        
        self.metrics['detection_events'].append(event)
        self.logger.info(f"Ponto {point.id} detectado em {point.position}")
        
        if self.node_red:
            self.node_red.send_data({
                'event': 'detection',
                'data': event
            })
    
    def log_delivery(self, point: DeliveryPoint, drone_pos: np.ndarray):
        """
        Registra entrega em um ponto.
        
        Args:
            point: Ponto entregue
            drone_pos: Posição do drone
        """
        point.delivery_time = time.time()
        self.metrics['points_delivered'] += 1
        
        if point.detection_time:
            delivery_time = point.delivery_time - point.detection_time
            self.metrics['delivery_times'].append(delivery_time)
        
        event = {
            'type': 'delivery',
            'timestamp': time.time(),
            'point_id': point.id,
            'point_position': point.position.tolist(),
            'drone_position': drone_pos.tolist()
        }
        
        self.logger.info(f"Entrega concluída no ponto {point.id}")
        
        if self.node_red:
            self.node_red.send_data({
                'event': 'delivery',
                'data': event
            })
    
    def log_replan(self, route: List[DeliveryPoint], reason: str = "route_completion"):
        """
        Registra replanejamento de rota.
        
        Args:
            route: Nova rota planejada
            reason: Razão do replanejamento
        """
        self.metrics['replan_count'] += 1
        
        event = {
            'type': 'replan',
            'timestamp': time.time(),
            'reason': reason,
            'route_length': len(route),
            'route_points': [p.id for p in route]
        }
        
        self.metrics['replan_events'].append(event)
        self.logger.info(f"Replanejamento #{self.metrics['replan_count']}: {len(route)} pontos")
        
        if self.node_red:
            self.node_red.send_data({
                'event': 'replan',
                'data': event
            })
    
    def update_distance(self, current_pos: np.ndarray):
        """
        Atualiza distância total percorrida.
        
        Args:
            current_pos: Posição atual do drone
        """
        if self.last_position is not None:
            distance = np.linalg.norm(current_pos - self.last_position)
            self.metrics['total_distance'] += distance
        
        self.last_position = current_pos.copy() if hasattr(current_pos, 'copy') else np.array(current_pos)
    
    def log_state(
        self,
        drone_pos: np.ndarray,
        drone_vel: np.ndarray,
        target_pos: Optional[np.ndarray],
        route: List[DeliveryPoint],
        detected_points: List[DeliveryPoint]
    ):
        """
        Registra estado atual da simulação.
        
        Args:
            drone_pos: Posição do drone
            drone_vel: Velocidade do drone
            target_pos: Posição alvo atual
            route: Rota planejada
            detected_points: Pontos detectados
        """
        self.update_distance(drone_pos)
        
        state = {
            'timestamp': time.time(),
            'drone_position': drone_pos.tolist() if hasattr(drone_pos, 'tolist') else list(drone_pos),
            'drone_velocity': drone_vel.tolist() if hasattr(drone_vel, 'tolist') else list(drone_vel),
            'target_position': target_pos.tolist() if target_pos is not None else None,
            'route_length': len(route),
            'detected_points_count': len(detected_points),
            'delivered_points_count': sum(1 for p in detected_points if p.delivered)
        }
        
        if self.node_red:
            self.node_red.send_data({
                'event': 'state',
                'data': state,
                'metrics': self.get_metrics_summary()
            })
    
    def get_metrics_summary(self) -> dict:
        """Retorna resumo das métricas."""
        elapsed_time = time.time() - self.metrics['start_time']
        avg_delivery_time = (
            np.mean(self.metrics['delivery_times'])
            if self.metrics['delivery_times'] else 0.0
        )
        
        return {
            'elapsed_time': elapsed_time,
            'total_distance': self.metrics['total_distance'],
            'replan_count': self.metrics['replan_count'],
            'points_detected': self.metrics['points_detected'],
            'points_delivered': self.metrics['points_delivered'],
            'avg_delivery_time': avg_delivery_time,
            'efficiency': self._calculate_efficiency()
        }
    
    def _calculate_efficiency(self) -> float:
        """
        Calcula eficiência baseada em múltiplos fatores:
        1. Distância percorrida vs distância ideal (peso: 70%)
        2. Número de replanejamentos (peso: 20%)
        3. Tempo de execução (peso: 10%)
        """
        if self.metrics['points_delivered'] == 0:
            return 0.0
        
        # 1. Eficiência de distância (70% do peso)
        # Estima distância ideal: média de 5m entre pontos (configuração padrão)
        # Distância ideal = número de pontos * distância média entre pontos
        num_points = self.metrics['points_delivered']
        estimated_ideal_distance = num_points * 5.0  # 5m entre pontos (configuração padrão)
        
        # Se não há distância percorrida, eficiência é 0
        if self.metrics['total_distance'] == 0:
            distance_efficiency = 0.0
        else:
            # Eficiência = distância ideal / distância real (limitado a 1.0)
            distance_efficiency = min(estimated_ideal_distance / self.metrics['total_distance'], 1.0)
        
        # 2. Eficiência de replanejamento (20% do peso)
        # Penalidade por replanejamento: cada replanejamento reduz eficiência em 2%
        replan_ratio = self.metrics['replan_count'] / max(num_points, 1)
        replan_efficiency = max(1.0 - replan_ratio * 0.5, 0.5)  # Mínimo 50% mesmo com muitos replanejamentos
        
        # 3. Eficiência de tempo (10% do peso)
        # Tempo ideal estimado: 2s por ponto (configuração padrão)
        elapsed_time = time.time() - self.metrics['start_time']
        estimated_ideal_time = num_points * 2.0
        if elapsed_time == 0:
            time_efficiency = 0.0
        else:
            time_efficiency = min(estimated_ideal_time / elapsed_time, 1.0)
        
        # Eficiência total: média ponderada
        total_efficiency = (
            distance_efficiency * 0.70 +  # 70% peso na distância
            replan_efficiency * 0.20 +    # 20% peso em replanejamentos
            time_efficiency * 0.10         # 10% peso no tempo
        )
        
        # Garantir que eficiência está entre 0 e 1
        return max(0.0, min(1.0, total_efficiency))
    
    def close(self):
        """Fecha o logger e salva métricas finais."""
        if self.node_red:
            self.node_red.close()
        
        summary = self.get_metrics_summary()
        self.logger.info("=" * 50)
        self.logger.info("RESUMO FINAL DA SIMULAÇÃO")
        self.logger.info("=" * 50)
        self.logger.info(f"Tempo total: {summary['elapsed_time']:.2f}s")
        self.logger.info(f"Distância total: {summary['total_distance']:.2f}m")
        self.logger.info(f"Replanejamentos: {summary['replan_count']}")
        self.logger.info(f"Pontos detectados: {summary['points_detected']}")
        self.logger.info(f"Pontos entregues: {summary['points_delivered']}")
        self.logger.info(f"Tempo médio por entrega: {summary['avg_delivery_time']:.2f}s")
        self.logger.info(f"Eficiência: {summary['efficiency']:.2%}")
        self.logger.info("=" * 50)

