@echo off
color 0a
echo ==========================================
echo   Initializing AI-Driven PQC Gateway
echo ==========================================

echo [1/3] Verifying Python Dependencies...
pip install -r requirements.txt

if not exist research_ai_model.pkl (
    echo [2/3] Random Forest Model missing. Beginning training sequence...
    python train_ai.py
) else (
    echo [2/3] Random Forest Model validated.
)

echo [3/3] Booting Flask Architecture...
timeout /t 2 /nobreak > NUL
start http://127.0.0.1:5000

python app.py
pause