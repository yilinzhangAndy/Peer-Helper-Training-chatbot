#!/bin/bash

# MAE Chatbot Web App Startup Script
echo "🚀 Starting MAE Peer Advisor Training System..."

# Check if we're in the right directory
if [ ! -f "web_app.py" ]; then
    echo "❌ Error: web_app.py not found. Please run this script from the chatbot directory."
    exit 1
fi

# Activate chatbot environment
echo "🔧 Activating chatbot environment..."
source ~/miniforge3/etc/profile.d/conda.sh
conda activate chatbot

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing..."
    pip install streamlit
fi

# Start the web application
echo "🌐 Starting web application..."
echo "📍 Local URL: http://localhost:8501"
echo "📍 Network URL: http://192.168.0.36:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

streamlit run web_app.py --server.port 8501
