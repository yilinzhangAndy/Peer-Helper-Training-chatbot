# 🔄 模型替换指南

## 📋 如何替换 Hugging Face 意图分类模型

当前系统使用 Hugging Face Inference API 进行意图分类。替换模型非常简单，只需要更新配置即可。

## 🎯 步骤 1: 准备新模型

确保你的新模型已经：
1. ✅ 上传到 Hugging Face Hub
2. ✅ 设置为公开（Public）或你有访问权限
3. ✅ 支持文本分类任务（Text Classification）
4. ✅ 返回格式为：`[{"label": "intent_name", "score": 0.95}, ...]`

## 🔧 步骤 2: 配置新模型

### 方法 1: Streamlit Cloud Secrets（推荐用于云端部署）

1. 访问 Streamlit Cloud Dashboard: https://share.streamlit.io/
2. 选择你的应用
3. 进入 **Settings** → **Secrets**
4. 添加或更新以下配置：

```toml
HF_MODEL = "your-username/your-new-model-name"
HF_TOKEN = "your-huggingface-token"
```

5. 保存并等待应用重新部署

### 方法 2: 本地配置（用于本地开发）

编辑 `.streamlit/secrets.toml` 文件：

```toml
HF_MODEL = "your-username/your-new-model-name"
HF_TOKEN = "your-huggingface-token"
```

### 方法 3: 环境变量

```bash
export HF_MODEL="your-username/your-new-model-name"
export HF_TOKEN="your-huggingface-token"
```

## 📝 步骤 3: 验证配置

替换后，系统会自动使用新模型。你可以通过以下方式验证：

1. **检查日志**：查看应用启动日志，确认模型加载成功
2. **测试分类**：发送一条消息，查看意图分类结果
3. **检查置信度**：观察新模型的置信度是否提高

## ⚠️ 重要注意事项

### 模型输出格式要求

新模型必须返回以下格式的 JSON：

```json
[
  {
    "label": "Goal Setting and Planning",
    "score": 0.95
  },
  {
    "label": "Understanding and Clarification",
    "score": 0.05
  }
]
```

### 意图标签要求

新模型的意图标签应该与系统期望的标签匹配：

- `Exploration and Reflection`
- `Feedback and Support`
- `Goal Setting and Planning`
- `Problem Solving and Critical Thinking`
- `Understanding and Clarification`

如果标签不同，需要修改 `web_app_cloud_simple.py` 中的 `hf_classify_via_api()` 函数来映射标签。

## 🔍 当前配置位置

- **代码位置**: `web_app_cloud_simple.py`
  - `_get_hf_model()`: 获取模型名称
  - `_get_hf_token()`: 获取 API token
  - `hf_classify_via_api()`: 调用模型 API

## 🐛 故障排除

### 问题 1: 模型未找到

**错误**: `Model not found` 或 `404 Not Found`

**解决**:
- 检查模型名称是否正确（格式：`username/model-name`）
- 确认模型是公开的或你有访问权限
- 检查 Hugging Face Hub 上的模型页面

### 问题 2: 认证失败

**错误**: `401 Unauthorized` 或 `Invalid token`

**解决**:
- 检查 `HF_TOKEN` 是否正确
- 确认 token 有读取权限
- 从 https://huggingface.co/settings/tokens 获取新 token

### 问题 3: 输出格式不匹配

**错误**: `Unexpected HF response format`

**解决**:
- 检查模型输出格式是否符合要求
- 可能需要修改 `hf_classify_via_api()` 函数来适配新格式

### 问题 4: 标签不匹配

**问题**: 模型返回的标签与系统期望的不同

**解决**:
- 修改 `hf_classify_via_api()` 函数，添加标签映射
- 或更新模型的标签以匹配系统期望

## 📚 相关文件

- `web_app_cloud_simple.py`: 主要应用文件，包含模型调用逻辑
- `.streamlit/secrets.toml`: 本地配置文件
- `README.md`: 项目文档

## 💡 提示

- 替换模型后，建议先在本地测试
- 确认新模型的准确率确实更高
- 保留旧模型配置作为备份
- 如果新模型有问题，可以快速切换回旧模型

## ✅ 完成检查清单

- [ ] 新模型已上传到 Hugging Face Hub
- [ ] 模型设置为公开或有访问权限
- [ ] 更新了 `HF_MODEL` 配置
- [ ] 确认 `HF_TOKEN` 有效
- [ ] 在本地测试新模型
- [ ] 验证意图分类结果
- [ ] 更新云端配置（如果使用 Streamlit Cloud）
- [ ] 测试云端部署
