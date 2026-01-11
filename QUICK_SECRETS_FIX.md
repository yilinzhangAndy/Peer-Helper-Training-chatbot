# ⚡ 快速配置 Streamlit Cloud Secrets

## 📊 当前问题

根据检查结果：
- ❌ Streamlit Secrets: 未找到
- ❌ API Key: 未设置
- ❌ Client 状态: 未创建

## 🎯 快速解决方案

### 方法 1: 在 Streamlit Cloud Dashboard 中查找（推荐）

#### 步骤 A: 从应用卡片进入
1. 访问 https://share.streamlit.io/
2. 找到你的应用卡片
3. **不要点击 "Open app"**
4. **点击应用名称或卡片本身**（进入应用详情页）

#### 步骤 B: 查找 Secrets 配置
在应用详情页，尝试以下位置：

**位置 1: 顶部标签页**
- 查看页面顶部是否有标签栏
- 查找：**"Settings"**, **"Secrets"**, **"Manage"**, **"Deployments"**
- 点击 **"Settings"** 或 **"Secrets"** 标签

**位置 2: 左侧菜单**
- 查看左侧边栏
- 查找：**"⚙️ Settings"**, **"Manage app"**, **"Configuration"**
- 点击进入

**位置 3: 右上角菜单**
- 查找右上角的 **"⋮"** (三个点) 图标
- 点击后查找：**"Settings"**, **"Manage app"**, **"Edit secrets"**

**位置 4: 页面内容**
- 向下滚动页面
- 使用浏览器搜索功能（`Ctrl+F` 或 `Cmd+F`）
- 搜索关键词：**"secret"**, **"env"**, **"config"**

#### 步骤 C: 配置 Secrets
一旦找到 Secrets 编辑器：

1. **清空编辑器**（如果有内容）
2. **添加以下内容**：

```toml
UF_LITELLM_BASE_URL = "https://api.ai.it.ufl.edu"
UF_LITELLM_API_KEY = "sk-FEhqmwbGafXtX9sv07rZLw"
```

3. **点击 "Save"** 保存
4. **等待 1-3 分钟**（自动重新部署）
5. **刷新应用页面**
6. **再次点击 "🔍 检查 Secrets 配置"** 验证

### 方法 2: 直接访问 Secrets URL（如果知道应用名）

尝试在浏览器中访问：
```
https://share.streamlit.io/app/your-app-name/secrets
```

或：
```
https://share.streamlit.io/app/your-app-name/settings
```

### 方法 3: 通过应用管理页面

1. 在应用详情页，查找 **"Manage app"** 按钮
2. 点击进入管理页面
3. 查找 **"Secrets"** 或 **"Environment variables"** 部分

## 🔍 如果仍然找不到

### 可能的原因：
1. **界面更新**：Streamlit Cloud 可能更新了界面，Secrets 位置改变了
2. **权限问题**：可能需要应用所有者权限
3. **应用类型**：某些应用类型可能有不同的配置方式

### 替代方案：

#### 方案 A: 查看 Streamlit Cloud 文档
- 访问：https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- 查看最新的配置方法

#### 方案 B: 联系 Streamlit 支持
- 如果界面确实找不到 Secrets 配置
- 可以联系 Streamlit 支持获取帮助

#### 方案 C: 使用 Fallback 模式（临时）
- 应用仍然可以正常工作
- 使用本地 fallback 响应生成学生回复
- 所有功能都可以正常使用

## 📝 配置后验证

配置完成后，应该看到：

```
✅ 从 Streamlit Secrets 读取：
   - UF_LITELLM_BASE_URL: https://api.ai.it.ufl.edu
   - UF_LITELLM_API_KEY: ✅ 已设置

✅ 实际使用的配置：
   - Base URL: https://api.ai.it.ufl.edu
   - API Key: ✅ 已设置
   - Client 状态: ✅ 已创建
```

## 💡 提示

1. **使用浏览器搜索**：在应用详情页按 `Ctrl+F` (Windows) 或 `Cmd+F` (Mac)，搜索 "secret"

2. **查看所有可见元素**：仔细查看所有按钮、菜单、标签页

3. **检查 URL**：注意浏览器地址栏，可能包含有用的路径信息

4. **截图保存**：如果找到了，截图保存位置，方便以后查找

## 🆘 需要帮助？

如果以上方法都不行，请提供：
1. 应用详情页的截图（隐藏敏感信息）
2. 你看到的所有菜单项
3. 浏览器地址栏的 URL

我可以根据具体情况提供更精确的指导。
