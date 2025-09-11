#!/bin/bash

# MAE Chatbot Deployment Update Script
echo "🔄 Updating MAE Chatbot Deployment..."

# Check if we're in the right directory
if [ ! -f "web_app.py" ]; then
    echo "❌ Error: web_app.py not found. Please run from chatbot directory."
    exit 1
fi

# Get update message
read -p "📝 Enter update message: " update_message

# Add all changes
echo "📦 Adding changes..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "$update_message"

# Push to main branch (triggers auto-deployment)
echo "🚀 Pushing to cloud..."
git push origin main

echo "✅ Update complete!"
echo "🌐 Your app will be updated in 1-3 minutes"
echo "📍 Check your deployment URL for the latest version"
