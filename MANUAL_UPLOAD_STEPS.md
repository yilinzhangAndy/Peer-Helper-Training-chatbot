# 📤 手动上传模型步骤（最简单的方法）

由于 API 权限限制，建议使用以下方法：

## 🎯 方法 1: 使用 Hugging Face Web UI（推荐）

### 步骤 1: 创建新模型仓库

1. 访问 https://huggingface.co/new
2. 选择 **Model** 类型
3. 填写信息：
   - **Model name**: `mae-intent-classifier-v2`
   - **Visibility**: Public（或 Private）
   - **License**: 选择合适的许可证
4. 点击 **Create model**

### 步骤 2: 上传文件

1. 进入模型页面：https://huggingface.co/zylandy/mae-intent-classifier-v2
2. 点击 **Files and versions** 标签
3. 点击 **Add file** → **Upload file**
4. 上传以下文件（从 `checkpoint-3146/` 目录）：
   - ✅ `config.json`
   - ✅ `model.safetensors` (475MB)
   - ✅ `tokenizer_config.json`
   - ✅ `vocab.json`
   - ✅ `merges.txt`
   - ✅ `special_tokens_map.json`

**注意**: 不需要上传这些文件：
   - ❌ `optimizer.pt`
   - ❌ `rng_state.pth`
   - ❌ `scheduler.pt`
   - ❌ `trainer_state.json`
   - ❌ `training_args.bin`

### 步骤 3: 更新配置

上传完成后，更新配置：

**Streamlit Cloud Secrets** 或 **.streamlit/secrets.toml**:
```toml
HF_MODEL = "zylandy/mae-intent-classifier-v2"
HF_TOKEN = "your-huggingface-token"  # 从 https://huggingface.co/settings/tokens 获取
```

## 🎯 方法 2: 使用 Git LFS（适合大文件）

如果 Web UI 上传失败（文件太大），可以使用 Git LFS：

```bash
# 1. 安装 Git LFS
git lfs install

# 2. 克隆仓库
git clone https://huggingface.co/zylandy/mae-intent-classifier-v2
cd mae-intent-classifier-v2

# 3. 复制文件
cp ../chatbot/checkpoint-3146/config.json .
cp ../chatbot/checkpoint-3146/model.safetensors .
cp ../chatbot/checkpoint-3146/tokenizer_config.json .
cp ../chatbot/checkpoint-3146/vocab.json .
cp ../chatbot/checkpoint-3146/merges.txt .
cp ../chatbot/checkpoint-3146/special_tokens_map.json .

# 4. 设置 Git LFS 跟踪大文件
git lfs track "*.safetensors"

# 5. 提交并推送
git add .
git commit -m "Upload model files"
git push
```

## 🎯 方法 3: 更新现有模型（如果已有）

如果你想更新现有的 `zylandy/mae-intent-classifier` 模型：

1. 访问 https://huggingface.co/zylandy/mae-intent-classifier
2. 点击 **Files and versions**
3. 删除旧文件（如果需要）
4. 上传新文件

然后更新配置：
```toml
HF_MODEL = "zylandy/mae-intent-classifier"  # 使用现有模型名
```

## ✅ 验证上传

上传完成后，测试模型：

```python
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="zylandy/mae-intent-classifier-v2",
    tokenizer="zylandy/mae-intent-classifier-v2"
)

result = classifier("I want to learn about research opportunities")
print(result)
```

## 📝 需要上传的文件清单

从 `checkpoint-3146/` 目录上传：

### 必需文件
- [x] `config.json` (1.1 KB)
- [x] `model.safetensors` (475 MB) ⚠️ 大文件，需要 Git LFS 或耐心等待
- [x] `tokenizer_config.json` (1.2 KB)
- [x] `vocab.json` (976 KB)
- [x] `merges.txt` (445 KB)
- [x] `special_tokens_map.json` (958 bytes)

### 可选文件
- [ ] `label_mapping.json` (如果有的话)

### 不需要上传
- [ ] `optimizer.pt` (训练相关)
- [ ] `rng_state.pth` (训练相关)
- [ ] `scheduler.pt` (训练相关)
- [ ] `trainer_state.json` (训练相关)
- [ ] `training_args.bin` (训练相关)
