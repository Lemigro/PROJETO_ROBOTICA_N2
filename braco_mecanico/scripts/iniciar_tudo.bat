@echo off
echo ========================================
echo   Iniciar Sistema Robótica N2
echo ========================================
echo.

echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Instale Python de https://www.python.org/
    pause
    exit /b 1
)
echo OK: Python encontrado
echo.

echo [2/5] Verificando dependencias Python...
python -c "import pybullet" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependencias...
    pip install -r config/requirements.txt
    if %errorlevel% neq 0 (
        echo ERRO ao instalar dependencias
        pause
        exit /b 1
    )
)
echo OK: Dependencias Python instaladas
echo.

echo [3/5] Verificando Mosquitto...
sc query mosquitto >nul 2>&1
if %errorlevel% neq 0 (
    echo AVISO: Mosquitto nao encontrado como servico
    echo Por favor, instale o Mosquitto de https://mosquitto.org/download/
    echo.
    echo Tentando iniciar manualmente...
    net start mosquitto 2>nul
    if %errorlevel% neq 0 (
        echo ERRO: Nao foi possivel iniciar o Mosquitto
        echo Por favor, inicie manualmente ou instale o Mosquitto
        pause
        exit /b 1
    )
) else (
    net start mosquitto >nul 2>&1
)
echo OK: Mosquitto rodando
echo.

echo [4/5] Verificando Node-RED...
node-red --version >nul 2>&1
if %errorlevel% neq 0 (
    echo AVISO: Node-RED nao encontrado
    echo Deseja instalar agora? (S/N)
    set /p install="> "
    if /i "%install%"=="S" (
        call instalar_node_red.bat
    ) else (
        echo Pule esta etapa e instale Node-RED manualmente
        echo npm install -g node-red node-red-dashboard
    )
) else (
    echo OK: Node-RED encontrado
    echo.
    echo Iniciando Node-RED em nova janela...
    start "Node-RED" cmd /k "node-red"
    timeout /t 3 >nul
    echo Node-RED iniciado! Acesse: http://localhost:1880
    echo.
    echo IMPORTANTE: Importe o arquivo node_red_flow_organizado.json no Node-RED
)
echo.

echo [5/5] Testando conexao MQTT...
python testar_mqtt.py
if %errorlevel% neq 0 (
    echo AVISO: Teste MQTT falhou, mas continuando...
)
echo.

echo ========================================
echo   Sistema Pronto!
echo ========================================
echo.
echo Próximos passos:
echo 1. Acesse Node-RED: http://localhost:1880
echo 2. Importe: node_red_flow_organizado.json
echo 3. Importe fluxo: node_red/node_red_flow_organizado.json
echo 4. Acesse Dashboard: http://localhost:1880/ui
echo 5. Execute os sistemas:
echo    - python examples/exemplo_manipulador.py
echo    - python examples/exemplo_robo_movel.py
echo.
pause

