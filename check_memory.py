#!/usr/bin/env python3
"""检查内存是否足够加载模型"""

try:
    import psutil
    mem = psutil.virtual_memory()
    available_gb = mem.available / (1024**3)
    total_gb = mem.total / (1024**3)
    
    print("💾 内存检查结果:")
    print("=" * 60)
    print(f"总内存: {total_gb:.1f} GB")
    print(f"可用内存: {available_gb:.1f} GB")
    print(f"已使用: {(total_gb - available_gb):.1f} GB")
    print(f"\n模型需要: 约 1-2 GB 可用内存")
    
    if available_gb >= 2.0:
        print(f"\n✅ 内存充足！可以加载模型")
        print(f"   状态应该显示: 'Hugging Face 模型可用（将使用本地加载）'")
    elif available_gb >= 1.0:
        print(f"\n⚠️  内存可能不足")
        print(f"   可以尝试加载，但可能失败")
        print(f"   状态可能显示: '将尝试本地加载'")
    else:
        print(f"\n❌ 内存不足")
        print(f"   无法加载模型，将使用关键词分类器")
        print(f"   状态可能显示: '使用关键词分类器作为备用方案'")
        
except ImportError:
    print("⚠️  psutil 未安装，无法检查内存")
    print("   安装: pip install psutil")
    print("   或运行应用，查看日志中的内存信息")
except Exception as e:
    print(f"❌ 检查失败: {e}")

print(f"\n💡 提示:")
print(f"   - 刷新 Streamlit 应用后，会自动检查内存")
print(f"   - 查看应用启动时的日志输出")
print(f"   - 或查看状态消息（会显示内存是否足够）")
