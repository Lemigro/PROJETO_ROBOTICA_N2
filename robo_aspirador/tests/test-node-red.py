"""
Script de teste para verificar se o Node-RED está recebendo dados
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
import json
from datetime import datetime

def test_node_red_connection():
    """Testa a conexão com Node-RED"""
    url = "http://127.0.0.1:1880/robo-data"
    
    # Teste 1: Métricas
    print("Enviando métricas de teste...")
    metrics_data = {
        "timestamp": datetime.now().isoformat(),
        "type": "metrics",
        "data": {
            "total_time": 120.5,
            "coverage_percentage": 85.3,
            "total_energy": 150.2,
            "efficiency": 0.568,
            "collisions": 2,
            "trajectory_length": 45.6,
            "average_speed": 0.38
        }
    }
    
    try:
        response = requests.post(url, json=metrics_data, timeout=2)
        if response.status_code == 200:
            print("[OK] Metricas enviadas com sucesso!")
        else:
            print(f"[AVISO] Resposta: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERRO] Node-RED nao esta rodando ou nao esta acessivel em http://127.0.0.1:1880")
        print("   Execute: node-red")
        return False
    except requests.exceptions.ReadTimeout:
        print("[ERRO] Timeout - Node-RED nao esta respondendo")
        print("   Verifique se o endpoint /robo-data esta configurado no Node-RED")
        print("   E se o Node-RED esta realmente rodando")
        return False
    except Exception as e:
        print(f"[ERRO] {e}")
        return False
    
    # Teste 2: Trajetória
    print("\nEnviando ponto de trajetória...")
    trajectory_data = {
        "timestamp": datetime.now().isoformat(),
        "type": "trajectory",
        "data": {
            "x": 1.5,
            "y": 2.3,
            "yaw": 0.5,
            "sensors": [1.2, 0.8, 1.5, 1.0, 1.3]
        }
    }
    
    try:
        response = requests.post(url, json=trajectory_data, timeout=2)
        if response.status_code == 200:
            print("[OK] Trajetoria enviada com sucesso!")
        else:
            print(f"[AVISO] Resposta: {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")
        return False
    
    # Teste 3: Resumo
    print("\nEnviando resumo de execução...")
    summary_data = {
        "timestamp": datetime.now().isoformat(),
        "type": "execution_summary",
        "data": {
            "execution_number": 1,
            "coverage_percentage": 85.3,
            "total_time": 120.5,
            "total_energy": 150.2,
            "collisions": 2,
            "trajectory_length": 45.6,
            "efficiency": 0.568
        }
    }
    
    try:
        response = requests.post(url, json=summary_data, timeout=2)
        if response.status_code == 200:
            print("[OK] Resumo enviado com sucesso!")
        else:
            print(f"[AVISO] Resposta: {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")
        return False
    
    print("\n[SUCESSO] Todos os testes concluidos!")
    print("   Verifique o Node-RED em http://127.0.0.1:1880")
    print("   Os dados devem aparecer no painel de debug (lado direito)")
    print("   Endpoint configurado: /robo-data")
    return True

if __name__ == "__main__":
    print("=== Teste de Conexão Node-RED ===\n")
    test_node_red_connection()

