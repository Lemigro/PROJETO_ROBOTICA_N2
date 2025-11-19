"""
Exemplo de uso do Manipulador Planar
"""

import math
import sys
from pathlib import Path

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from manipulador_planar import ManipuladorPlanar


def exemplo_basico():
    """Exemplo básico de controle de posição"""
    print("=== Exemplo Básico: Manipulador 2 DOF ===\n")
    
    # Criar manipulador com 2 juntas
    manipulator = ManipuladorPlanar(num_joints=2, use_gui=True)
    
    # Definir ângulos de referência (em radianos)
    target_angles = [math.pi/4, math.pi/6]  # 45° e 30°
    
    print(f"Ângulos de referência: {[math.degrees(a) for a in target_angles]}°")
    print("Iniciando simulação...\n")
    
    try:
        # Executar simulação por 10 segundos
        manipulator.run_simulation(duration=10.0, target_angles=target_angles)
        
        # Aguardar um pouco antes de mudar o target
        print("\nAguardando 2 segundos...")
        import time
        time.sleep(2)
        
        # Mudar para novos ângulos (teste de perturbação)
        print("\n=== Mudando ângulos de referência ===")
        new_targets = [math.pi/2, -math.pi/4]  # 90° e -45°
        manipulator.set_target_angles(new_targets)
        manipulator.run_simulation(duration=10.0)
        
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário")
    finally:
        manipulator.cleanup()


def exemplo_3_dof():
    """Exemplo com manipulador 3 DOF"""
    print("=== Exemplo: Manipulador 3 DOF ===\n")
    
    # Criar manipulador com 3 juntas
    manipulator = ManipuladorPlanar(num_joints=3, use_gui=True)
    
    # Definir ângulos de referência
    target_angles = [math.pi/3, -math.pi/4, math.pi/6]  # 60°, -45°, 30°
    
    print(f"Ângulos de referência: {[math.degrees(a) for a in target_angles]}°")
    print("Iniciando simulação...\n")
    
    try:
        manipulator.run_simulation(duration=15.0, target_angles=target_angles)
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário")
    finally:
        manipulator.cleanup()


if __name__ == "__main__":
    # Executar exemplo básico
    exemplo_basico()
    
    # Descomente para testar 3 DOF
    # exemplo_3_dof()

