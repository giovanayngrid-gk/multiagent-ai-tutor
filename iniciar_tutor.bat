@echo off
title Inicializador - Tutor Multiagente
color 0A

echo ======================================================
echo    INICIANDO AMBIENTE DO TUTOR MULTIAGENTE
echo ======================================================
echo.

:: 1. Finaliza eventuais processos anteriores do Ollama
echo [1/4] Limpando processos antigos...
taskkill /F /IM ollama.exe /T >nul 2>&1
taskkill /F /IM ollama_app.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

:: 2. Configura as variaveis para forcar execucao via CPU
echo [2/4] Configurando execucao por CPU...
set CUDA_VISIBLE_DEVICES=-1
set OLLAMA_LLM_LIBRARY=cpu

:: 3. Inicia o servidor do Ollama em uma janela separada em segundo plano
echo [3/4] Iniciando servico do Ollama...
start "Ollama Server (CPU)" /min cmd /c "set CUDA_VISIBLE_DEVICES=-1&& set OLLAMA_LLM_LIBRARY=cpu&& ollama serve"
timeout /t 4 /nobreak >nul

:: 4. Acessa a pasta do projeto, ativa a venv e roda o Streamlit
echo [4/4] Iniciando a interface Streamlit...
cd /d "C:\Users\giova\Downloads\tutor_multiagente"

call ".\venv_limpa\Scripts\activate.bat"
streamlit run app-edu.py

pause