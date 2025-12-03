"""
Interface para comunicação com Node-RED via MQTT - Robô Móvel
"""

import json
import time
from typing import Dict, Optional

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("Aviso: paho-mqtt não está instalado. Métricas não serão enviadas ao Node-RED.")


class NodeRedInterface:
    """Interface para enviar métricas ao Node-RED via MQTT - Robô Móvel"""
    
    def __init__(self, broker: str = "localhost", port: int = 1883, 
                 topic_prefix: str = "robotica_n2"):
        """
        Inicializa a interface MQTT
        
        Args:
            broker: Endereço do broker MQTT
            port: Porta do broker MQTT
            topic_prefix: Prefixo dos tópicos MQTT
        """
        self.broker = broker
        self.port = port
        self.topic_prefix = topic_prefix
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        
        if MQTT_AVAILABLE:
            self._connect()
        else:
            print("MQTT não disponível. Métricas serão apenas exibidas no console.")
    
    def _connect(self):
        """Conecta ao broker MQTT"""
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            
            # Tentar conectar (não bloquear se não conseguir)
            try:
                self.client.connect(self.broker, self.port, 60)
                self.client.loop_start()
                time.sleep(0.1)  # Pequeno delay para estabelecer conexão
            except Exception as e:
                print(f"Aviso: Não foi possível conectar ao broker MQTT em {self.broker}:{self.port}")
                print(f"Erro: {e}")
                print("Métricas serão apenas exibidas no console.")
                self.client = None
        except Exception as e:
            print(f"Erro ao inicializar cliente MQTT: {e}")
            self.client = None
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback de conexão"""
        if rc == 0:
            self.connected = True
            print(f"Conectado ao broker MQTT em {self.broker}:{self.port}")
        else:
            print(f"Falha ao conectar ao broker MQTT. Código: {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback de desconexão"""
        self.connected = False
        if rc != 0:
            print("Desconectado inesperadamente do broker MQTT")
    
    def send_metrics(self, system_name: str, metrics: Dict):
        """
        Envia métricas ao Node-RED
        
        Args:
            system_name: Nome do sistema ('robo_movel')
            metrics: Dicionário com as métricas
        """
        # Converter valores numpy para tipos nativos do Python (evita problemas de serialização)
        clean_metrics = {}
        for key, value in metrics.items():
            if hasattr(value, 'item'):  # numpy scalar
                clean_metrics[key] = float(value.item())
            elif isinstance(value, (int, float)):
                clean_metrics[key] = float(value)
            else:
                clean_metrics[key] = value
        
        # Adicionar timestamp
        payload = {
            'timestamp': time.time(),
            'system': system_name,
            'metrics': clean_metrics
        }
        
        # Tentar enviar via MQTT
        if self.client and self.connected:
            try:
                topic = f"{self.topic_prefix}/{system_name}/metrics"
                json_payload = json.dumps(payload, default=str)
                self.client.publish(topic, json_payload, qos=1)
            except Exception as e:
                print(f"Erro ao enviar métricas via MQTT: {e}")
    
    def disconnect(self):
        """Desconecta do broker MQTT"""
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass
            self.connected = False

