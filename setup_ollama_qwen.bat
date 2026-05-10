@echo off
echo ======================================================================
echo KUWERA QWEN - Ollama Setup
echo ======================================================================
echo.

REM Check if Ollama is installed
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Ollama tidak ditemukan!
    echo.
    echo Silakan install Ollama terlebih dahulu:
    echo 1. Buka https://ollama.com di browser
    echo 2. Download dan install Ollama untuk Windows
    echo 3. Jalankan kembali script ini setelah installasi
    echo.
    pause
    exit /b 1
)

echo [OK] Ollama ditemukan
echo.

REM Create temporary Modelfile
echo Creating Modelfile...
(
echo FROM ./models/llm/qwen2.5-1.5b-instruct-q4_k_m.gguf
echo.
echo TEMPLATE """{{ if .System }}^<|im_start|^>system
echo {{ .System }}^<|im_end|^>
echo {{ end }}{{ if .Prompt }}^<|im_start|^>user
echo {{ .Prompt }}^<|im_end|^>
echo {{ end }}^<|im_start|^>assistant
echo """
echo.
echo SYSTEM """Kamu adalah Kuwera, AI asisten cerdas dari Indonesia. Kamu memiliki akses ke data ekonomi Indonesia dan internasional. Jawablah dalam Bahasa Indonesia yang baik, benar, dan ramah."""
echo.
echo PARAMETER temperature 0.7
echo PARAMETER top_p 0.9
echo PARAMETER top_k 40
echo PARAMETER repeat_penalty 1.1
) > Modelfile

echo [OK] Modelfile created
echo.

REM Create model
echo Creating Kuwera-Qwen model...
ollama create kuera-qwen -f Modelfile
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Gagal membuat model!
    echo Pastikan model file ada di: models\llm\qwen2.5-1.5b-instruct-q4_k_m.gguf
    del Modelfile
    pause
    exit /b 1
)

echo [OK] Model kuera-qwen created successfully!
echo.

REM Cleanup
del Modelfile

REM Test model
echo Testing model...
echo "Halo, siapa kamu?" | ollama run kuera-qwen --verbose

echo.
echo ======================================================================
echo SETUP COMPLETE!
echo ======================================================================
echo.
echo Model Kuwera-Qwen sudah siap digunakan!
echo.
echo Cara menggunakan:
echo   1. Command line: ollama run kuera-qwen
echo   2. API: curl http://localhost:11434/api/generate -d ^
          "{\"model\": \"kuera-qwen\", \"prompt\": \"Halo\"}"
echo   3. Integrasi dengan Kuera Smart Chat
echo.
echo Contoh:
echo   ollama run kuera-qwen
echo   ^> Halo, apa kabar?
echo.
pause
