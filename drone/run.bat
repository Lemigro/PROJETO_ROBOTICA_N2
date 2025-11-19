@echo off
REM Script de execução rápida para Windows
echo ========================================
echo Drone de Entregas - Iniciando Simulacao
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python 3.8 ou superior.
    pause
    exit /b 1
)

REM Verificar se as dependências estão instaladas
python -c "import pybullet" >nul 2>&1
if errorlevel 1 (
    echo Dependencias nao encontradas. Instalando...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERRO: Falha ao instalar dependencias!
        pause
        exit /b 1
    )
)

REM Executar simulação
echo Iniciando simulacao...
python main.py

pause

