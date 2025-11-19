# 🚀 Quick Start - Robô Aspirador

## Instalação Rápida (3 passos)

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Testar
```bash
python tests/test_imports.py
```

### 3. Executar
```bash
python main.py --execution 1
```

## 📋 Comandos Principais

### Primeira Execução
```bash
python main.py --execution 1
```

### Execução com Aprendizado
```bash
python main.py --execution 2 --load-map --map-file map_exec_1.json
```

### Visualizar Mapa
```bash
python scripts/visualizar_mapa.py maps/map_exec_1.json
```

### Testar Node-RED
```bash
# 1. Iniciar Node-RED
node-red

# 2. Em outro terminal
python tests/test-node-red.py
```

## 🎯 Fluxo Completo

1. **Primeira Execução** → Gera `maps/map_exec_1.json`
2. **Visualizar** → `python scripts/visualizar_mapa.py maps/map_exec_1.json`
3. **Segunda Execução** → `python main.py --execution 2 --load-map --map-file map_exec_1.json`
4. **Comparar** → Visualize ambos os mapas

## ⚡ Script Rápido (Windows)

Use `run.bat`:
```bash
run.bat 1              # Primeira execução
run.bat 2 map_exec_1.json  # Segunda execução
```

## 📊 O que Esperar

- **Tempo**: 1-5 minutos por execução
- **Mapa**: Salvo em `maps/map_exec_N.json`
- **Visualização**: Imagem PNG gerada
- **Métricas**: Exibidas no console

## ❓ Problemas?

Consulte `docs/CONFIGURACAO.md` para ajustar parâmetros.

