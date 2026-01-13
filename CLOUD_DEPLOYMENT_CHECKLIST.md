# ☁️ 云端部署检查清单

## ✅ 已完成的配置

### 代码功能
- ✅ 本地模型加载功能已实现
- ✅ 内存检查功能已实现
- ✅ 自动降级到关键词分类器（如果内存不足）
- ✅ 状态检测和显示已优化

### 依赖文件
- ✅ `requirements.txt` 包含所有必需依赖：
  - transformers
  - torch
  - huggingface_hub
  - psutil

### 配置文件
- ✅ `.gitignore` 已更新，排除大文件
- ✅ 代码已推送到 GitHub

## 🚀 云端部署流程

### 1. Streamlit Cloud 自动部署
- ✅ 代码推送到 GitHub 后，Streamlit Cloud 会自动：
  1. 检测到新的提交
  2. 开始重新部署（1-3分钟）
  3. 安装 `requirements.txt` 中的依赖
  4. 运行 `web_app_cloud_simple.py`

### 2. 首次运行
- 📥 应用启动时：
  1. 检查 Hugging Face 配置（HF_TOKEN, HF_MODEL）
  2. 测试 Inference API（可能返回 404，因为模型太大）
  3. 检查内存是否足够
  4. 显示相应的状态消息

### 3. 首次调用模型
- 🚀 用户发送第一条消息时：
  1. 代码尝试本地加载模型
  2. 从 Hugging Face 下载模型（约 500MB）
  3. 检查内存是否足够
  4. 如果足够，加载模型；如果不足，使用关键词分类器

## 📊 如何检查云端是否成功

### 方法 1: 查看状态消息
刷新应用后，应该看到以下之一：

**如果内存充足（≥2GB）**：
```
✅ Hugging Face 模型可用（将使用本地加载）
```

**如果内存不足或无法检查**：
```
ℹ️ 将尝试本地加载。如果内存不足，将使用关键词分类器。
```

**如果完全失败**：
```
🔄 使用关键词分类器作为备用方案
```

### 方法 2: 查看应用日志
在 Streamlit Cloud Dashboard：
1. 点击 "Manage app"
2. 查看 "Logs" 标签
3. 查找以下信息：
   - `🔄 Loading model locally: zylandy/mae-intent-classifier`
   - `Memory: X.X GB available / Y.Y GB total`
   - `✅ Model loaded successfully` 或 `⚠️ Insufficient memory`

### 方法 3: 测试分类
发送一条消息，查看：
- **如果使用模型**：置信度通常 > 0.7
- **如果使用关键词分类器**：置信度通常 < 0.6

## ⚠️ 可能的问题

### 问题 1: 内存不足
**症状**：
- 状态显示 "将尝试本地加载"
- 日志显示 "Insufficient memory"
- 自动使用关键词分类器

**解决方案**：
- 升级到 Streamlit Cloud Pro（有更多内存）
- 或继续使用关键词分类器（功能完整）

### 问题 2: 下载失败
**症状**：
- 日志显示网络错误
- 模型加载失败

**解决方案**：
- 检查网络连接
- 重试（模型会缓存，后续会更快）

### 问题 3: 依赖安装失败
**症状**：
- 应用无法启动
- 日志显示导入错误

**解决方案**：
- 检查 `requirements.txt` 是否正确
- 确保所有依赖都已列出

## 📝 总结

- ✅ **代码已准备好**：所有功能已实现
- ✅ **依赖已配置**：requirements.txt 完整
- ✅ **已推送到 GitHub**：Streamlit Cloud 会自动部署
- ⏳ **等待部署**：1-3 分钟后刷新应用
- 🔍 **检查状态**：查看状态消息和日志

**下一步**：
1. 等待 Streamlit Cloud 自动部署（1-3分钟）
2. 刷新应用
3. 查看状态消息
4. 测试模型是否可用
