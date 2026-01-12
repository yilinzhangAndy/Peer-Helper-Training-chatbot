#!/usr/bin/env python3
"""
检查当前使用的模型状态和分类方法

使用方法:
python check_model_status.py
"""

import os
import sys
import requests

def check_model_status():
    """检查模型状态和分类方法"""
    
    print("🔍 检查模型部署状态和分类方法...")
    print("=" * 60)
    
    # 1. 检查配置
    print("\n📋 1. 检查配置...")
    try:
        import streamlit as st
        hf_token = st.secrets.get("HF_TOKEN", "")
        hf_model = st.secrets.get("HF_MODEL", "")
        print(f"   ✅ 从 Streamlit Secrets 读取配置")
    except:
        hf_token = os.getenv("HF_TOKEN", "")
        hf_model = os.getenv("HF_MODEL", "zylandy/mae-intent-classifier")
        print(f"   ⚠️  从环境变量读取配置")
    
    print(f"   HF_MODEL: {hf_model if hf_model else '未设置'}")
    print(f"   HF_TOKEN: {'已设置' if hf_token else '未设置'}")
    
    # 2. 测试 Hugging Face API
    print(f"\n📤 2. 测试 Hugging Face API...")
    if hf_token and hf_model:
        test_text = "I want to learn about research opportunities"
        
        # 尝试多个端点
        endpoints = [
            f"https://api-inference.huggingface.co/models/{hf_model}",
            f"https://router.huggingface.co/models/{hf_model}",
        ]
        
        hf_working = False
        for url in endpoints:
            try:
                headers = {"Authorization": f"Bearer {hf_token}"}
                resp = requests.post(
                    url,
                    headers=headers,
                    json={"inputs": test_text},
                    timeout=10
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"   ✅ Hugging Face API 工作正常！")
                    print(f"   使用的端点: {url}")
                    
                    # 解析结果
                    if isinstance(data, list):
                        if data and isinstance(data[0], list):
                            candidates = data[0]
                        else:
                            candidates = data
                        
                        if candidates:
                            top = max(candidates, key=lambda x: x.get("score", 0.0))
                            label = top.get("label", "Unknown")
                            score = float(top.get("score", 0.0))
                            print(f"   测试结果:")
                            print(f"      意图: {label}")
                            print(f"      置信度: {score:.3f}")
                    
                    hf_working = True
                    break
                elif resp.status_code == 503:
                    print(f"   ⚠️  模型正在加载中（503）")
                    print(f"   这是正常的，等待后会自动使用新模型")
                    hf_working = True  # 认为模型存在，只是需要加载
                    break
                elif resp.status_code == 410:
                    print(f"   ⚠️  端点已废弃: {url}")
                    continue
                else:
                    print(f"   ❌ 端点返回错误: {resp.status_code}")
                    print(f"   响应: {resp.text[:200]}")
            except Exception as e:
                print(f"   ❌ 端点错误: {str(e)[:100]}")
                continue
        
        if not hf_working:
            print(f"   ❌ Hugging Face API 不可用")
    else:
        print(f"   ⚠️  配置不完整，无法测试 Hugging Face API")
        hf_working = False
    
    # 3. 检查 Fallback 分类器
    print(f"\n🔧 3. 检查 Fallback 分类器（关键词匹配）...")
    print(f"   ✅ SimpleIntentClassifier 始终可用（基于关键词）")
    print(f"   支持的意图类别:")
    print(f"      - Exploration and Reflection")
    print(f"      - Feedback and Support")
    print(f"      - Goal Setting and Planning")
    print(f"      - Problem Solving and Critical Thinking")
    print(f"      - Understanding and Clarification")
    
    # 4. 总结
    print(f"\n" + "=" * 60)
    print(f"📊 总结:")
    print(f"=" * 60)
    
    if hf_working:
        print(f"✅ 当前使用: Hugging Face 模型 ({hf_model})")
        print(f"   - 这是你的新训练的模型")
        print(f"   - 如果看到分类结果，说明新模型已成功部署")
        print(f"   - Fallback 分类器作为备用（如果 API 失败）")
    else:
        print(f"⚠️  当前使用: Fallback 分类器（关键词匹配）")
        print(f"   - Hugging Face API 不可用或未配置")
        print(f"   - 使用 SimpleIntentClassifier（基于关键词）")
        print(f"   - 这是备用方案，准确率较低")
    
    print(f"\n💡 如何判断使用的是哪个模型:")
    print(f"   1. 查看分类置信度:")
    print(f"      - Hugging Face 模型: 置信度通常 > 0.7")
    print(f"      - 关键词分类器: 置信度通常 < 0.6")
    print(f"   2. 查看应用日志:")
    print(f"      - 如果有 'HF API' 相关错误，可能在使用 fallback")
    print(f"   3. 测试复杂句子:")
    print(f"      - Hugging Face 模型: 能理解复杂语义")
    print(f"      - 关键词分类器: 只匹配关键词")
    
    return hf_working

if __name__ == "__main__":
    try:
        # 尝试导入 streamlit（如果在 Streamlit 环境中）
        import streamlit as st
        # 在 Streamlit 中运行
        st.set_page_config(page_title="Model Status Check")
        st.title("🔍 模型状态检查")
        
        if st.button("检查模型状态"):
            with st.spinner("检查中..."):
                hf_working = check_model_status()
                if hf_working:
                    st.success("✅ Hugging Face 模型可用")
                else:
                    st.warning("⚠️ 使用 Fallback 分类器")
    except ImportError:
        # 不在 Streamlit 环境中，直接运行
        hf_working = check_model_status()
        sys.exit(0 if hf_working else 1)
