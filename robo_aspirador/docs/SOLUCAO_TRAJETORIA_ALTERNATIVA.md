# Solução Alternativa: Trajetória 2D

## 🔍 Problema

O gráfico de **Trajetória do Robô (Vista Superior)** não está exibindo dados, mesmo com os dados chegando corretamente no Node-RED.

## ✅ Tentativas Realizadas

1. ✅ Formato `{x: number, y: number}` - Não funcionou
2. ✅ Chart type `scatter` - Não funcionou  
3. ✅ Chart type `xy` - Não funcionou
4. ✅ Enviar pontos individuais - Não funcionou
5. ✅ Enviar arrays completos - Testando...

## 🎯 Solução Alternativa: Usar Python para Visualizar

Se o Node-RED Dashboard não funcionar, você pode visualizar a trajetória diretamente no Python:

### Opção 1: Script de Visualização Python

Crie um script `visualizar_trajetoria.py`:

```python
import json
import matplotlib.pyplot as plt
import numpy as np

# Carrega trajetória do arquivo
with open('maps/map_exec_1.json', 'r') as f:
    map_data = json.load(f)

trajectory = map_data.get('trajectory', [])

if trajectory:
    x = [p['x'] for p in trajectory]
    y = [p['y'] for p in trajectory]
    
    plt.figure(figsize=(10, 10))
    plt.plot(x, y, 'b-', linewidth=1, alpha=0.7)
    plt.scatter(x[0], y[0], c='green', s=100, marker='o', label='Início')
    plt.scatter(x[-1], y[-1], c='red', s=100, marker='s', label='Fim')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.title('Trajetória do Robô (Vista Superior)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('trajectory_plot.png', dpi=150)
    plt.show()
    print("Gráfico salvo em trajectory_plot.png")
else:
    print("Nenhuma trajetória encontrada")
```

Execute:
```bash
python visualizar_trajetoria.py
```

### Opção 2: Adicionar ao main.py

Adicione no final do `main.py`, no método `finish()`:

```python
def finish(self):
    # ... código existente ...
    
    # Visualiza trajetória
    if len(self.map.trajectory) > 0:
        try:
            import matplotlib.pyplot as plt
            x = [p['x'] for p in self.map.trajectory]
            y = [p['y'] for p in self.map.trajectory]
            
            plt.figure(figsize=(8, 8))
            plt.plot(x, y, 'b-', linewidth=1, alpha=0.7)
            plt.scatter(x[0], y[0], c='green', s=100, marker='o', label='Início')
            plt.scatter(x[-1], y[-1], c='red', s=100, marker='s', label='Fim')
            plt.xlabel('X (m)')
            plt.ylabel('Y (m)')
            plt.title(f'Trajetória - Execução {self.execution_number}')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.axis('equal')
            plt.tight_layout()
            plt.savefig(f'trajectory_exec_{self.execution_number}.png', dpi=150)
            print(f"Trajetória salva em trajectory_exec_{self.execution_number}.png")
            plt.close()
        except ImportError:
            print("matplotlib não instalado. Instale com: pip install matplotlib")
```

## 📊 Status Atual

- ✅ **Gauges**: Funcionando
- ✅ **Evolução Tempo vs Cobertura**: Funcionando
- ✅ **Comparativo Entre Execuções**: Funcionando
- ❌ **Trajetória 2D**: Não funcionando no Node-RED Dashboard

## 💡 Recomendação

Use a **Opção 2** para visualizar a trajetória automaticamente após cada execução. O gráfico será salvo como imagem PNG.

---

**Nota**: O problema pode ser uma limitação do Node-RED Dashboard com scatter charts em tempo real. A visualização em Python é mais confiável e oferece mais controle.

