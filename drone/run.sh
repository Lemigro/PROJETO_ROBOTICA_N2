#!/bin/bash
# Script de execução rápida para Linux/Mac

echo "========================================"
echo "Drone de Entregas - Iniciando Simulação"
echo "========================================"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python não encontrado!"
    echo "Por favor, instale Python 3.8 ou superior."
    exit 1
fi

# Verificar se as dependências estão instaladas
python3 -c "import pybullet" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Dependências não encontradas. Instalando..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao instalar dependências!"
        exit 1
    fi
fi

# Executar simulação
echo "Iniciando simulação..."
python3 main.py

