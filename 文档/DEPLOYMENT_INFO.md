# 🌐 应用部署说明

## 两个版本的对比

### 1. 本地版本 (localhost:8501)
- **URL**: http://localhost:8501/
- **位置**: 运行在你的本地电脑上
- **状态**: ✅ 当前正在运行
- **用途**: 
  - 本地开发和测试
  - 快速测试新功能
  - 不需要网络连接（除了 API 调用）

### 2. 云端版本 (Streamlit Cloud)
- **URL**: https://peer-apper-training-chatbot-an46q5yl8sqbcyqchwgnin.streamlit.app/
- **位置**: Streamlit Cloud 服务器
- **状态**: 需要检查是否已部署
- **用途**:
  - 公开访问（任何人都可以访问）
  - 24/7 在线
  - 分享给其他人使用
  - 生产环境

## 应该使用哪一个？

### 使用本地版本 (localhost:8501) 如果：
- ✅ 你在本地开发或测试
- ✅ 你想快速测试新功能
- ✅ 你不需要分享给其他人
- ✅ 你的电脑正在运行

### 使用云端版本 (Streamlit Cloud) 如果：
- ✅ 你想分享给其他人使用
- ✅ 你需要 24/7 在线访问
- ✅ 你不需要本地运行应用
- ✅ 你想在生产环境中使用

## 配置差异

### 本地版本配置
- 使用 `.streamlit/secrets.toml` 文件
- 或使用环境变量
- 配置在本地电脑上

### 云端版本配置
- 在 Streamlit Cloud 的 Secrets 设置中配置
- 通过 Streamlit Cloud Dashboard 设置
- Settings → Secrets → 添加 `UF_LITELLM_API_KEY` 和 `UF_LITELLM_BASE_URL`

## 当前状态

- **本地版本**: ✅ 正在运行 (localhost:8501)
- **云端版本**: 需要检查部署状态

## 推荐

**对于开发和测试**: 使用本地版本 (localhost:8501)
**对于分享和使用**: 使用云端版本 (Streamlit Cloud)

两个版本功能相同，只是部署位置不同。
