"""
Arquivo principal para executar a simulação do Manipulador Planar
Execute: python main.py
"""

import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from manipulador_planar import main

if __name__ == "__main__":
    main()

