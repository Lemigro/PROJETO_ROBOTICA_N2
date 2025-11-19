"""
Script para visualizar o mapa gerado pelo robô aspirador
"""
import json
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Adiciona o diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.mapping import OccupancyMap

def visualizar_mapa(arquivo_mapa):
    """Visualiza o mapa de ocupação e cobertura"""
    print(f"Carregando mapa de {arquivo_mapa}...")
    
    # Carrega o mapa
    mapa = OccupancyMap()
    if not mapa.load(arquivo_mapa):
        print(f"Erro: Nao foi possivel carregar {arquivo_mapa}")
        return
    
    print(f"Mapa carregado!")
    print(f"  Dimensoes: {mapa.width}x{mapa.height} celulas")
    print(f"  Resolucao: {mapa.resolution}m por celula")
    print(f"  Trajetoria: {len(mapa.trajectory)} pontos")
    
    # Calcula estatisticas
    cobertura_pct = mapa.get_coverage_percentage()
    celulas_livres = np.sum(mapa.occupancy == 0)
    celulas_ocupadas = np.sum(mapa.occupancy == 1)
    celulas_desconhecidas = np.sum(mapa.occupancy == -1)
    celulas_visitadas = np.sum(mapa.coverage > 0)
    
    print(f"\nEstatisticas:")
    print(f"  Cobertura: {cobertura_pct:.2f}%")
    print(f"  Celulas livres: {celulas_livres}")
    print(f"  Celulas ocupadas: {celulas_ocupadas}")
    print(f"  Celulas desconhecidas: {celulas_desconhecidas}")
    print(f"  Celulas visitadas: {celulas_visitadas}")
    
    # Cria visualizacao
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # 1. Mapa de Ocupacao
    ax1 = axes[0]
    ocupacao_vis = np.zeros_like(mapa.occupancy, dtype=float)
    ocupacao_vis[mapa.occupancy == -1] = 0.5  # Desconhecido = cinza
    ocupacao_vis[mapa.occupancy == 0] = 1.0    # Livre = branco
    ocupacao_vis[mapa.occupancy == 1] = 0.0    # Ocupado = preto
    
    ax1.imshow(ocupacao_vis, cmap='gray', origin='lower')
    ax1.set_title('Mapa de Ocupacao')
    ax1.set_xlabel('X (celulas)')
    ax1.set_ylabel('Y (celulas)')
    
    # 2. Mapa de Cobertura
    ax2 = axes[1]
    cobertura_vis = mapa.coverage.copy()
    cobertura_vis[mapa.occupancy == 1] = -1  # Marca obstaculos
    
    im = ax2.imshow(cobertura_vis, cmap='YlOrRd', origin='lower')
    ax2.set_title('Mapa de Cobertura (visitas)')
    ax2.set_xlabel('X (celulas)')
    ax2.set_ylabel('Y (celulas)')
    plt.colorbar(im, ax=ax2, label='Numero de visitas')
    
    # 3. Trajetoria
    ax3 = axes[2]
    if len(mapa.trajectory) > 0:
        traj = np.array(mapa.trajectory)
        x = traj[:, 0]
        y = traj[:, 1]
        
        # Converte para coordenadas do mapa
        map_x = ((x - mapa.origin_x) / mapa.resolution).astype(int)
        map_y = ((y - mapa.origin_y) / mapa.resolution).astype(int)
        
        # Filtra pontos dentro do mapa
        valid = (map_x >= 0) & (map_x < mapa.width) & (map_y >= 0) & (map_y < mapa.height)
        map_x = map_x[valid]
        map_y = map_y[valid]
        
        ax3.plot(map_x, map_y, 'b-', linewidth=0.5, alpha=0.7, label='Trajetoria')
        ax3.plot(map_x[0], map_y[0], 'go', markersize=8, label='Inicio')
        ax3.plot(map_x[-1], map_y[-1], 'ro', markersize=8, label='Fim')
        ax3.set_title('Trajetoria do Robo')
        ax3.set_xlabel('X (celulas)')
        ax3.set_ylabel('Y (celulas)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_aspect('equal')
    
    plt.tight_layout()
    
    # Extrai apenas o nome do arquivo (sem caminho e sem extensão)
    nome_base = os.path.basename(arquivo_mapa).replace(".json", "")
    
    # Salva no diretório maps/ (mesmo diretório onde estão os mapas)
    diretorio_maps = os.path.dirname(arquivo_mapa) if os.path.dirname(arquivo_mapa) else "maps"
    if not os.path.exists(diretorio_maps):
        diretorio_maps = "maps"
        os.makedirs(diretorio_maps, exist_ok=True)
    
    arquivo_saida = os.path.join(diretorio_maps, f'mapa_visualizacao_{nome_base}.png')
    plt.savefig(arquivo_saida, dpi=150)
    print(f"\nVisualizacao salva em: {arquivo_saida}")
    print("\nFechando a janela para continuar...")
    plt.show()

if __name__ == "__main__":
    import sys
    
    arquivo = "map_exec_1.json"
    if len(sys.argv) > 1:
        arquivo = sys.argv[1]
    
    try:
        visualizar_mapa(arquivo)
    except ImportError:
        print("Matplotlib nao esta instalado. Instale com: pip install matplotlib")
    except Exception as e:
        print(f"Erro ao visualizar: {e}")
        import traceback
        traceback.print_exc()

