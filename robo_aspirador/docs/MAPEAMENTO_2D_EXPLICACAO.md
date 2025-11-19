# Mapeamento de Ocupação 2D - Explicação Técnica

## 📊 Visão Geral

O sistema implementa **mapeamento de ocupação 2D** (bidimensional), que é o padrão para robôs móveis terrestres. Embora a simulação PyBullet seja 3D, o mapeamento projeta tudo no plano horizontal (XY).

## 🔍 Como Funciona

### Simulação 3D vs Mapeamento 2D

```
┌─────────────────────────────────────┐
│  SIMULAÇÃO 3D (PyBullet)            │
│  - Coordenadas: (x, y, z)           │
│  - Obstáculos têm altura            │
│  - Robô se move em 3D               │
└─────────────────────────────────────┘
              ↓ PROJEÇÃO
┌─────────────────────────────────────┐
│  MAPA 2D (OccupancyMap)             │
│  - Coordenadas: (x, y)              │
│  - Vista de cima (top-down)         │
│  - Apenas plano horizontal          │
└─────────────────────────────────────┘
```

### Por que 2D?

1. **Robôs terrestres** se movem principalmente no plano horizontal
2. **Eficiência**: Mapas 2D são muito mais rápidos de processar
3. **Padrão da indústria**: SLAM 2D é o mais comum (ROS, etc.)
4. **Suficiente**: Para navegação, altura não é crítica

## 📐 Implementação Técnica

### 1. Estrutura do Mapa

```python
# src/mapping.py - Linha 12
class OccupancyMap:
    """Mapa de ocupação 2D para mapeamento do ambiente"""
    
    def __init__(self, width=20, height=20, resolution=0.1, origin_x=-10, origin_y=-10):
        # Apenas 2 dimensões: width (X) e height (Y)
        # Não há dimensão Z (altura)
```

### 2. Projeção 3D → 2D

```python
# main.py - Linha 124-135
# Obtém pose do robô (3D)
x, y, yaw = self.robot.get_pose()  # z é ignorado

# Atualiza mapa usando apenas x, y
self.map.update_occupancy(x, y, sensor_readings, sensor_angles, yaw)
self.map.update_coverage(x, y, dt)
```

### 3. Conversão de Coordenadas

```python
# src/mapping.py - Linhas 44-70
def world_to_map(self, x, y):
    """Converte coordenadas do mundo para células do mapa"""
    # Apenas x e y são usados
    map_x = int((x - self.origin_x) / self.resolution)
    map_y = int((y - self.origin_y) / self.resolution)
    return map_x, map_y
```

### 4. Sensores Projetados no Plano

Os sensores ultrassônicos detectam obstáculos em 3D, mas apenas a **projeção horizontal** é usada:

```python
# src/mapping.py - Linha 76
def update_occupancy(self, x, y, sensor_readings, sensor_angles, robot_orientation):
    # sensor_readings: distâncias no plano horizontal
    # sensor_angles: ângulos no plano horizontal
    # robot_orientation: yaw (rotação em torno do eixo Z)
```

## 🗺️ Estrutura do Mapa

### Valores das Células

```python
# -1 = Desconhecido (cinza)
#  0 = Livre (branco)
#  1 = Ocupado (preto)
```

### Dimensões

- **Width**: Largura em células (eixo X)
- **Height**: Altura em células (eixo Y)
- **Resolution**: Metros por célula (ex: 0.1m = 10cm por célula)
- **Origin**: Ponto de referência (x, y) no mundo

### Exemplo Visual

```
Mapa 2D (vista de cima):
┌─────────────────────────┐
│ -1 -1 -1 -1 -1 -1 -1    │  ← Desconhecido
│ -1  0  0  0  0  0 -1    │  ← Livre
│ -1  0  1  1  1  0 -1    │  ← Ocupado (obstáculo)
│ -1  0  0  0  0  0 -1    │  ← Livre
│ -1 -1 -1 -1 -1 -1 -1    │  ← Desconhecido
└─────────────────────────┘
```

## 📊 Dados Armazenados

O mapa salvo em JSON contém:

```json
{
  "width": 40,        // Células em X
  "height": 40,       // Células em Y
  "resolution": 0.1, // 10cm por célula
  "origin_x": -2,     // Origem X no mundo (metros)
  "origin_y": -2,     // Origem Y no mundo (metros)
  "occupancy": [...], // Matriz 2D: -1, 0, ou 1
  "coverage": [...],  // Matriz 2D: número de visitas
  "trajectory": [...] // Lista de pontos (x, y, yaw)
}
```

**Nota**: Não há dimensão Z ou altura armazenada.

## ✅ Verificação: Está Correto?

### ✅ SIM, está em 2D!

**Evidências:**

1. **Classe declara 2D**: `"""Mapa de ocupação 2D para mapeamento do ambiente"""`
2. **Apenas 2 dimensões**: `width` e `height` (sem `depth`)
3. **Funções usam apenas x, y**: `world_to_map(x, y)`, `update_occupancy(x, y, ...)`
4. **Trajetória 2D**: `trajectory.append((x, y, yaw))` - sem z
5. **Visualização 2D**: `scripts/visualizar_mapa.py` mostra vista de cima

### 🔄 Fluxo de Dados

```
PyBullet 3D                    Mapeamento 2D
─────────────────              ──────────────
Robô: (x, y, z)     →         Mapa: (x, y)
Sensores: 3D rays   →         Projeção: 2D
Obstáculos: 3D      →         Células: 2D grid
```

## 🎯 Comparação: 2D vs 3D

| Aspecto | 2D (Atual) | 3D (Alternativa) |
|---------|------------|------------------|
| **Dimensões** | X, Y | X, Y, Z |
| **Complexidade** | Baixa | Alta |
| **Processamento** | Rápido | Lento |
| **Memória** | Pouca | Muita |
| **Uso** | Robôs terrestres | Drones, robôs aéreos |
| **Padrão** | SLAM 2D (ROS) | SLAM 3D (mais raro) |

## 📈 Quando Usar 2D vs 3D?

### Use 2D quando:
- ✅ Robô se move no chão
- ✅ Altura dos obstáculos não importa
- ✅ Precisa de processamento rápido
- ✅ Navegação em ambientes planos

### Use 3D quando:
- ⚠️ Robô voa (drone)
- ⚠️ Precisa evitar obstáculos em altura
- ⚠️ Ambientes com múltiplos níveis
- ⚠️ Planejamento 3D necessário

## 🔧 Melhorias Possíveis (Opcional)

Se quiser melhorar o mapeamento 2D atual:

### 1. Altura Mínima dos Obstáculos

Atualmente, qualquer obstáculo em qualquer altura é marcado. Poderia filtrar:

```python
# Exemplo: só marcar obstáculos entre 0.1m e 1.5m de altura
if 0.1 <= obstacle_z <= 1.5:
    self.occupancy[map_y, map_x] = 1
```

### 2. Mapa de Altura (Opcional)

Adicionar um mapa separado para altura média:

```python
# Novo: mapa de altura média
self.height_map = np.zeros((height, width), dtype=np.float32)
```

### 3. Filtro de Ruído

Melhorar a qualidade do mapa 2D:

```python
# Aplicar filtro morfológico
from scipy import ndimage
self.occupancy = ndimage.binary_opening(self.occupancy)
```

## 📚 Referências

- **SLAM 2D**: Padrão usado em ROS (Robot Operating System)
- **Occupancy Grid Maps**: Formato padrão para robôs móveis
- **Projeção 3D→2D**: Técnica comum em visão computacional

## ✅ Conclusão

**Seu mapeamento JÁ está em 2D!** ✅

A simulação PyBullet é 3D, mas o mapeamento projeta corretamente tudo no plano horizontal (XY), que é o padrão para robôs terrestres. Isso está correto e alinhado com as práticas da indústria.

**Não é necessário mudar para 3D** a menos que você precise:
- Mapear múltiplos andares
- Evitar obstáculos em altura específica
- Navegar com drone

Para um robô aspirador terrestre, **2D é perfeito**! 🎯

