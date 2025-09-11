#!/bin/bash

# Install Local LLM Options for MAE Chatbot
echo "🆓 Installing Free Local LLM Options..."

# Option 1: Ollama (推荐)
echo "📦 Option 1: Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    echo "Downloading Llama2 model (this may take a while)..."
    ollama pull llama2
    
    echo "✅ Ollama installed successfully!"
else
    echo "✅ Ollama already installed"
fi

# Option 2: Transformers with free models
echo "📦 Option 2: Installing Transformers..."
pip install transformers torch

# Option 3: Simple rule-based system (already implemented)
echo "📦 Option 3: Rule-based system (no installation needed)"

echo ""
echo "🎯 Available Free Options:"
echo "1. Ollama + Llama2: High quality, requires ~4GB RAM"
echo "2. Transformers: Medium quality, requires ~2GB RAM"  
echo "3. Rule-based: Basic quality, minimal resources"
echo ""
echo "To use Ollama, run: python web_app_free.py"
echo "To use rule-based, run: python web_app.py"
