# 📤 模型上传到 Hugging Face 指南

## 🎯 快速开始

### 方法 1: 使用自动上传脚本（推荐）

1. **安装依赖**
   ```bash
   pip install huggingface_hub transformers
   ```

2. **登录 Hugging Face**
   ```bash
   huggingface-cli login
   ```
   输入你的 Hugging Face token（从 https://huggingface.co/settings/tokens 获取）

3. **运行上传脚本**
   ```bash
   cd /Users/zhangyilin/Documents/UF/Ph.D/Chatbot/chatbot
   python upload_model_to_hf.py --repo-name mae-intent-classifier-v2
   ```

   或者指定完整参数：
   ```bash
   python upload_model_to_hf.py \
     --model-path ../pre-train/balanced_finetuned_model \
     --repo-name mae-intent-classifier-v2 \
     --username your-username \
     --private  # 如果不想公开
   ```

4. **验证模型结构（不上传）**
   ```bash
   python upload_model_to_hf.py --repo-name test --verify-only
   ```

### 方法 2: 手动上传（使用 Web UI）

1. **访问 Hugging Face Hub**
   - 登录 https://huggingface.co/
   - 点击右上角头像 → **New model**

2. **创建新模型仓库**
   - 填写模型名称（例如: `mae-intent-classifier-v2`）
   - 选择可见性（Public 或 Private）
   - 点击 **Create model**

3. **上传文件**
   - 在模型页面，点击 **Files and versions** 标签
   - 点击 **Add file** → **Upload file**
   - 上传以下文件：
     - `config.json`
     - `pytorch_model.bin` 或 `model.safetensors`
     - `tokenizer_config.json`
     - `vocab.json`
     - `merges.txt`
     - `label_mapping.json`（如果有）

### 方法 3: 使用 Python 代码上传

```python
from huggingface_hub import HfApi, create_repo
from pathlib import Path

# 初始化 API
api = HfApi()

# 创建仓库
repo_name = "your-username/mae-intent-classifier-v2"
create_repo(repo_id=repo_name, exist_ok=True)

# 上传文件夹
api.upload_folder(
    folder_path="../pre-train/balanced_finetuned_model",
    repo_id=repo_name,
    repo_type="model"
)
```

## 📋 模型文件检查清单

上传前确保模型文件夹包含：

### 必需文件
- ✅ `config.json` - 模型配置
- ✅ `pytorch_model.bin` 或 `model.safetensors` - 模型权重

### Tokenizer 文件（推荐）
- ✅ `tokenizer_config.json`
- ✅ `vocab.json`（RoBERTa）
- ✅ `merges.txt`（RoBERTa）

### 可选但推荐
- ✅ `label_mapping.json` - 标签映射（如果使用）
- ✅ `README.md` - 模型说明文档

## 🔧 配置更新

上传成功后，更新配置：

### Streamlit Cloud Secrets
```
HF_MODEL = "your-username/mae-intent-classifier-v2"
HF_TOKEN = "your-huggingface-token"
```

### 本地配置 (.streamlit/secrets.toml)
```toml
HF_MODEL = "your-username/mae-intent-classifier-v2"
HF_TOKEN = "your-huggingface-token"
```

## 🚀 更简单的部署方案

### 方案 1: 继续使用 Hugging Face Inference API（当前方案）

**优点：**
- ✅ 无需服务器
- ✅ 自动扩展
- ✅ 免费额度充足
- ✅ 简单配置

**缺点：**
- ⚠️ 首次调用可能较慢（冷启动）
- ⚠️ 需要网络连接

**适用场景：** 当前方案，适合大多数情况

### 方案 2: 本地部署模型（最快）

**优点：**
- ✅ 响应最快
- ✅ 无需网络
- ✅ 完全控制

**缺点：**
- ⚠️ 需要服务器资源
- ⚠️ 需要管理模型文件
- ⚠️ 部署较复杂

**实现方式：**
```python
# 在 web_app_cloud_simple.py 中直接加载本地模型
from models.intent_classifier import IntentClassifier

# 加载模型（只需一次）
intent_classifier = IntentClassifier("../pre-train/balanced_finetuned_model")

# 使用
result = intent_classifier.classify(text)
```

### 方案 3: 使用其他云服务

**选项：**
- **AWS SageMaker**: 企业级，功能强大
- **Google Cloud AI Platform**: 集成好
- **Azure ML**: 微软生态
- **Replicate**: 简单易用，按需付费

## 💡 推荐方案

**对于你的情况，我推荐：**

1. **短期（最简单）**: 继续使用 Hugging Face Inference API
   - 上传新模型到 HF
   - 更新 `HF_MODEL` 配置
   - 无需修改代码

2. **中期（如果需要更快响应）**: 本地部署
   - 在 Streamlit Cloud 上直接加载模型
   - 需要处理模型文件大小限制

3. **长期（如果需要更多控制）**: 考虑专用推理服务

## 🐛 常见问题

### Q: 上传失败，提示 "Repository not found"
**A:** 确保已登录：`huggingface-cli login`

### Q: 上传很慢
**A:** 模型文件较大，这是正常的。可以：
- 使用 `model.safetensors` 格式（更小）
- 压缩模型（量化）

### Q: 如何测试上传的模型？
**A:** 
```python
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="your-username/mae-intent-classifier-v2",
    tokenizer="your-username/mae-intent-classifier-v2"
)

result = classifier("I want to learn about research opportunities")
print(result)
```

### Q: 模型太大，上传失败
**A:** 
- 检查文件大小（HF 免费账户有 10GB 限制）
- 考虑使用模型量化
- 或使用 Git LFS

## 📚 相关资源

- [Hugging Face Hub 文档](https://huggingface.co/docs/hub)
- [模型上传指南](https://huggingface.co/docs/hub/models-uploading)
- [Inference API 文档](https://huggingface.co/docs/api-inference)
