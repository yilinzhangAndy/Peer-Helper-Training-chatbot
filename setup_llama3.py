#!/usr/bin/env python3
"""
Setup Llama 3.1 8B Instruct for MAE Chatbot
自动安装和配置 Llama 3.1 模型
"""

import subprocess
import sys
import os
import time

def check_ollama():
    """检查 Ollama 是否已安装"""
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def install_ollama():
    """安装 Ollama"""
    print("📦 Installing Ollama...")
    try:
        # 下载并安装 Ollama
        subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh"], 
                      check=True)
        subprocess.run(["sh", "-"], input="curl -fsSL https://ollama.ai/install.sh | sh", 
                      text=True, check=True)
        print("✅ Ollama installed successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to install Ollama: {e}")
        return False

def download_llama3():
    """下载 Llama 3.1 8B Instruct 模型"""
    print("🦙 Downloading Llama 3.1 8B Instruct model...")
    print("⏳ This may take 10-20 minutes depending on your internet speed...")
    
    try:
        # 下载模型
        result = subprocess.run(["ollama", "pull", "llama3.1:8b-instruct"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Llama 3.1 8B Instruct model downloaded successfully!")
            return True
        else:
            print(f"❌ Failed to download model: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False

def test_model():
    """测试模型是否正常工作"""
    print("🧪 Testing Llama 3.1 model...")
    
    test_prompt = "Hello, I'm a student. Can you help me with my studies?"
    
    try:
        result = subprocess.run([
            "ollama", "run", "llama3.1:8b-instruct", 
            f"Respond as a helpful peer advisor: {test_prompt}"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Model test successful!")
            print(f"Sample response: {result.stdout.strip()[:100]}...")
            return True
        else:
            print("❌ Model test failed")
            return False
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

def main():
    print("🚀 Setting up Llama 3.1 8B Instruct for MAE Chatbot")
    print("=" * 60)
    
    # Step 1: Check/Install Ollama
    if not check_ollama():
        print("Ollama not found. Installing...")
        if not install_ollama():
            print("❌ Failed to install Ollama. Please install manually:")
            print("   Visit: https://ollama.ai/download")
            return False
    else:
        print("✅ Ollama already installed")
    
    # Step 2: Download Llama 3.1 model
    if not download_llama3():
        print("❌ Failed to download model")
        return False
    
    # Step 3: Test model
    if not test_model():
        print("❌ Model test failed")
        return False
    
    print("\n🎉 Setup complete!")
    print("You can now use Llama 3.1 8B Instruct in your chatbot")
    print("\nNext steps:")
    print("1. Run: streamlit run web_app_llama.py")
    print("2. Enjoy free, high-quality AI responses!")
    
    return True

if __name__ == "__main__":
    main()
