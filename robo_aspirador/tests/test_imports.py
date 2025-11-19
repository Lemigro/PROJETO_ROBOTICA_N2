"""Script de teste para verificar se todos os módulos podem ser importados"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src import robot
    print("[OK] robot.py importado")
    
    from src import sensors
    print("[OK] sensors.py importado")
    
    from src import controller
    print("[OK] controller.py importado")
    
    from src import mapping
    print("[OK] mapping.py importado")
    
    from src import learning
    print("[OK] learning.py importado")
    
    from src import logger
    print("[OK] logger.py importado")
    
    from src import environment
    print("[OK] environment.py importado")
    
    print("\n[SUCESSO] Todos os modulos foram importados com sucesso!")
    
except ImportError as e:
    print(f"[ERRO] Erro ao importar: {e}")
    import sys
    sys.exit(1)

