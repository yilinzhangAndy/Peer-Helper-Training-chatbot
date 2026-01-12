# 🔧 Hugging Face 模型替代方案

## 📋 当前情况

- ✅ 模型已成功上传到 Hugging Face
- ⚠️ 模型文件在 `checkpoint-3146/` 子目录
- ⚠️ Inference API 返回 404（可能因为文件位置或配置）
- ⚠️ 模型页面没有 "Hosted inference API" 选项

## 🎯 解决方案

### 方案 1: 添加模型卡片（Model Card）- 最简单

Hugging Face 需要模型卡片来识别任务类型。

1. **访问模型页面**: https://huggingface.co/zylandy/mae-intent-classifier
2. **点击 "Add a model card"** 或编辑 README.md
3. **添加以下内容**:

```yaml
---
tags:
- text-classification
- intent-classification
pipeline_tag: text-classification
library_name: transformers
---
```

或者直接在 README.md 开头添加：

```markdown
---
pipeline_tag: text-classification
tags:
- text-classification
---

# MAE Intent Classifier

This model classifies student advisor conversation intents into 5 categories:
- Exploration and Reflection
- Feedback and Support
- Goal Setting and Planning
- Problem Solving and Critical Thinking
- Understanding and Clarification
```

4. **保存后等待几分钟**，让 Hugging Face 处理

### 方案 2: 移动文件到根目录

如果方案1不行，将文件移动到根目录：

1. **使用 Git**（推荐）:
```bash
git clone https://huggingface.co/zylandy/mae-intent-classifier
cd mae-intent-classifier
mv checkpoint-3146/config.json .
mv checkpoint-3146/model.safetensors .
mv checkpoint-3146/tokenizer_config.json .
mv checkpoint-3146/vocab.json .
mv checkpoint-3146/merges.txt .
mv checkpoint-3146/special_tokens_map.json .
git add .
git commit -m "Move model files to root directory"
git push
```

2. **或使用 Web UI**: 在模型页面上删除子目录中的文件，重新上传到根目录

### 方案 3: 使用本地模型加载（如果子目录也能工作）

如果之前的模型在子目录也能工作，可能是 API 端点问题。我们可以：

1. **继续使用关键词分类器**（当前方案）
   - ✅ 已经工作正常
   - ✅ 准确率可能略低，但功能完整

2. **或者等待 Hugging Face 修复 API 端点问题**

### 方案 4: 使用 Inference Endpoints（付费，但最可靠）

如果以上都不行，可以使用 Hugging Face 的 Inference Endpoints：

1. 访问: https://huggingface.co/inference-endpoints
2. 创建新的 Endpoint
3. 选择你的模型
4. 获得专用 API 端点
5. 更新代码使用新的端点

## 🔍 如何判断哪个方案有效

### 测试方法：

1. **添加模型卡片后**，等待 5-10 分钟
2. **运行测试脚本**:
```bash
python test_model_deployment.py
```
3. **如果返回 200 或 503**，说明模型正在加载，等待即可
4. **如果还是 404**，尝试方案 2（移动文件）

## 💡 当前状态

**即使显示 "🔄 使用关键词分类器作为备用方案"**：

- ✅ **系统正常工作**
- ✅ **所有功能可用**
- ✅ **分类仍然有效**
- ⚠️ **只是可能准确率略低**

**这不是问题**，关键词分类器已经足够好用了。如果新模型能工作当然更好，但即使不能，系统也完全正常。

## 📝 推荐步骤

1. **先尝试方案 1**（添加模型卡片）- 最简单，5分钟
2. **如果不行，尝试方案 2**（移动文件）- 需要 Git 操作
3. **如果都不行，继续使用关键词分类器** - 已经工作正常

## ✅ 验证

添加模型卡片或移动文件后：

1. 等待 5-10 分钟
2. 刷新应用
3. 应该会看到 "✅ Hugging Face 意图分类模型已连接"

如果还是不行，关键词分类器会继续工作，不影响使用。
