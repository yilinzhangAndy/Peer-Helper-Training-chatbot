# 📁 Hugging Face 模型文件结构说明

## ✅ 根目录必需文件

为了让 Inference API 正常工作，以下文件**必须**在根目录：

### 核心文件（必需）
- ✅ `config.json` - 模型配置
- ✅ `model.safetensors` - 模型权重
- ✅ `tokenizer_config.json` - Tokenizer 配置

### Tokenizer 文件（必需）
- ✅ `vocab.json` - 词汇表
- ✅ `merges.txt` - BPE 合并规则（如果是 RoBERTa/BERT）
- ✅ `special_tokens_map.json` - 特殊 token 映射

## 📂 checkpoint-3146 目录

### 位置
`checkpoint-3146/` 目录可以：
- ✅ **保留在根目录**（和必需文件一起）- 推荐
- ✅ **删除** - 也可以，不影响 Inference API

### 目录内容
`checkpoint-3146/` 目录通常包含：
- `config.json` - 已移动到根目录
- `model.safetensors` - 已移动到根目录
- `tokenizer_config.json` - 已移动到根目录
- `vocab.json` - 已移动到根目录
- `merges.txt` - 已移动到根目录
- `special_tokens_map.json` - 已移动到根目录
- `optimizer.pt` - 优化器状态（训练用，推理不需要）
- `rng_state.pth` - 随机数状态（训练用，推理不需要）
- `scheduler.pt` - 学习率调度器（训练用，推理不需要）
- `trainer_state.json` - 训练器状态（训练用，推理不需要）
- `training_args.bin` - 训练参数（训练用，推理不需要）

### 建议
- **保留 checkpoint-3146 目录**：如果你想保留训练检查点
- **删除 checkpoint-3146 目录**：如果只想保留推理必需的文件

## 📋 正确的文件结构

### 选项 1: 保留 checkpoint-3146（推荐）
```
mae-intent-classifier/
├── config.json                    ✅ 必需
├── model.safetensors              ✅ 必需
├── tokenizer_config.json          ✅ 必需
├── vocab.json                     ✅ 必需
├── merges.txt                     ✅ 必需
├── special_tokens_map.json        ✅ 必需
├── README.md                      ✅ 模型卡片
├── .gitattributes                 ✅ Git 配置
└── checkpoint-3146/               ⚪ 可选（训练检查点）
    ├── optimizer.pt
    ├── rng_state.pth
    ├── scheduler.pt
    ├── trainer_state.json
    └── training_args.bin
```

### 选项 2: 删除 checkpoint-3146
```
mae-intent-classifier/
├── config.json                    ✅ 必需
├── model.safetensors              ✅ 必需
├── tokenizer_config.json          ✅ 必需
├── vocab.json                     ✅ 必需
├── merges.txt                     ✅ 必需
├── special_tokens_map.json        ✅ 必需
├── README.md                      ✅ 模型卡片
└── .gitattributes                 ✅ Git 配置
```

## ⚠️ 重要提示

### 如果只上传了 3 个文件
如果你只上传了：
- `config.json`
- `model.safetensors`
- `tokenizer_config.json`

**还需要上传**：
- `vocab.json`
- `merges.txt`
- `special_tokens_map.json`

这些文件对于 Tokenizer 正常工作很重要！

## 🔍 如何检查

访问模型页面：https://huggingface.co/zylandy/mae-intent-classifier

在 "Files and versions" 标签中，应该看到：
- ✅ 根目录有 6 个必需文件
- ✅ checkpoint-3146 目录（可选）

## ✅ 验证

上传所有文件后：
1. 等待 5-10 分钟
2. 刷新 Streamlit 应用
3. 应该会看到 "✅ Hugging Face Intent Classification Model Connected"
