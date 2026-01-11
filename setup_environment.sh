#!/bin/bash
# 环境设置脚本

echo "=" | cat
echo "🔧 设置Chatbot环境"
echo "=" | cat

# 激活chatbot环境
echo "📦 激活chatbot环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate chatbot

if [ $? -ne 0 ]; then
    echo "❌ 无法激活chatbot环境"
    echo "   请手动运行: conda activate chatbot"
    exit 1
fi

echo "✅ 环境已激活: $(which python)"
echo ""

# 检查并安装依赖
echo "📋 检查依赖..."
python -c "import streamlit" 2>/dev/null && echo "✅ streamlit已安装" || echo "⚠️ streamlit未安装"
python -c "import pandas" 2>/dev/null && echo "✅ pandas已安装" || echo "⚠️ pandas未安装"
python -c "import openpyxl" 2>/dev/null && echo "✅ openpyxl已安装" || echo "⚠️ openpyxl未安装"
python -c "import pdfplumber" 2>/dev/null && echo "✅ pdfplumber已安装" || echo "⚠️ pdfplumber未安装"

echo ""
echo "📦 安装缺失的依赖..."
pip install -r requirements.txt
pip install pdfplumber

echo ""
echo "✅ 环境设置完成！"
echo ""
echo "现在可以运行："
echo "  python extract_pdf_content.py"
echo "  python strategy_matrix.py"
echo "  streamlit run web_app_cloud_simple.py"
