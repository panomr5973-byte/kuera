@echo off
chcp 65001 >nul
echo ===========================================
echo KUWERA AI - Bartowski Model Downloader
echo ===========================================
echo.
echo This will download 4 models from bartowski collection:
echo 1. Qwen2.5-Coder-3B-Instruct (2.0 GB)
echo 2. Qwen2.5-7B-Instruct (4.4 GB)
echo 3. Meta-Llama-3.1-8B-Instruct (4.9 GB)
echo 4. Llama-3.2-3B-Instruct (2.0 GB)
echo.
echo Total: ~13 GB
echo Destination: models\llm\
echo ===========================================
echo.

set /p choice="Download which model? (1-4, or 'all'): "

if "%choice%"=="1" goto model1
if "%choice%"=="2" goto model2
if "%choice%"=="3" goto model3
if "%choice%"=="4" goto model4
if "%choice%"=="all" goto all

echo Invalid choice
goto end

:model1
echo Downloading Qwen2.5-Coder-3B-Instruct...
huggingface-cli download bartowski/Qwen2.5-Coder-3B-Instruct-GGUF Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf --local-dir models\llm --resume-download
goto complete

:model2
echo Downloading Qwen2.5-7B-Instruct...
huggingface-cli download bartowski/Qwen2.5-7B-Instruct-GGUF Qwen2.5-7B-Instruct-Q4_K_M.gguf --local-dir models\llm --resume-download
goto complete

:model3
echo Downloading Meta-Llama-3.1-8B-Instruct...
huggingface-cli download bartowski/Meta-Llama-3.1-8B-Instruct-GGUF Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf --local-dir models\llm --resume-download
goto complete

:model4
echo Downloading Llama-3.2-3B-Instruct...
huggingface-cli download bartowski/Llama-3.2-3B-Instruct-GGUF Llama-3.2-3B-Instruct-Q4_K_M.gguf --local-dir models\llm --resume-download
goto complete

:all
echo Downloading all 4 models (this will take a while)...
echo.
echo [1/4] Qwen2.5-Coder-3B-Instruct...
huggingface-cli download bartowski/Qwen2.5-Coder-3B-Instruct-GGUF Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf --local-dir models\llm --resume-download
echo.
echo [2/4] Qwen2.5-7B-Instruct...
huggingface-cli download bartowski/Qwen2.5-7B-Instruct-GGUF Qwen2.5-7B-Instruct-Q4_K_M.gguf --local-dir models\llm --resume-download
echo.
echo [3/4] Meta-Llama-3.1-8B-Instruct...
huggingface-cli download bartowski/Meta-Llama-3.1-8B-Instruct-GGUF Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf --local-dir models\llm --resume-download
echo.
echo [4/4] Llama-3.2-3B-Instruct...
huggingface-cli download bartowski/Llama-3.2-3B-Instruct-GGUF Llama-3.2-3B-Instruct-Q4_K_M.gguf --local-dir models\llm --resume-download
goto complete

:complete
echo.
echo ===========================================
echo Download process completed!
echo Run 'python integrate_bartowski_models.py' to update registry
echo ===========================================

:end
echo.
pause
