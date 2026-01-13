# 📊 数据存储状态说明

## ✅ 真实对话数据（Few-Shot 数据）

### 状态：✅ **数据还在，可以正常使用**

**数据文件位置：**
- `data/peer_dataset_26.xlsm` (168KB) - **1387 条真实对话** ✅
- `data/extracted_pdf_content.json` (5KB) - PDF 提取的对话 ✅

**验证结果：**
```
✅ 成功加载数据文件: data/peer_dataset_26.xlsm
   数据行数: 1387
✅ 成功解析 1387 条对话
✅ 成功加载 1387 条真实对话
```

**用途：**
- 这些数据用于 Few-Shot Learning
- 生成学生回复时作为示例参考
- 系统会自动从这些数据中选择相关示例

**数据内容：**
- 每条对话包含：Advisor（导师）、Student（学生）、Intent（意图）、Persona（类型）
- 数据格式：Excel (.xlsm)
- 列名：Mentor Label, Mentor, Mentee, Mentee Label

**数据样本：**
```
对话 1:
  Advisor: This is being recorded to the cloud. Now, it's only going to be looked at by the...
  Student: No problem. Just I wanna get rid of the hold. The advice for meeting hold that I...
  Intent: Problem Solving and Critical Thinking
```

## ⚠️ 用户输入的对话数据

### 状态：❌ **没有持久化存储**

**当前存储方式：**
- 存储在 `st.session_state.messages` 中（**内存中**）
- 只在当前浏览器会话中有效
- 刷新页面或开始新对话会丢失

**已禁用的功能：**
- `save_to_google_sheets()` - 已禁用（返回 False）
- Google Sheets 日志记录 - 已禁用
- Dropbox 集成 - 存在但未激活

**可用的导出功能：**
- `export_session_data()` - 可以导出当前会话数据（JSON 格式）
- 但需要手动下载，不会自动保存

## 📋 数据分类总结

### 1. Few-Shot 训练数据 ✅
- **文件**: `data/peer_dataset_26.xlsm`
- **数量**: 1387 条对话
- **状态**: ✅ 存在且可正常加载
- **用途**: 用于生成学生回复的示例
- **持久化**: ✅ 永久存储（文件）

### 2. PDF 提取的对话 ✅
- **文件**: `data/extracted_pdf_content.json`
- **状态**: ✅ 存在
- **用途**: 补充 Few-Shot 示例
- **持久化**: ✅ 永久存储（文件）

### 3. 用户在应用中输入的对话 ❌
- **存储位置**: `st.session_state.messages`（内存）
- **状态**: ❌ 没有持久化存储
- **持久化**: ❌ 只在当前会话有效
- **丢失时机**: 
  - 刷新页面
  - 开始新对话
  - 关闭浏览器标签

## 🔍 如何验证数据

### 验证 Few-Shot 数据：

```python
from few_shot_examples import load_conversations_from_file

conversations = load_conversations_from_file()
print(f"加载了 {len(conversations)} 条对话")
```

### 验证用户对话数据：

在应用中：
- 对话数据只在当前会话中可见
- 可以使用 "Export" 功能下载当前会话数据
- 但不会自动保存到服务器

## 💡 如果需要保存用户对话

### 选项 1: 启用 Google Sheets 日志（需要配置）

1. 配置 Google Sheets API
2. 修改 `save_to_google_sheets()` 函数
3. 启用 `st.session_state.allow_logging`

### 选项 2: 使用 Dropbox 集成（需要配置）

1. 配置 Dropbox API token
2. 使用 `dropbox_integration.py` 中的功能
3. 在对话结束时自动上传

### 选项 3: 本地文件导出（当前可用）

1. 使用 `export_session_data()` 函数
2. 手动下载 JSON 文件
3. 保存到本地

## 📊 数据统计

### Few-Shot 数据：
- ✅ **1387 条真实对话** - 已加载
- ✅ **PDF 对话** - 已加载
- ✅ **总计约 1400+ 条对话** - 可用于 Few-Shot

### 用户对话数据：
- ❌ **没有持久化存储**
- ⚠️ **只在当前会话有效**
- 💾 **可以手动导出**

## 🎯 结论

### ✅ 真实对话数据（Few-Shot）
- **状态**: ✅ 还在，可以正常使用
- **位置**: `data/peer_dataset_26.xlsm`
- **数量**: 1387 条
- **用途**: 生成学生回复的示例

### ❌ 用户输入的对话
- **状态**: ❌ 没有持久化存储
- **存储**: 只在内存中（当前会话）
- **建议**: 如果需要保存，可以启用 Google Sheets 或 Dropbox 集成

## 📝 建议

如果你需要保存用户在应用中输入的对话：

1. **短期方案**: 使用导出功能手动下载
2. **长期方案**: 配置 Google Sheets 或 Dropbox 集成
3. **开发方案**: 添加数据库存储（如 SQLite 或 PostgreSQL）
