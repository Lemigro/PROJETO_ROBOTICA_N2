@echo off
echo ========================================
echo Instalacao do Node-RED e Dependencias
echo ========================================
echo.

echo [1/3] Verificando Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERRO: Node.js nao encontrado!
    echo Por favor, instale Node.js de https://nodejs.org/
    pause
    exit /b 1
)
echo Node.js encontrado!
echo.

echo [2/3] Instalando Node-RED...
call npm install -g node-red
if %errorlevel% neq 0 (
    echo ERRO ao instalar Node-RED
    pause
    exit /b 1
)
echo Node-RED instalado!
echo.

echo [3/3] Instalando node-red-dashboard...
call npm install -g node-red-dashboard
if %errorlevel% neq 0 (
    echo ERRO ao instalar dashboard
    pause
    exit /b 1
)
echo Dashboard instalado!
echo.

echo ========================================
echo Instalacao concluida!
echo ========================================
echo.
echo Para iniciar o Node-RED, execute:
echo   node-red
echo.
echo Depois acesse: http://localhost:1880
echo.
pause

