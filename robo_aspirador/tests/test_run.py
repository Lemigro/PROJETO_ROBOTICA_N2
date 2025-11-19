"""Teste rápido para verificar se a simulação pode ser inicializada"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    print("Testando inicializacao da simulacao...")
    
    # Importa apenas o necessário para testar
    from main import VacuumRobotSimulation
    
    print("[OK] Classe VacuumRobotSimulation importada")
    
    # Tenta criar uma instância (mas não executa)
    print("\nTentando criar instancia da simulacao...")
    print("(Isso pode demorar alguns segundos enquanto o PyBullet carrega)")
    
    # Cria simulação em modo headless para teste rápido
    sim = VacuumRobotSimulation(gui=False, load_map=False, execution_number=1)
    
    print("[OK] Simulacao criada com sucesso!")
    print("\n[SUCESSO] Tudo pronto para executar!")
    print("\nPara executar a simulacao completa, use:")
    print("  python main.py --execution 1")
    print("\nOu com interface grafica:")
    print("  python main.py")
    
    # Limpa
    if hasattr(sim, 'physics_client') and sim.physics_client is not None:
        import pybullet as p
        if p.isConnected():
            p.disconnect()
    
except Exception as e:
    print(f"\n[ERRO] Falha ao inicializar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

