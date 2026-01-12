# ✅ 模型更新总结

## 📋 当前状态

- **模型仓库**: `zylandy/mae-intent-classifier` ✅
- **Token**: 有效，无需更改 ✅
- **配置**: 无需更改 ✅

## 🔍 发现的问题

模型文件上传到了 `checkpoint-3146/` 子目录，但 Hugging Face Inference API 需要文件在**仓库根目录**。

### 当前文件结构：
```
zylandy/mae-intent-classifier/
  └── checkpoint-3146/
      ├── config.json
      ├── model.safetensors
      ├── tokenizer_config.json
      └── ...
```

### 需要的文件结构：
```
zylandy/mae-intent-classifier/
  ├── config.json          ← 必需：模型配置
  ├── model.safetensors    ← 必需：模型权重
  ├── tokenizer_config.json ← 必需：Tokenizer 配置
  ├── vocab.json           ← 必需：RoBERTa 词汇表
  ├── merges.txt           ← 必需：RoBERTa BPE 合并规则
  └── special_tokens_map.json ← 必需：特殊 token 映射
```

**为什么需要 6 个文件？**

你的模型是 **RoBERTa** 类型，需要：
- **前 3 个文件**：模型本身（config + weights + tokenizer config）
- **后 3 个文件**：RoBERTa Tokenizer 的数据文件
  - `vocab.json`：词汇表（将词转换为 ID）
  - `merges.txt`：BPE（Byte Pair Encoding）合并规则
  - `special_tokens_map.json`：特殊 token（如 [CLS], [SEP] 等）

**如果缺少后 3 个文件**，Inference API 无法正确 tokenize 输入文本，会返回错误。

## 🔧 解决方案

### 方法 1: 移动文件到根目录（推荐）

1. 访问模型页面：https://huggingface.co/zylandy/mae-intent-classifier
2. 进入 **Files and versions** 标签
3. 对于每个文件（在 `checkpoint-3146/` 目录下）：
   - 点击文件右侧的 **⋮** 菜单
   - 选择 **Move** 或 **Delete and re-upload**
   - 将文件移动到根目录

4. 需要移动的文件（**6 个文件，全部必需**）：
   - `checkpoint-3146/config.json` → `config.json` ✅ 已上传
   - `checkpoint-3146/model.safetensors` → `model.safetensors` ✅ 已上传
   - `checkpoint-3146/tokenizer_config.json` → `tokenizer_config.json` ✅ 已上传
   - `checkpoint-3146/vocab.json` → `vocab.json` ⚠️ **还需要上传**
   - `checkpoint-3146/merges.txt` → `merges.txt` ⚠️ **还需要上传**
   - `checkpoint-3146/special_tokens_map.json` → `special_tokens_map.json` ⚠️ **还需要上传**

**当前状态**：已上传 3 个核心文件，还需要上传 3 个 Tokenizer 文件。

### 方法 2: 使用 Git（如果熟悉 Git）

```bash
# 克隆仓库
git clone https://huggingface.co/zylandy/mae-intent-classifier
cd mae-intent-classifier

# 移动文件
mv checkpoint-3146/config.json .
mv checkpoint-3146/model.safetensors .
mv checkpoint-3146/tokenizer_config.json .
mv checkpoint-3146/vocab.json .
mv checkpoint-3146/merges.txt .
mv checkpoint-3146/special_tokens_map.json .

# 提交
git add .
git commit -m "Move model files to root directory"
git push
```

## ✅ 验证

移动文件后，验证 API 是否正常工作：

```python
import requests

HF_TOKEN = "your-token"
HF_MODEL = "zylandy/mae-intent-classifier"

headers = {"Authorization": f"Bearer {HF_TOKEN}"}
url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

resp = requests.post(
    url, 
    headers=headers, 
    json={"inputs": "I want to learn about research opportunities"}, 
    timeout=60
)

print(resp.json())
```

## 📝 配置确认

**无需更改配置！** 当前配置已经正确：

```toml
# Streamlit Secrets 或 .streamlit/secrets.toml
HF_MODEL = "zylandy/mae-intent-classifier"  # ✅ 正确
HF_TOKEN = "your-token"  # ✅ Token 仍然有效，无需更改
```

## 🎯 总结

1. ✅ **Token**: 无需更改，仍然有效
2. ✅ **模型名称**: 无需更改（还是 `zylandy/mae-intent-classifier`）
3. ⚠️ **文件位置**: 需要将文件从 `checkpoint-3146/` 移动到根目录
4. ✅ **配置**: 无需更改

移动文件后，系统会自动使用新模型！
