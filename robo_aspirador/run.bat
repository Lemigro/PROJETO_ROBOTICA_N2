@echo off
REM Script de execução rápida do Robô Aspirador
REM Uso: run.bat [execução] [carregar-mapa]

setlocal

set EXECUTION=1
set LOAD_MAP=
set MAP_FILE=

if "%1" neq "" set EXECUTION=%1
if "%2" neq "" (
    set LOAD_MAP=--load-map
    set MAP_FILE=--map-file %2
)

echo ========================================
echo Robo Aspirador Inteligente
echo Execucao #%EXECUTION%
echo ========================================
echo.

if "%LOAD_MAP%" neq "" (
    echo Carregando mapa: %MAP_FILE%
    echo.
    python main.py --execution %EXECUTION% %LOAD_MAP% %MAP_FILE%
) else (
    python main.py --execution %EXECUTION%
)

echo.
echo ========================================
echo Execucao finalizada!
echo ========================================
pause

