# Guia Rápido - Robô Aspirador

## Instalação Rápida

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Testar importações:**
```bash
python test_imports.py
```

## Executar a Simulação

### Primeira Execução (Exploração)
```bash
python main.py --execution 1
```

### Execuções Subsequentes (Com Aprendizado)
```bash
# Segunda execução (carrega mapa da primeira)
python main.py --execution 2 --load-map --map-file map_exec_1.json

# Terceira execução (carrega mapa da segunda)
python main.py --execution 3 --load-map --map-file map_exec_2.json
```

### Sem Interface Gráfica (Mais Rápido)
```bash
python main.py --no-gui --execution 1
```

## O que Esperar

1. **Janela do PyBullet** abrirá mostrando:
   - Ambiente com obstáculos (paredes e caixas)
   - Robô azul navegando
   - Sensores detectando obstáculos

2. **Console** mostrará:
   - Progresso da simulação
   - Métricas em tempo real (cobertura, energia, colisões)
   - Estatísticas finais ao terminar

3. **Arquivos Gerados:**
   - `map_exec_N.json` - Mapa salvo após cada execução

## Controles

- **Fechar a janela** ou **Ctrl+C** para parar a simulação
- A simulação para automaticamente quando:
  - 95% da área é coberta
  - Tempo máximo (5 minutos) é atingido

## Troubleshooting

### PyBullet não abre
- Verifique drivers gráficos
- Tente `--no-gui` para modo headless

### Erro de importação
- Execute: `pip install -r requirements.txt`
- Verifique se está no diretório correto

### Node-RED não recebe dados
- Isso é normal! O sistema funciona sem Node-RED
- Para usar Node-RED, configure um endpoint HTTP em `http://localhost:1880/robot-logs`

## Próximos Passos

1. Execute múltiplas vezes para ver o aprendizado
2. Compare os mapas gerados (`map_exec_*.json`)
3. Observe a melhoria de eficiência entre execuções
4. Configure Node-RED para visualização avançada (opcional)

