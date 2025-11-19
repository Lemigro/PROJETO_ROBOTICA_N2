"""
Script de teste simples para verificar instalação e componentes básicos.
"""
import sys
import numpy as np

def test_imports():
    """Testa se todas as dependências estão instaladas."""
    print("Testando imports...")
    try:
        import pybullet as p
        print("[OK] PyBullet importado com sucesso")
    except ImportError as e:
        print(f"[ERRO] Erro ao importar PyBullet: {e}")
        return False
    
    try:
        import yaml
        print("[OK] PyYAML importado com sucesso")
    except ImportError as e:
        print(f"[ERRO] Erro ao importar PyYAML: {e}")
        return False
    
    try:
        from src.pid_controller import PIDController
        print("[OK] Modulos do projeto importados com sucesso")
    except ImportError as e:
        print(f"[ERRO] Erro ao importar modulos: {e}")
        return False
    
    return True

def test_pid():
    """Testa o controlador PID."""
    print("\nTestando controlador PID...")
    try:
        from src.pid_controller import PIDController
        
        pid = PIDController([1.0, 1.0, 1.0], [0.0, 0.0, 0.0], [0.1, 0.1, 0.1])
        error = np.array([1.0, 0.5, 0.2])
        control = pid.update(error, 0.01)
        
        assert len(control) == 3
        print("[OK] Controlador PID funcionando corretamente")
        return True
    except Exception as e:
        print(f"[ERRO] Erro no teste PID: {e}")
        return False

def test_sensor():
    """Testa o sensor de proximidade."""
    print("\nTestando sensor de proximidade...")
    try:
        from src.sensor import ProximitySensor, DeliveryPoint
        
        sensor = ProximitySensor(5.0)
        point = DeliveryPoint(np.array([10.0, 10.0, 0.0]), 1)
        drone_pos = np.array([8.0, 8.0, 2.0])
        
        detected = sensor.detect_points(drone_pos, [point])
        assert len(detected) == 1
        print("[OK] Sensor de proximidade funcionando corretamente")
        return True
    except Exception as e:
        print(f"[ERRO] Erro no teste de sensor: {e}")
        return False

def test_route_planner():
    """Testa o planejador de rotas."""
    print("\nTestando planejador de rotas...")
    try:
        from src.route_planner import RoutePlanner
        from src.sensor import DeliveryPoint
        
        config = {'algorithm': 'nearest_neighbor', 'min_distance_threshold': 0.5}
        planner = RoutePlanner(config)
        
        points = [
            DeliveryPoint(np.array([5.0, 0.0, 0.0]), 1),
            DeliveryPoint(np.array([0.0, 5.0, 0.0]), 2),
            DeliveryPoint(np.array([10.0, 10.0, 0.0]), 3),
        ]
        
        start_pos = np.array([0.0, 0.0, 2.0])
        route = planner.plan_route(start_pos, points)
        
        assert len(route) > 0
        print("[OK] Planejador de rotas funcionando corretamente")
        return True
    except Exception as e:
        print(f"[ERRO] Erro no teste de planejamento: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("TESTES DO SISTEMA DE DRONE DE ENTREGAS")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_pid,
        test_sensor,
        test_route_planner
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    if all(results):
        print("[OK] TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        return 0
    else:
        print("[ERRO] ALGUNS TESTES FALHARAM")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

