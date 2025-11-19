"""
Sistema de Logging e Integração com Node-RED
"""
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional


class NodeREDLogger:
    """Logger para enviar dados ao Node-RED via HTTP/MQTT"""
    
    def __init__(self, node_red_url="http://localhost:1880", use_mqtt=False, mqtt_broker=None):
        """
        Inicializa o logger
        
        Args:
            node_red_url: URL base do Node-RED (endpoint HTTP)
            use_mqtt: Se True, usa MQTT em vez de HTTP
            mqtt_broker: Endereço do broker MQTT (se usar MQTT)
        """
        self.node_red_url = node_red_url
        self.use_mqtt = use_mqtt
        self.mqtt_broker = mqtt_broker
        self.session = requests.Session()
        self.logs = []  # Buffer local de logs
    
    def log_metrics(self, metrics: Dict):
        """
        Envia métricas ao Node-RED
        
        Args:
            metrics: Dicionário com métricas
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'type': 'metrics',
            'data': metrics
        }
        
        self.logs.append(log_entry)
        
        if self.use_mqtt:
            self._send_mqtt(log_entry)
        else:
            self._send_http(log_entry)
    
    def log_trajectory_point(self, x: float, y: float, yaw: float, sensors: List[float]):
        """
        Envia um ponto da trajetória
        
        Args:
            x, y, yaw: Pose do robô
            sensors: Leituras dos sensores
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'type': 'trajectory',
            'data': {
                'x': x,
                'y': y,
                'yaw': yaw,
                'sensors': sensors
            }
        }
        
        self.logs.append(log_entry)
        
        if self.use_mqtt:
            self._send_mqtt(log_entry)
        else:
            self._send_http(log_entry)
    
    def log_execution_summary(self, summary: Dict):
        """
        Envia resumo de uma execução
        
        Args:
            summary: Dicionário com resumo da execução
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'type': 'execution_summary',
            'data': summary
        }
        
        self.logs.append(log_entry)
        
        if self.use_mqtt:
            self._send_mqtt(log_entry)
        else:
            self._send_http(log_entry)
    
    def _send_http(self, log_entry: Dict):
        """Envia log via HTTP POST ao Node-RED"""
        try:
            # Endpoint do Node-RED (ajuste conforme sua configuração)
            endpoint = f"{self.node_red_url}/robo-data"
            
            # Envia dados sem esperar resposta (fire and forget)
            # Isso evita timeout se o Node-RED não retornar resposta
            response = self.session.post(
                endpoint,
                json=log_entry,
                timeout=0.5  # Timeout muito curto, só para verificar conexão
            )
            
            # Se chegou aqui, a conexão funcionou (mesmo que status não seja 200)
            # Não precisa fazer nada, os dados foram enviados
        except requests.exceptions.RequestException as e:
            # Silenciosamente falha se Node-RED não estiver disponível
            pass
    
    def _send_mqtt(self, log_entry: Dict):
        """Envia log via MQTT (requer paho-mqtt)"""
        try:
            import paho.mqtt.client as mqtt
            
            client = mqtt.Client()
            client.connect(self.mqtt_broker or "localhost", 1883, 60)
            client.publish("robot/vacuum/logs", json.dumps(log_entry))
            client.disconnect()
        except ImportError:
            print("Warning: paho-mqtt not installed. Install with: pip install paho-mqtt")
        except Exception as e:
            print(f"Warning: Failed to send MQTT log: {e}")
    
    def get_logs(self) -> List[Dict]:
        """Retorna todos os logs armazenados"""
        return self.logs.copy()
    
    def clear_logs(self):
        """Limpa o buffer de logs"""
        self.logs = []


class MetricsCollector:
    """Coletor de métricas de desempenho"""
    
    def __init__(self):
        """Inicializa o coletor"""
        self.start_time = None
        self.total_time = 0.0
        self.total_energy = 0.0
        self.collisions = 0
        self.trajectory_length = 0.0
        self.last_position = None
    
    def start(self):
        """Inicia a coleta de métricas"""
        self.start_time = time.time()
        self.total_time = 0.0
        self.total_energy = 0.0
        self.collisions = 0
        self.trajectory_length = 0.0
        self.last_position = None
    
    def update(self, position, energy_delta, has_collision=False):
        """
        Atualiza métricas
        
        Args:
            position: Posição atual (x, y)
            energy_delta: Incremento de energia
            has_collision: Se houve colisão
        """
        if self.start_time is None:
            self.start()
        
        self.total_energy += energy_delta
        
        if has_collision:
            self.collisions += 1
        
        if self.last_position is not None:
            import math
            dx = position[0] - self.last_position[0]
            dy = position[1] - self.last_position[1]
            self.trajectory_length += math.sqrt(dx**2 + dy**2)
        
        self.last_position = position
        self.total_time = time.time() - self.start_time
    
    def get_metrics(self, coverage_percentage: float) -> Dict:
        """
        Retorna métricas atuais
        
        Args:
            coverage_percentage: Porcentagem de área coberta
        
        Returns:
            dict: Métricas coletadas
        """
        efficiency = coverage_percentage / self.total_energy if self.total_energy > 0 else 0
        
        return {
            'total_time': self.total_time,
            'total_energy': self.total_energy,
            'collisions': self.collisions,
            'trajectory_length': self.trajectory_length,
            'coverage_percentage': coverage_percentage,
            'efficiency': efficiency,
            'average_speed': self.trajectory_length / self.total_time if self.total_time > 0 else 0
        }

