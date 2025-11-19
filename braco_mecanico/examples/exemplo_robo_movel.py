"""
Exemplo de uso do Robô Móvel Diferencial
"""

import sys
from pathlib import Path

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from robo_movel import RoboMovel


def exemplo_basico():
    """Exemplo básico de navegação com evasão de obstáculos"""
    print("=== Exemplo: Robô Móvel com Evasão de Obstáculos ===\n")
    
    robo = RoboMovel(use_gui=True)
    
    try:
        # Executar simulação por 30 segundos
        robo.run_simulation(duration=30.0)
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário")
    finally:
        robo.cleanup()


if __name__ == "__main__":
    exemplo_basico()

