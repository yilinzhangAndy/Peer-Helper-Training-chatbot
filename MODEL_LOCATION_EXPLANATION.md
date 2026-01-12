# 📍 模型位置和使用方式说明

## 📦 模型存储位置

### Hugging Face Hub（云端）
- ✅ **模型文件存储在 Hugging Face Hub**
- ✅ 访问地址: https://huggingface.co/zylandy/mae-intent-classifier
- ✅ 所有必需文件都在根目录
- ✅ 这是**永久存储**位置

### Streamlit 服务器（临时）
- ⚠️ **模型文件不在 Streamlit 代码仓库中**
- ⚠️ 代码会从 Hugging Face **下载**模型到 Streamlit 服务器
- ⚠️ 下载后临时存储在服务器的缓存目录中
- ⚠️ 这是**临时存储**，每次部署可能需要重新下载

## 🚀 使用流程

### 1. 首次调用时
```
用户发送消息 
  → 代码检查本地是否有缓存的模型
  → 如果没有，从 Hugging Face 下载（约 500MB）
  → 下载到 Streamlit 服务器的临时目录
  → 加载到内存（约 1-2GB）
  → 进行推理
```

### 2. 后续调用时
```
用户发送消息
  → 代码检查本地是否有缓存的模型
  → 如果有，直接使用（很快）
  → 进行推理
```

## 💡 为什么还显示 "processing"？

### 可能原因

1. **应用还没有刷新**
   - 需要完全刷新（Ctrl+F5 或 Cmd+Shift+R）
   - 或者清除浏览器缓存

2. **状态检测逻辑还在使用旧的代码**
   - 如果代码已更新但应用还没重新部署
   - 需要等待 Streamlit Cloud 自动重新部署（1-3分钟）

3. **Session state 缓存了旧状态**
   - Streamlit 会缓存 session state
   - 需要清除或等待超时

### 解决方案

1. **完全刷新应用**
   ```
   - 按 Ctrl+F5 (Windows/Linux) 或 Cmd+Shift+R (Mac)
   - 或清除浏览器缓存后刷新
   ```

2. **等待自动重新部署**
   - 如果代码已推送到 GitHub
   - Streamlit Cloud 会自动重新部署（1-3分钟）
   - 部署完成后刷新应用

3. **手动清除 session state**
   - 在应用界面，点击右上角的菜单
   - 选择 "Clear cache" 或 "Rerun"

## 📊 当前状态

- ✅ **模型位置**: Hugging Face Hub（云端）
- ✅ **使用方式**: 从 Hugging Face 下载到 Streamlit 服务器临时使用
- ✅ **内存状态**: 充足（3.6 GB 可用）
- ⚠️ **API 状态**: 不可用（模型太大，免费 API 不支持）
- ✅ **本地加载**: 可用（内存充足）

## 🎯 总结

**模型在哪里？**
- 永久存储：Hugging Face Hub（云端）
- 临时使用：Streamlit 服务器（下载后临时使用）

**为什么还显示 processing？**
- 可能是应用还没刷新或代码还没更新
- 完全刷新应用应该会看到新状态

**下一步？**
- 完全刷新应用（Ctrl+F5）
- 应该会看到 "Hugging Face 模型可用（将使用本地加载）"
