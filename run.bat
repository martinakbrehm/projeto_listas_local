@echo off
REM Script para executar o Gerador de Listas PF no Windows
REM Uso: run.bat

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Iniciando aplicação...
python app.py

pause