#!/bin/bash

echo "========================================"
echo "Instalação do Node-RED e Dependências"
echo "========================================"
echo

echo "[1/3] Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERRO: Node.js não encontrado!"
    echo "Por favor, instale Node.js de https://nodejs.org/"
    exit 1
fi
node --version
echo "Node.js encontrado!"
echo

echo "[2/3] Instalando Node-RED..."
npm install -g node-red
if [ $? -ne 0 ]; then
    echo "ERRO ao instalar Node-RED"
    exit 1
fi
echo "Node-RED instalado!"
echo

echo "[3/3] Instalando node-red-dashboard..."
npm install -g node-red-dashboard
if [ $? -ne 0 ]; then
    echo "ERRO ao instalar dashboard"
    exit 1
fi
echo "Dashboard instalado!"
echo

echo "========================================"
echo "Instalação concluída!"
echo "========================================"
echo
echo "Para iniciar o Node-RED, execute:"
echo "  node-red"
echo
echo "Depois acesse: http://localhost:1880"
echo

