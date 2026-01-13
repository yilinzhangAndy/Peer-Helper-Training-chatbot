# 🔧 Streamlit Cloud Secrets 配置故障排除

## 为什么本地可以修改，但云端修改不过来？

### 常见原因

1. **Secrets 格式错误** ❌
2. **Secrets 名称拼写错误** ❌
3. **没有保存或重新部署** ❌
4. **配置位置不对** ❌
5. **缓存问题** ❌

## 详细配置步骤（带截图说明）

### 步骤 1: 找到正确的配置位置

**重要**: Streamlit Cloud 的 Secrets 配置在 **Dashboard** 中，不是在代码仓库中！

1. 访问 https://share.streamlit.io/
2. 登录你的账号
3. 找到你的应用：`peer-apper-training-chatbot`
4. 点击应用名称（不是代码链接）

### 步骤 2: 打开 Settings

在应用详情页面：
- 点击左侧菜单的 **"⚙️ Settings"** 或 **"Settings"**
- **不要**点击 "Edit source code" 或 "View source code"

### 步骤 3: 找到 Secrets 编辑器

在 Settings 页面中：
- 向下滚动找到 **"Secrets"** 部分
- 点击 **"Edit secrets"** 或 **"Open secrets editor"**
- 会打开一个文本编辑器

### 步骤 4: 正确配置 Secrets

**⚠️ 重要：必须是 TOML 格式，不要有多余的引号或格式**

**正确格式** ✅：
```toml
UF_LITELLM_BASE_URL = "https://api.ai.it.ufl.edu"
UF_LITELLM_API_KEY = "sk-FEhqmwbGafXtX9sv07rZLw"
```

**错误格式** ❌：
```toml
# 错误 1: 多余的空格或格式
UF_LITELLM_BASE_URL="https://api.ai.it.ufl.edu"  # 缺少空格
"UF_LITELLM_API_KEY" = "sk-FEhqmwbGafXtX9sv07rZLw"  # key 不应该有引号

# 错误 2: 拼写错误
UF_LITELLM_BASE_URL = "https://api.ai.it.ufl.edu"  # 正确
UF_LITELLM_BASE_UR = "https://api.ai.it.ufl.edu"  # 错误：少了一个 L

# 错误 3: 大小写错误
uf_litellm_api_key = "sk-FEhqmwbGafXtX9sv07rZLw"  # 错误：应该是大写
UF_LITELLM_API_KEY = "sk-FEhqmwbGafXtX9sv07rZLw"  # 正确
```

### 步骤 5: 保存并验证

1. **点击 "Save" 按钮**（通常在编辑器底部或右上角）
2. **等待自动重新部署**（通常需要 1-2 分钟）
3. **查看部署状态**：
   - 在 Dashboard 中查看 "Deployments" 或 "Activity"
   - 应该看到新的部署正在进行
   - 等待部署完成（状态变为 "Running"）

### 步骤 6: 清除缓存并测试

1. **清除浏览器缓存**：
   - Chrome/Edge: `Ctrl+Shift+Delete` (Windows) 或 `Cmd+Shift+Delete` (Mac)
   - 选择 "Cached images and files"
   - 点击 "Clear data"

2. **硬刷新页面**：
   - Windows: `Ctrl+F5`
   - Mac: `Cmd+Shift+R`

3. **访问应用并检查**：
   - 应该看到：`✅ UF LiteLLM client initialized`
   - 不应该看到：`⚠️ UF LiteLLM client not ready`

## 验证 Secrets 是否配置成功

### 方法 1: 在应用中添加调试代码（临时）

在 `web_app_cloud_simple.py` 的初始化部分添加：

```python
# 临时调试代码（配置成功后删除）
if st.sidebar.button("🔍 Debug Secrets"):
    st.write("### Secrets 检查")
    try:
        st.write(f"UF_LITELLM_BASE_URL: {st.secrets.get('UF_LITELLM_BASE_URL', 'NOT FOUND')}")
        st.write(f"UF_LITELLM_API_KEY: {'已设置' if st.secrets.get('UF_LITELLM_API_KEY') else '未设置'}")
    except Exception as e:
        st.error(f"读取 Secrets 失败: {e}")
```

### 方法 2: 检查应用日志

在 Streamlit Cloud Dashboard 中：
1. 点击 "Logs" 或 "View logs"
2. 查找错误信息
3. 如果看到 "API key not provided"，说明 Secrets 没有正确配置

## 常见错误和解决方案

### 错误 1: "API key not provided"

**原因**: Secrets 没有配置或名称错误

**解决**:
1. 检查 Secrets 名称是否完全匹配：`UF_LITELLM_API_KEY`（大小写敏感）
2. 确保在 Streamlit Cloud Dashboard 中配置，不是在代码中
3. 保存后等待重新部署

### 错误 2: "Base URL not provided"

**原因**: `UF_LITELLM_BASE_URL` 没有配置

**解决**:
1. 确保两个 Secrets 都配置了
2. 检查格式是否正确

### 错误 3: Secrets 配置了但应用还是显示错误

**原因**: 
- 缓存问题
- 没有重新部署
- Secrets 格式错误

**解决**:
1. 清除浏览器缓存
2. 检查部署日志，确保重新部署成功
3. 验证 Secrets 格式（使用上面的正确格式）

### 错误 4: 找不到 Secrets 编辑器

**原因**: 可能在不同的位置

**解决**:
1. 在应用详情页，查找 "Settings" 或 "⚙️" 图标
2. 或者点击应用名称旁边的三个点 "..." → "Settings"
3. 在 Settings 页面查找 "Secrets" 部分

## 本地 vs 云端配置对比

| 项目 | 本地版本 | 云端版本 |
|------|---------|---------|
| 配置文件 | `.streamlit/secrets.toml` | Streamlit Cloud Dashboard |
| 文件位置 | 项目目录下 | 云端服务器（不可见） |
| 编辑方式 | 直接编辑文件 | Web Dashboard 编辑器 |
| 生效方式 | 重启应用 | 自动重新部署 |
| 验证方式 | 查看文件内容 | 查看应用状态 |

## 快速检查清单

配置云端 Secrets 前，确认：

- [ ] 已登录 Streamlit Cloud Dashboard
- [ ] 找到了正确的应用
- [ ] 打开了 Settings → Secrets 编辑器
- [ ] Secrets 格式正确（TOML 格式）
- [ ] 两个 Secrets 都配置了：
  - [ ] `UF_LITELLM_BASE_URL`
  - [ ] `UF_LITELLM_API_KEY`
- [ ] 点击了 "Save" 按钮
- [ ] 等待了重新部署完成（1-2 分钟）
- [ ] 清除了浏览器缓存
- [ ] 刷新了应用页面

## 如果还是不行

1. **检查代码是否正确读取 Secrets**：
   - 查看 `uf_navigator_api.py` 中的 `_get_secret()` 函数
   - 确保它优先读取 `st.secrets`

2. **查看部署日志**：
   - 在 Streamlit Cloud Dashboard 中查看 "Logs"
   - 查找是否有错误信息

3. **尝试重新部署**：
   - 在 Dashboard 中点击 "Reboot app" 或 "Redeploy"
   - 这会强制重新加载所有配置

4. **联系支持**：
   - 如果以上都不行，可能是 Streamlit Cloud 的问题
   - 可以联系 Streamlit 支持或查看文档

## 测试配置是否成功

配置完成后，在应用中应该看到：

```
✅ UF LiteLLM client initialized (API will be used on demand).
```

而不是：

```
⚠️ UF LiteLLM client not ready. Check Streamlit secrets: UF_LITELLM_API_KEY / UF_LITELLM_BASE_URL.
🔄 Using fallback responses for student replies
```
