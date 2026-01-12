#!/usr/bin/env python3
"""
测试 Hugging Face 模型部署状态

使用方法:
python test_model_deployment.py
"""

import os
import sys
from huggingface_hub import InferenceClient, HfApi

def test_model_deployment():
    """测试模型是否成功部署"""
    
    # 配置（从环境变量读取，不要硬编码 token）
    HF_TOKEN = os.getenv("HF_TOKEN", "")
    HF_MODEL = os.getenv("HF_MODEL", "zylandy/mae-intent-classifier")
    
    if not HF_TOKEN:
        print("❌ 请设置 HF_TOKEN 环境变量")
        print("   例如: export HF_TOKEN='your-token'")
        return False
    
    print("🧪 测试模型部署状态...")
    print("=" * 60)
    print(f"模型: {HF_MODEL}")
    print(f"Token: {HF_TOKEN[:20]}...")
    
    # 方法 1: 检查模型是否存在
    print(f"\n📋 方法 1: 检查模型仓库...")
    try:
        api = HfApi(token=HF_TOKEN)
        model_info = api.model_info(HF_MODEL, token=HF_TOKEN)
        print(f"✅ 模型仓库存在")
        print(f"   模型 ID: {model_info.id}")
        print(f"   最后更新: {model_info.last_modified}")
        
        # 列出文件
        files = [f.rfilename for f in model_info.siblings]
        print(f"\n📁 模型文件 ({len(files)} 个):")
        for file in sorted(files)[:10]:  # 只显示前10个
            print(f"   - {file}")
        if len(files) > 10:
            print(f"   ... 还有 {len(files) - 10} 个文件")
            
    except Exception as e:
        print(f"❌ 无法访问模型仓库: {e}")
        return False
    
    # 方法 2: 使用 InferenceClient 测试
    print(f"\n📤 方法 2: 使用 InferenceClient 测试...")
    try:
        client = InferenceClient(model=HF_MODEL, token=HF_TOKEN)
        
        test_text = "I want to learn about research opportunities"
        print(f"   测试文本: {test_text}")
        
        # 尝试文本分类
        try:
            result = client.text_classification(test_text)
            print(f"   ✅ 文本分类成功！")
            
            # 处理结果
            if isinstance(result, list):
                if result:
                    top = result[0] if isinstance(result[0], dict) else max(result, key=lambda x: x.get("score", 0.0))
                    if isinstance(top, dict):
                        label = top.get("label", "Unknown")
                        score = top.get("score", 0.0)
                        print(f"   📊 分类结果:")
                        print(f"      意图: {label}")
                        print(f"      置信度: {score:.3f}")
                    else:
                        print(f"   📊 结果: {top}")
            else:
                print(f"   📊 结果: {result}")
                
            print(f"\n✅ 模型部署成功并可以使用！")
            return True
            
        except Exception as e:
            print(f"   ⚠️  文本分类失败: {e}")
            print(f"   💡 提示: 模型可能正在加载，或需要使用不同的 API 方法")
            
            # 尝试其他方法
            try:
                print(f"\n   尝试使用 post 方法...")
                result = client.post(json={"inputs": test_text})
                print(f"   ✅ Post 方法成功！")
                print(f"   结果: {result}")
                return True
            except Exception as e2:
                print(f"   ❌ Post 方法也失败: {e2}")
                return False
                
    except Exception as e:
        print(f"❌ InferenceClient 初始化失败: {e}")
        return False

if __name__ == "__main__":
    success = test_model_deployment()
    sys.exit(0 if success else 1)
