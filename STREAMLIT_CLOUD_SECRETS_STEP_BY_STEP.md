# 🔐 Streamlit Cloud Secrets 配置 - 详细步骤指南

## 📊 当前状态

根据你的检查结果：
- ❌ Streamlit Secrets: 未找到
- ❌ 环境变量: 未设置
- ❌ API Key: 未设置
- ✅ Base URL: 有默认值（但需要 API Key 才能工作）

## 🎯 详细查找步骤

### 步骤 1: 访问 Streamlit Cloud Dashboard

1. 打开浏览器，访问：**https://share.streamlit.io/**
2. 使用你的 GitHub 账号登录
3. 确保你登录的是正确的账号（拥有应用权限的账号）

### 步骤 2: 找到你的应用

1. 在 Dashboard 主页面，找到应用列表
2. 查找应用名称（可能是）：
   - `Peer-Helper-Training-chatbot`
   - `peer-apper-training-chatbot`
   - 或其他相关名称
3. **重要**：点击应用**卡片**或**应用名称**（不是 "Open app" 按钮）

### 步骤 3: 进入应用管理页面

在应用详情页，尝试以下方法：

#### 方法 A: 查看顶部标签页
- 查找顶部是否有这些标签：
  - **"Settings"** ⭐ 最可能在这里
  - **"Secrets"**
  - **"Deployments"**
  - **"Activity"**
  - **"Manage"**
- 点击 **"Settings"** 或 **"Secrets"** 标签

#### 方法 B: 查看左侧菜单
- 在左侧边栏查找：
  - **"⚙️ Settings"**
  - **"Manage app"**
  - **"Configuration"**
  - **"Secrets"**
- 点击进入

#### 方法 C: 查看右上角菜单
- 查找右上角的 **"⋮"** (三个点) 图标
- 点击后，查找：
  - **"Settings"**
  - **"Manage app"**
  - **"Edit secrets"**
  - **"Configuration"**

#### 方法 D: 查看页面内容
- 在应用详情页向下滚动
- 查找任何包含以下关键词的部分：
  - "Secrets"
  - "Environment variables"
  - "Configuration"
  - "Settings"

### 步骤 4: 找到 Secrets 编辑器

一旦进入 Settings 或 Secrets 页面：

1. **查找 "Secrets" 部分**
   - 可能在页面中间或底部
   - 标题可能是 "Secrets", "Environment Variables", 或 "Configuration"

2. **查找编辑按钮**
   - 点击 **"Edit secrets"**
   - 或 **"Manage secrets"**
   - 或 **"Open secrets editor"**
   - 或直接显示一个文本编辑器

3. **如果看到文本编辑器**
   - 这就是 Secrets 配置的地方
   - 可能是空的，或者已经有一些内容

### 步骤 5: 配置 Secrets

在编辑器中，**删除所有现有内容**（如果有），然后添加：

```toml
UF_LITELLM_BASE_URL = "https://api.ai.it.ufl.edu"
UF_LITELLM_API_KEY = "sk-FEhqmwbGafXtX9sv07rZLw"
```

**重要格式要求**：
- ✅ 使用 TOML 格式
- ✅ 键值对之间用 `=` 连接，等号两边有空格
- ✅ 字符串用双引号括起来
- ❌ 不要包含 `[secrets]` 或其他节标题
- ❌ 不要有多余的空格或特殊字符

### 步骤 6: 保存并等待部署

1. **点击 "Save" 按钮**
   - 通常在编辑器底部或右上角
   - 可能显示为 "Save", "Update", "Apply" 等

2. **等待自动重新部署**
   - Streamlit Cloud 会自动检测更改
   - 通常需要 1-3 分钟
   - 可以在 "Deployments" 或 "Activity" 标签查看部署状态

3. **验证配置**
   - 等待部署完成后，刷新应用页面
   - 点击应用内的 **"🔍 检查 Secrets 配置"** 按钮
   - 应该看到：
     - ✅ `UF_LITELLM_BASE_URL: https://api.ai.it.ufl.edu`
     - ✅ `UF_LITELLM_API_KEY: ✅ 已设置`
     - ✅ `Client 状态: ✅ 已创建`

## 🔍 如果仍然找不到 Secrets

### 可能的原因和解决方案

#### 原因 1: 界面更新
**解决方案**：
- Streamlit Cloud 可能更新了界面
- Secrets 可能改名为 "Environment variables" 或其他名称
- 尝试搜索页面中的关键词："secret", "env", "config"

#### 原因 2: 权限问题
**解决方案**：
- 确认你是应用的所有者或有编辑权限
- 如果应用是共享的，可能需要所有者权限才能编辑 Secrets

#### 原因 3: 应用类型不同
**解决方案**：
- 某些类型的应用可能有不同的配置方式
- 检查应用详情页是否有 "Advanced settings" 或其他选项

### 替代方案

#### 方案 A: 通过 GitHub Repository
1. 访问 GitHub Repository Settings
2. 查找 "Secrets and variables" → "Actions"
3. 但注意：这通常用于 GitHub Actions，不是 Streamlit Cloud

#### 方案 B: 联系 Streamlit 支持
- 如果以上方法都不行，可能是 Streamlit Cloud 的问题
- 可以联系 Streamlit 支持或查看社区论坛

#### 方案 C: 使用应用内的检查功能
- 至少可以确认当前配置状态
- 了解是否需要配置

## 📝 配置后的验证清单

配置完成后，检查以下项目：

- [ ] Secrets 已保存
- [ ] 应用已重新部署（查看部署日志）
- [ ] 等待 1-3 分钟
- [ ] 刷新应用页面
- [ ] 点击 "🔍 检查 Secrets 配置" 按钮
- [ ] 看到 ✅ 标记（不是 ❌）
- [ ] 应用显示 "✅ UF LiteLLM client initialized"

## 💡 提示

1. **截图保存**：如果找到了 Secrets 配置页面，可以截图保存，方便以后查找

2. **使用浏览器搜索**：在应用详情页，按 `Ctrl+F` (Windows) 或 `Cmd+F` (Mac) 搜索 "secret" 或 "env"

3. **查看所有菜单**：仔细查看所有可见的菜单项和按钮

4. **检查 URL**：注意浏览器地址栏的 URL，可能包含有用的信息

## 🆘 如果还是找不到

请提供以下信息，我可以进一步帮助：
1. 应用详情页的截图（隐藏敏感信息）
2. 你看到的所有菜单项和按钮
3. 浏览器地址栏的完整 URL
