"""
Script para testar a conexão MQTT
Verifica se o broker está funcionando e se os tópicos estão corretos
"""

import time
import json
import sys
from pathlib import Path

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from node_red_interface import NodeRedInterface


def test_mqtt_connection():
    """Testa a conexão MQTT"""
    print("=== Teste de Conexão MQTT ===\n")
    
    # Criar interface
    node_red = NodeRedInterface()
    
    if not node_red.client:
        print("❌ Cliente MQTT não foi criado")
        return False
    
    if not node_red.connected:
        print("❌ Não conectado ao broker MQTT")
        print("   Verifique se o Mosquitto está rodando:")
        print("   - Windows: Verifique o serviço Mosquitto")
        print("   - Linux: sudo systemctl start mosquitto")
        return False
    
    print("✓ Conectado ao broker MQTT\n")
    
    # Testar envio de métricas
    print("Enviando métricas de teste...")
    
    # Teste 1: Manipulador Planar
    print("\n[1] Testando Manipulador Planar...")
    test_metrics_manipulador = {
        'erro_medio_posicao': 0.05,
        'tempo_estabilizacao': 2.3,
        'energia_total_gasta': 15.7,
        'overshoot_maximo': 0.12,
        'estabilizado': True
    }
    node_red.send_metrics('manipulador_planar', test_metrics_manipulador)
    time.sleep(0.5)
    
    # Teste 2: Robô Móvel
    print("[2] Testando Robô Móvel...")
    test_metrics_robo = {
        'numero_colisoes': 2,
        'tempo_reacao_medio': 0.15,
        'distancia_percorrida_sem_impacto': 12.5,
        'erro_medio_lateral': 0.08
    }
    node_red.send_metrics('robo_movel', test_metrics_robo)
    time.sleep(0.5)
    
    print("\n✓ Métricas enviadas com sucesso!")
    print("\nVerifique no Node-RED se as mensagens foram recebidas.")
    print("Tópicos utilizados:")
    print("  - robotica_n2/manipulador_planar/metrics")
    print("  - robotica_n2/robo_movel/metrics")
    
    # Desconectar
    node_red.disconnect()
    
    return True


def test_mqtt_broker():
    """Testa se o broker MQTT está acessível"""
    print("\n=== Teste do Broker MQTT ===\n")
    
    try:
        import paho.mqtt.client as mqtt
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("✓ Broker MQTT está acessível")
                client.disconnect()
            else:
                print(f"❌ Falha ao conectar. Código: {rc}")
        
        client = mqtt.Client()
        client.on_connect = on_connect
        
        try:
            client.connect("localhost", 1883, 60)
            client.loop_start()
            time.sleep(1)
            client.loop_stop()
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            print("\nSoluções:")
            print("1. Instale o Mosquitto:")
            print("   - Windows: Baixe de https://mosquitto.org/download/")
            print("   - Linux: sudo apt-get install mosquitto mosquitto-clients")
            print("2. Inicie o serviço:")
            print("   - Windows: net start mosquitto")
            print("   - Linux: sudo systemctl start mosquitto")
            return False
        
    except ImportError:
        print("❌ paho-mqtt não está instalado")
        print("   Execute: pip install paho-mqtt")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("Teste de Configuração MQTT/Node-RED")
    print("=" * 50)
    print()
    
    # Testar broker
    broker_ok = test_mqtt_broker()
    
    if broker_ok:
        # Testar conexão e envio
        test_mqtt_connection()
    else:
        print("\n❌ Configure o broker MQTT antes de continuar")
    
    print("\n" + "=" * 50)

