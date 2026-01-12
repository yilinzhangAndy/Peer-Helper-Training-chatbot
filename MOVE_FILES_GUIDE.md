# 📦 移动 Hugging Face 模型文件到根目录指南

## 🎯 目标

将模型文件从 `checkpoint-3146/` 子目录移动到根目录，以便 Inference API 可以正常工作。

## 🚀 方法 1: 使用脚本自动操作（推荐）

我已经创建了一个自动化脚本，可以帮你完成所有操作。

### 步骤：

1. **运行脚本**:
```bash
cd /Users/zhangyilin/Documents/UF/Ph.D/Chatbot/chatbot
./move_hf_files_to_root.sh
```

脚本会自动：
- ✅ 克隆模型仓库
- ✅ 移动文件到根目录
- ✅ 提交更改
- ✅ 推送到 Hugging Face
- ✅ 清理临时文件

### 如果脚本失败：

- 检查网络连接
- 确认 Hugging Face token 有效
- 查看错误信息

## 🖱️ 方法 2: 使用 Hugging Face Web UI（简单）

如果你更喜欢在网页上操作：

### 步骤：

1. **访问模型页面**: https://huggingface.co/zylandy/mae-intent-classifier

2. **进入文件管理**:
   - 点击 "Files and versions" 标签
   - 或直接访问: https://huggingface.co/zylandy/mae-intent-classifier/tree/main

3. **下载文件**（从子目录）:
   - 进入 `checkpoint-3146/` 目录
   - 下载以下文件到本地：
     - `config.json`
     - `model.safetensors`
     - `tokenizer_config.json`
     - `vocab.json`
     - `merges.txt`
     - `special_tokens_map.json`

4. **上传到根目录**:
   - 回到根目录（点击 "mae-intent-classifier" 或 "main"）
   - 点击 "Add file" → "Upload file"
   - 上传刚才下载的文件

5. **删除子目录中的文件**（可选）:
   - 进入 `checkpoint-3146/` 目录
   - 删除已移动的文件（保留其他文件如 `optimizer.pt` 等）

## 💻 方法 3: 使用 Git 手动操作

如果你熟悉 Git：

### 步骤：

1. **克隆仓库**:
```bash
git clone https://huggingface.co/zylandy/mae-intent-classifier
cd mae-intent-classifier
```

2. **移动文件**:
```bash
mv checkpoint-3146/config.json .
mv checkpoint-3146/model.safetensors .
mv checkpoint-3146/tokenizer_config.json .
mv checkpoint-3146/vocab.json .
mv checkpoint-3146/merges.txt .
mv checkpoint-3146/special_tokens_map.json .
```

3. **提交并推送**:
```bash
git add .
git commit -m "Move model files to root directory for Inference API"
git push
```

## 📋 需要移动的文件列表

以下文件需要从 `checkpoint-3146/` 移动到根目录：

- ✅ `config.json` - 模型配置（必需）
- ✅ `model.safetensors` - 模型权重（必需）
- ✅ `tokenizer_config.json` - Tokenizer 配置（必需）
- ✅ `vocab.json` - 词汇表（必需）
- ✅ `merges.txt` - BPE 合并规则（必需）
- ✅ `special_tokens_map.json` - 特殊 token 映射（必需）

**不需要移动的文件**（可以保留在子目录）：
- `optimizer.pt` - 优化器状态（训练用）
- `rng_state.pth` - 随机数状态（训练用）
- `scheduler.pt` - 学习率调度器（训练用）
- `trainer_state.json` - 训练器状态（训练用）
- `training_args.bin` - 训练参数（训练用）

## ⏱️ 操作后等待时间

移动文件后：
1. **等待 5-10 分钟** 让 Hugging Face 处理
2. **刷新 Streamlit 应用**
3. 应该会看到 `✅ Hugging Face Intent Classification Model Connected`

## ✅ 验证

移动完成后，可以通过以下方式验证：

1. **检查文件位置**:
   - 访问: https://huggingface.co/zylandy/mae-intent-classifier
   - 确认根目录有 `config.json`, `model.safetensors` 等文件

2. **测试 API**:
```bash
python test_model_deployment.py
```
应该返回 200 或 503（加载中）

3. **刷新应用**:
   - 应该看到 "✅ Hugging Face 意图分类模型已连接"

## 💡 提示

- **备份**: 移动前建议先备份（Git 会自动保留历史）
- **不要删除子目录**: 可以保留 `checkpoint-3146/` 目录，只移动必需文件
- **如果失败**: 可以继续使用关键词分类器（已经工作正常）

## 🆘 遇到问题？

如果移动后还是 404：
1. 等待更长时间（10-30 分钟）
2. 检查文件是否真的在根目录
3. 或者继续使用关键词分类器（已经工作正常）
