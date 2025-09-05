@echo off
echo 🚀 Starting MAE Peer Advisor Training System...

REM Check if we're in the right directory
if not exist "web_app.py" (
    echo ❌ Error: web_app.py not found. Please run this script from the chatbot directory.
    pause
    exit /b 1
)

REM Activate chatbot environment
echo 🔧 Activating chatbot environment...
call conda activate chatbot

REM Check if streamlit is installed
streamlit --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit not found. Installing...
    pip install streamlit
)

REM Start the web application
echo 🌐 Starting web application...
echo 📍 Local URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ==================================

streamlit run web_app.py --server.port 8501
