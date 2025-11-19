"""
Teste rápido de configuração e imports.
"""
import yaml
import sys

def test_config():
    """Testa se a configuração está correta."""
    print("Testando configuracao...")
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Verificar estrutura
        assert 'simulation' in config
        assert 'drone' in config
        assert 'control' in config
        assert 'sensor' in config
        assert 'route_planning' in config
        assert 'logging' in config
        
        # Verificar tipos
        assert isinstance(config['simulation']['timestep'], (int, float))
        assert isinstance(config['drone']['max_velocity'], (int, float))
        assert 'pid' in config['control']
        assert 'position' in config['control']['pid']
        assert 'attitude' in config['control']['pid']
        
        print("[OK] Configuracao valida")
        print(f"  - Timestep: {config['simulation']['timestep']} (tipo: {type(config['simulation']['timestep']).__name__})")
        print(f"  - Pontos de entrega: {config['environment']['num_delivery_points']}")
        print(f"  - Raio de deteccao: {config['sensor']['detection_radius']}m")
        return True
    except Exception as e:
        print(f"[ERRO] Erro na configuracao: {e}")
        return False

def test_imports():
    """Testa imports principais."""
    print("\nTestando imports...")
    try:
        from src.drone_simulator import DroneSimulator
        from src.pid_controller import DroneController
        from src.sensor import ProximitySensor
        from src.route_planner import RoutePlanner
        from src.logger import SimulationLogger
        print("[OK] Todos os modulos importados com sucesso")
        return True
    except Exception as e:
        print(f"[ERRO] Erro nos imports: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_initialization():
    """Testa inicialização dos componentes."""
    print("\nTestando inicializacao...")
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Testar inicialização (sem PyBullet GUI para teste rápido)
        from src.pid_controller import DroneController
        from src.sensor import ProximitySensor
        from src.route_planner import RoutePlanner
        
        # Mesclar configurações
        control_config = config['control'].copy()
        control_config.update({
            'max_velocity': config['drone']['max_velocity'],
            'max_acceleration': config['drone']['max_acceleration']
        })
        
        controller = DroneController(control_config)
        sensor = ProximitySensor(config['sensor']['detection_radius'])
        route_planner = RoutePlanner(config['route_planning'])
        
        print("[OK] Componentes inicializados com sucesso")
        return True
    except Exception as e:
        print(f"[ERRO] Erro na inicializacao: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE CONFIGURACAO E INICIALIZACAO")
    print("=" * 60)
    
    results = [
        test_config(),
        test_imports(),
        test_initialization()
    ]
    
    print("\n" + "=" * 60)
    if all(results):
        print("[OK] TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("[ERRO] ALGUNS TESTES FALHARAM")
        print("=" * 60)
        sys.exit(1)

