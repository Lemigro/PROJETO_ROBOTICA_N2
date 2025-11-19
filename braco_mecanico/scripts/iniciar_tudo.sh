#!/bin/bash

echo "========================================"
echo "  Iniciar Sistema Robótica N2"
echo "========================================"
echo

echo "[1/5] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python não encontrado!"
    echo "Instale Python de https://www.python.org/"
    exit 1
fi
python3 --version
echo "OK: Python encontrado"
echo

echo "[2/5] Verificando dependências Python..."
python3 -c "import pybullet" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Instalando dependências..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERRO ao instalar dependências"
        exit 1
    fi
fi
echo "OK: Dependências Python instaladas"
echo

echo "[3/5] Verificando Mosquitto..."
if ! command -v mosquitto &> /dev/null; then
    echo "AVISO: Mosquitto não encontrado"
    echo "Instale com: sudo apt-get install mosquitto mosquitto-clients"
    exit 1
fi

sudo systemctl start mosquitto 2>/dev/null
if [ $? -eq 0 ]; then
    echo "OK: Mosquitto iniciado"
else
    echo "AVISO: Não foi possível iniciar Mosquitto automaticamente"
    echo "Tente: sudo systemctl start mosquitto"
fi
echo

echo "[4/5] Verificando Node-RED..."
if ! command -v node-red &> /dev/null; then
    echo "AVISO: Node-RED não encontrado"
    read -p "Deseja instalar agora? (s/N): " install
    if [[ "$install" =~ ^[Ss]$ ]]; then
        bash instalar_node_red.sh
    else
        echo "Instale manualmente: npm install -g node-red node-red-dashboard"
    fi
else
    echo "OK: Node-RED encontrado"
    echo
    echo "Iniciando Node-RED em background..."
    node-red > /dev/null 2>&1 &
    sleep 3
    echo "Node-RED iniciado! Acesse: http://localhost:1880"
    echo
    echo "IMPORTANTE: Importe o arquivo node_red_flow_organizado.json no Node-RED"
fi
echo

echo "[5/5] Testando conexão MQTT..."
python3 testar_mqtt.py
if [ $? -ne 0 ]; then
    echo "AVISO: Teste MQTT falhou, mas continuando..."
fi
echo

echo "========================================"
echo "  Sistema Pronto!"
echo "========================================"
echo
echo "Próximos passos:"
echo "1. Acesse Node-RED: http://localhost:1880"
echo "2. Importe: node_red_flow_organizado.json"
echo "3. Acesse Dashboard: http://localhost:1880/ui"
echo "4. Execute os sistemas:"
echo "   - python3 exemplo_manipulador.py"
echo "   - python3 exemplo_robo_movel.py"
echo

