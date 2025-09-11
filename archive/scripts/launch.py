#!/usr/bin/env python3
"""
MAE Peer Advisor Training System Launcher
Simple launcher script for the web application
"""

import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("🚀 MAE Peer Advisor Training System Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("web_app.py"):
        print("❌ Error: web_app.py not found.")
        print("Please run this script from the chatbot directory.")
        input("Press Enter to exit...")
        return
    
    # Check if streamlit is available
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
        print("✅ Streamlit installed successfully")
    
    print("\n🌐 Starting web application...")
    print("📍 Local URL: http://localhost:8501")
    print("📍 Network URL: http://192.168.0.36:8501")
    print("\n⏳ Please wait for the application to load...")
    print("🔄 The browser will open automatically in a few seconds...")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start streamlit in background
    try:
        # Open browser after a short delay
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:8501")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_app.py", 
            "--server.port", "8501"
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        print("Thank you for using MAE Peer Advisor Training System!")

if __name__ == "__main__":
    main()
