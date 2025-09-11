#!/bin/bash

echo "🚀 Starting MAE Chatbot with Llama 3.1..."
echo "=========================================="

# Activate chatbot environment
echo "🔧 Activating chatbot environment..."
source ~/miniforge3/etc/profile.d/conda.sh
conda activate chatbot

# Check if Ollama is running
echo "🦙 Checking Ollama service..."
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Starting Ollama service..."
    brew services start ollama
    sleep 3
fi

# Check if Llama model is available
echo "🧠 Checking Llama 3.1 model..."
if ! ollama list | grep -q "llama3.1:8b"; then
    echo "Downloading Llama 3.1 8B model..."
    ollama pull llama3.1:8b
fi

# Start the web application
echo "🌐 Starting web application..."
echo "📍 Local URL: http://localhost:8501"
echo "📍 Network URL: http://192.168.0.36:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

streamlit run web_app_llama.py --server.port 8501
