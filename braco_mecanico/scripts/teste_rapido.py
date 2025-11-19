"""
Script de teste rápido para verificar se tudo está funcionando
"""

import sys
# -*- coding: utf-8 -*-

def test_imports():
    """Testa se todas as importações funcionam"""
    print("Testando importações...")
    try:
        import pybullet as p
        print("OK: PyBullet importado com sucesso")
    except ImportError as e:
        print(f"ERRO: Erro ao importar PyBullet: {e}")
        return False
    
    try:
        import numpy as np
        print("OK: NumPy importado com sucesso")
    except ImportError as e:
        print(f"ERRO: Erro ao importar NumPy: {e}")
        return False
    
    # Adicionar diretório src ao path
    import sys
    from pathlib import Path
    src_path = Path(__file__).parent.parent / 'src'
    sys.path.insert(0, str(src_path))
    
    try:
        from manipulador_planar import ManipuladorPlanar, PIDController
        print("OK: ManipuladorPlanar importado com sucesso")
    except ImportError as e:
        print(f"ERRO: Erro ao importar ManipuladorPlanar: {e}")
        return False
    
    try:
        from robo_movel import RoboMovel
        print("OK: RoboMovel importado com sucesso")
    except ImportError as e:
        print(f"ERRO: Erro ao importar RoboMovel: {e}")
        return False
    
    try:
        from node_red_interface import NodeRedInterface
        print("OK: NodeRedInterface importado com sucesso")
    except ImportError as e:
        print(f"ERRO: Erro ao importar NodeRedInterface: {e}")
        return False
    
    return True

def test_pid():
    """Testa o controlador PID"""
    print("\nTestando controlador PID...")
    try:
        import sys
        from pathlib import Path
        src_path = Path(__file__).parent.parent / 'src'
        sys.path.insert(0, str(src_path))
        from manipulador_planar import PIDController
        pid = PIDController(kp=1.0, ki=0.1, kd=0.1)
        
        # Teste básico
        error = 1.0
        dt = 0.01
        torque = pid.compute(error, dt)
        
        if abs(torque) > 0:
            print(f"OK: PID funcionando (torque calculado: {torque:.3f})")
            return True
        else:
            print("ERRO: PID retornou torque zero")
            return False
    except Exception as e:
        print(f"ERRO: Erro ao testar PID: {e}")
        return False

def main():
    """Função principal de teste"""
    print("=== Teste Rápido do Projeto ===\n")
    
    # Testar importações
    if not test_imports():
        print("\nERRO: Falha nos testes de importacao")
        sys.exit(1)
    
    # Testar PID
    if not test_pid():
        print("\nERRO: Falha no teste do PID")
        sys.exit(1)
    
    print("\nOK: Todos os testes basicos passaram!")
    print("\nPróximos passos:")
    print("1. Execute: python examples/exemplo_manipulador.py")
    print("2. Execute: python examples/exemplo_robo_movel.py")
    print("\nNota: Certifique-se de que o PyBullet está instalado corretamente.")

if __name__ == "__main__":
    main()

