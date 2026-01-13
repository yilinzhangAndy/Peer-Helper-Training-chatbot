# 🔧 API 配置指南

## UF LiteLLM API 配置

应用需要配置 UF LiteLLM API 才能使用 AI 生成学生回复。如果未配置，系统会自动使用本地 fallback 响应。

### 配置方法

#### 方法 1: 使用 Streamlit Secrets（推荐）

1. **创建 secrets 文件**
   ```bash
   mkdir -p .streamlit
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. **编辑 `.streamlit/secrets.toml`**
   ```toml
   UF_LITELLM_BASE_URL = "https://api.ai.it.ufl.edu"
   UF_LITELLM_API_KEY = "your-actual-api-key-here"
   ```

3. **重启 Streamlit 应用**

#### 方法 2: 使用环境变量

在启动应用前设置环境变量：

```bash
export UF_LITELLM_BASE_URL="https://api.ai.it.ufl.edu"
export UF_LITELLM_API_KEY="your-actual-api-key-here"
streamlit run web_app_cloud_simple.py
```

或者在 conda 环境中：

```bash
conda activate chatbot
export UF_LITELLM_BASE_URL="https://api.ai.it.ufl.edu"
export UF_LITELLM_API_KEY="your-actual-api-key-here"
streamlit run web_app_cloud_simple.py
```

#### 方法 3: 在代码中临时设置（仅用于测试）

⚠️ **不推荐用于生产环境**

在 `uf_navigator_api.py` 中，你可以临时传递参数：

```python
uf_api = UFNavigatorAPI(
    base_url="https://api.ai.it.ufl.edu",
    api_key="your-api-key"
)
```

### 获取 API Key

如果你没有 API key，请联系：
- **UF IT 部门**
- 或者查看 UF LiteLLM API 文档

### 验证配置

配置完成后，应用启动时会显示：
```
✅ UF LiteLLM client initialized (API will be used on demand).
```

如果配置不正确，会显示：
```
⚠️ UF LiteLLM client not ready. Check Streamlit secrets: UF_LITELLM_API_KEY / UF_LITELLM_BASE_URL.
🔄 Using fallback responses for student replies
```

### 使用 Fallback 模式

即使没有配置 API，应用仍然可以正常工作：
- ✅ 系统会自动使用本地 fallback 响应
- ✅ 所有功能都可以正常使用
- ⚠️ 学生回复将使用预设的模板，而不是 AI 生成

### 故障排除

1. **检查 secrets 文件位置**
   - 确保文件在 `.streamlit/secrets.toml`
   - 确保文件格式正确（TOML 格式）

2. **检查环境变量**
   ```bash
   echo $UF_LITELLM_API_KEY
   echo $UF_LITELLM_BASE_URL
   ```

3. **重启应用**
   - 修改配置后需要重启 Streamlit 应用

4. **查看错误信息**
   - 应用会显示具体的错误信息
   - 检查是否有拼写错误或格式问题
