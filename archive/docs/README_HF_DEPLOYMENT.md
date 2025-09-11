# 🚀 将RoBERTa模型部署到Hugging Face Spaces

## 步骤1: 上传模型到Hugging Face Hub

```bash
# 安装Hugging Face CLI
pip install huggingface_hub

# 登录
huggingface-cli login

# 创建模型仓库
huggingface-cli repo create mae-intent-classifier --type model

# 上传模型
huggingface-cli upload your-username/mae-intent-classifier ./pre-train/balanced_finetuned_model
```

## 步骤2: 创建Hugging Face Space

1. 访问 [huggingface.co/spaces](https://huggingface.co/spaces)
2. 点击 "Create new Space"
3. 填写信息：
   - **Space name**: `mae-intent-classifier`
   - **License**: `MIT`
   - **SDK**: `Streamlit`
   - **Hardware**: `GPU T4 small` (免费)

## 步骤3: 上传代码

将以下文件上传到Space：
- `huggingface_app.py` (重命名为 `app.py`)
- `requirements_hf.txt` (重命名为 `requirements.txt`)

## 步骤4: 修改模型路径

在 `app.py` 中修改：
```python
model_name = "your-username/mae-intent-classifier"  # 替换为你的实际模型名
```

## 步骤5: 部署

1. 提交代码到Space
2. 等待自动构建完成
3. 访问你的Space URL

## 优势

- ✅ **完全免费**
- ✅ **GPU支持**
- ✅ **自动部署**
- ✅ **全球访问**
- ✅ **API接口**

## 其他免费选项

### Modal
```python
import modal

app = modal.App("mae-classifier")

@app.function(gpu="T4")
def classify_intent(text: str):
    # 你的模型代码
    pass
```

### Replicate
```python
import replicate

output = replicate.run(
    "your-username/mae-classifier:latest",
    input={"text": "I need help"}
)
```

### Google Colab + ngrok
```python
!pip install streamlit pyngrok
!streamlit run app.py --server.port 8501 &
!ngrok http 8501
```
