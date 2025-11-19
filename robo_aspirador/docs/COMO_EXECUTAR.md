# Como Executar o Projeto

## 🚀 Executar run.bat

### Opção 1: Duplo Clique (Mais Fácil)
1. Abra o explorador de arquivos
2. Navegue até a pasta `robo_aspirador`
3. **Duplo clique** no arquivo `run.bat`
4. A primeira execução será iniciada automaticamente

### Opção 2: Pelo Terminal/PowerShell
```bash
# Navegue até a pasta
cd "C:\Users\pedro.nascimento\Documents\PEDRON\PROJETOS_PESSOAIS\PROJETO_ROBOTICA_N2\robo_aspirador"

# Execute
.\run.bat 1
```

### Opção 3: Com Parâmetros
```bash
# Primeira execução
.\run.bat 1

# Segunda execução (com mapa)
.\run.bat 2 map_exec_1.json

# Terceira execução
.\run.bat 3 map_exec_2.json
```

## 📋 Sintaxe do run.bat

```
run.bat [número_execução] [arquivo_mapa]
```

**Exemplos:**
- `run.bat` → Executa execução #1 (padrão)
- `run.bat 1` → Executa execução #1
- `run.bat 2 map_exec_1.json` → Executa #2 carregando o mapa da execução 1
- `run.bat 3 map_exec_2.json` → Executa #3 carregando o mapa da execução 2

## 🎯 Alternativa: Python Direto

Se preferir usar Python diretamente:

```bash
# Primeira execução
python main.py --execution 1

# Segunda execução com aprendizado
python main.py --execution 2 --load-map --map-file map_exec_1.json
```

## ⚡ Dica Rápida

Crie um atalho na área de trabalho:
1. Clique direito em `run.bat`
2. "Criar atalho"
3. Arraste o atalho para a área de trabalho
4. Duplo clique para executar!

