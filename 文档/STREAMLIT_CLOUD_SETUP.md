# ☁️ Streamlit Cloud 配置指南

## 本地 vs 云端配置

### ✅ 本地版本（已配置成功）
- **位置**: `.streamlit/secrets.toml` 文件
- **状态**: ✅ 已配置并测试通过
- **URL**: http://localhost:8501

### ⚠️ 云端版本（需要配置）
- **位置**: Streamlit Cloud Dashboard
- **状态**: 需要手动配置
- **URL**: https://peer-apper-training-chatbot-an46q5yl8sqbcyqchwgnin.streamlit.app/

## 配置云端 Secrets 的步骤

### 方法 1: 通过 Streamlit Cloud Dashboard（推荐）

1. **登录 Streamlit Cloud**
   - 访问 https://share.streamlit.io/
   - 使用你的 GitHub 账号登录

2. **找到你的应用**
   - 在 Dashboard 中找到 "peer-apper-training-chatbot" 应用
   - 点击应用名称进入设置

3. **打开 Secrets 设置**
   - 点击左侧菜单的 **"Settings"** 或 **"⚙️ Settings"**
   - 找到 **"Secrets"** 部分
   - 点击 **"Edit secrets"** 或 **"Open secrets editor"**

4. **添加 Secrets**
   在编辑器中添加以下内容（TOML 格式）：
   ```toml
   UF_LITELLM_BASE_URL = "https://api.ai.it.ufl.edu"
   UF_LITELLM_API_KEY = "sk-FEhqmwbGafXtX9sv07rZLw"
   ```

5. **保存并重新部署**
   - 点击 **"Save"** 保存配置
   - Streamlit Cloud 会自动重新部署应用
   - 等待部署完成（通常需要 1-2 分钟）

6. **验证配置**
   - 访问云端应用 URL
   - 应该看到：`✅ UF LiteLLM client initialized`
   - 而不是错误消息

### 方法 2: 通过 GitHub Secrets（如果使用 GitHub Actions）

如果你使用 GitHub Actions 部署，可以在 GitHub Repository Settings 中配置：

1. 进入 GitHub Repository
2. Settings → Secrets and variables → Actions
3. 添加以下 Secrets：
   - `UF_LITELLM_BASE_URL`: `https://api.ai.it.ufl.edu`
   - `UF_LITELLM_API_KEY`: `sk-FEhqmwbGafXtX9sv07rZLw`

## 配置后的验证

### 本地版本验证（已完成 ✅）
```
✅ models.list() OK, found 17 models
✅ chat.completions OK
🎉 All tests passed! API is working correctly.
```

### 云端版本验证（配置后检查）
访问云端应用，应该看到：
- ✅ `UF LiteLLM client initialized (API will be used on demand).`
- ✅ 可以使用 AI 生成学生回复
- ❌ 不再显示 "UF LiteLLM client not ready" 错误

## 重要提示

### 安全注意事项
- ⚠️ **不要**在代码中硬编码 API key
- ⚠️ **不要**将 secrets.toml 提交到 git（已在 .gitignore 中）
- ✅ 使用 Streamlit Cloud 的 Secrets 功能
- ✅ API key 只存储在 Streamlit Cloud 的加密存储中

### 配置位置对比

| 配置位置 | 本地版本 | 云端版本 |
|---------|---------|---------|
| 配置文件 | `.streamlit/secrets.toml` | Streamlit Cloud Dashboard |
| 访问方式 | 本地文件系统 | Web Dashboard |
| 安全性 | 本地文件（需保护） | 云端加密存储 |
| 更新方式 | 编辑文件 + 重启 | Dashboard 编辑 + 自动部署 |

## 故障排除

### 如果云端配置后仍然显示错误：

1. **检查 Secrets 格式**
   - 确保是 TOML 格式
   - 确保没有多余的空格或引号
   - 确保 key 名称正确（`UF_LITELLM_BASE_URL` 和 `UF_LITELLM_API_KEY`）

2. **检查部署状态**
   - 在 Streamlit Cloud Dashboard 查看部署日志
   - 确保没有部署错误

3. **等待重新部署**
   - 保存 Secrets 后，应用会自动重新部署
   - 等待 1-2 分钟后再检查

4. **清除浏览器缓存**
   - 有时需要清除浏览器缓存才能看到更新

## 当前状态总结

- ✅ **本地版本**: 已配置并测试通过
- ⚠️ **云端版本**: 需要在 Streamlit Cloud Dashboard 中配置 Secrets

配置完成后，两个版本都应该能正常使用 UF LiteLLM API！
