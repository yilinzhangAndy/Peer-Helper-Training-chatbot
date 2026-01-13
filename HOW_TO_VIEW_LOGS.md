# 📋 如何查看 Streamlit Cloud 日志

## 🔍 查看日志的方法

### 方法 1: Download Log（你看到的选项）

1. **点击 "Download log"** 或类似的下载选项
2. **下载日志文件**
3. **打开日志文件**，查找以下关键词：
   - `Using Hugging Face local model`
   - `Loading model locally`
   - `Model loaded successfully`
   - `Using keyword classifier`
   - `Insufficient memory`

### 方法 2: 在应用界面查看

如果应用正在运行，日志可能会显示在：
- **应用底部**的日志输出区域
- **浏览器控制台**（按 F12 打开开发者工具，查看 Console）

### 方法 3: Streamlit Cloud Dashboard

在 Streamlit Cloud Dashboard 中：
1. **点击你的应用**
2. **点击 "Manage app"** 或 "Settings"
3. **查找以下选项**：
   - "Logs"
   - "View logs"
   - "Download logs"
   - "Runtime logs"

## 🔍 在日志中查找什么

### 如果模型正在使用，应该看到：

```
✅ Using Hugging Face local model for intent classification
🔄 Loading model locally: zylandy/mae-intent-classifier
Memory: X.X GB available / Y.Y GB total
✅ Model loaded successfully
```

### 如果使用关键词分类器，应该看到：

```
🔄 Using keyword classifier for intent classification (fallback)
⚠️ Local model failed: ...
```

### 如果内存不足，应该看到：

```
⚠️ Insufficient memory: X.X GB available, need at least 2 GB
```

## 💡 替代方法：在代码中添加更明显的提示

如果你无法查看日志，我可以：
1. **在 UI 中显示使用的分类器**（已经在本地环境实现）
2. **添加更明显的状态消息**
3. **在应用界面显示模型加载状态**

## 📝 快速检查方法

### 方法 1: 测试复杂句子

发送一条复杂的句子，比如：
- "I'm feeling uncertain about my career path and would like some guidance on exploring different options"

**如果使用模型**：
- ✅ 能准确分类（通常是 Exploration and Reflection）
- ✅ 置信度较高（>0.7）

**如果使用关键词分类器**：
- ⚠️ 可能误分类
- ⚠️ 置信度可能较低（<0.6）

### 方法 2: 查看置信度模式

**模型的置信度**：
- 通常较高（0.7-0.99）
- 对复杂句子也能准确分类

**关键词分类器的置信度**：
- 范围：0.5-0.95
- 对简单句子可能很高，对复杂句子较低

## 🎯 根据你的数据判断

根据你之前的置信度：
- **99.2%** - 很可能使用了模型（超过关键词分类器最高值 95%）
- **88.2%** - 很可能使用了模型（典型模型范围）
- **59.0%** - 可能是关键词分类器，或模型对这条消息的置信度较低

**结论**：你的模型很可能已经在使用了！

## 💡 建议

1. **下载日志文件**，搜索 "Using Hugging Face local model"
2. **如果找到这个日志**，说明模型正在使用 ✅
3. **如果没找到**，可能还在加载，或内存不足

需要我添加更明显的 UI 提示来显示使用的分类器吗？
