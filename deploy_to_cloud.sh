#!/bin/bash

echo "🚀 MAE Chatbot Cloud Deployment Script"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "web_app_cloud.py" ]; then
    echo "❌ Error: web_app_cloud.py not found. Please run from chatbot directory."
    exit 1
fi

# Initialize Git if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: MAE Chatbot System for Cloud Deployment"
fi

# Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 Please add your GitHub repository URL:"
    read -p "GitHub repository URL: " repo_url
    
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "✅ Remote origin added: $repo_url"
    else
        echo "❌ No repository URL provided. Please run:"
        echo "   git remote add origin https://github.com/你的用户名/mae-chatbot-system.git"
        exit 1
    fi
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Update: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

echo ""
echo "✅ Code pushed to GitHub successfully!"
echo ""
echo "🌐 Next steps:"
echo "1. Visit: https://share.streamlit.io"
echo "2. Click 'New app'"
echo "3. Connect your GitHub account"
echo "4. Select repository: mae-chatbot-system"
echo "5. Main file: web_app_cloud.py"
echo "6. Click 'Deploy'"
echo ""
echo "🎉 Your app will be available at:"
echo "   https://mae-chatbot-system-你的用户名.streamlit.app"
echo ""
echo "📱 Share this URL with anyone worldwide!"
