# 💾 如何检查内存是否足够

## 🔍 自动检查

代码已经添加了自动内存检查功能。应用启动时会：

1. **检查可用内存**
2. **判断是否足够加载模型**（需要至少 2GB）
3. **显示相应的状态消息**

## 📊 状态说明

### ✅ "Hugging Face 模型可用（将使用本地加载）"
- **含义**: 内存充足（≥2GB），可以加载模型
- **操作**: 首次调用会自动加载模型
- **预期**: 模型会正常工作

### ℹ️ "将尝试本地加载"
- **含义**: 无法检查内存，或内存可能不足
- **操作**: 会尝试加载，如果失败会回退到关键词分类器
- **预期**: 如果内存不足，会看到错误信息

### ⏳ "Inference API 可能不可用"
- **含义**: API 不可用（模型太大），但可以尝试本地加载
- **操作**: 会尝试本地加载
- **预期**: 取决于可用内存

## 🧪 手动检查内存

### 方法 1: 在应用中查看日志

应用启动时，查看日志输出：
```
Memory: X.X GB available / Y.Y GB total
```

如果看到：
- **≥2 GB available**: ✅ 内存足够
- **<2 GB available**: ⚠️ 可能不足

### 方法 2: 运行测试脚本

创建文件 `check_memory.py`:

```python
import psutil

mem = psutil.virtual_memory()
available_gb = mem.available / (1024**3)
total_gb = mem.total / (1024**3)

print(f"总内存: {total_gb:.1f} GB")
print(f"可用内存: {available_gb:.1f} GB")
print(f"模型需要: 约 1-2 GB")

if available_gb >= 2.0:
    print("✅ 内存充足，可以加载模型")
else:
    print("⚠️ 内存可能不足，加载可能失败")
```

运行：
```bash
python check_memory.py
```

### 方法 3: 查看系统信息

**本地运行**:
```bash
# macOS/Linux
free -h  # Linux
vm_stat  # macOS

# 或使用 Python
python3 -c "import psutil; m=psutil.virtual_memory(); print(f'可用: {m.available/(1024**3):.1f} GB')"
```

**Streamlit Cloud**:
- 免费版: 通常只有 1GB 内存
- Pro 版: 有更多内存

## ⚠️ 如果内存不足

### 症状
- 看到 "Out of memory" 错误
- 模型加载失败
- 自动回退到关键词分类器

### 解决方案

1. **升级到 Streamlit Cloud Pro**（如果有预算）
2. **使用 Inference Endpoints**（付费服务）
3. **继续使用关键词分类器**（如果准确率可接受）
4. **优化模型大小**（量化、剪枝等）

## 📝 总结

- ✅ **代码已自动检查内存**
- ✅ **会显示相应的状态消息**
- ✅ **如果内存不足，会自动回退**
- ⚠️ **Streamlit Cloud 免费版可能内存不足**

**建议**: 刷新应用，查看显示的状态消息，就知道内存是否足够了！
