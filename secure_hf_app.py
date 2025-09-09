import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

# 设置页面配置
st.set_page_config(
    page_title="MAE Intent Classifier",
    page_icon="🎓",
    layout="wide"
)

# 安全配置
MAX_INPUT_LENGTH = 500
RATE_LIMIT = 10  # 每分钟最多10次请求

# 加载模型
@st.cache_resource
def load_model():
    try:
        # 从环境变量或默认值获取模型名
        model_name = os.getenv("MODEL_NAME", "your-username/mae-intent-classifier")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        return tokenizer, model
    except Exception as e:
        st.error(f"模型加载失败: {e}")
        return None, None

def classify_intent(text, tokenizer, model):
    """使用RoBERTa模型分类意图"""
    if not tokenizer or not model:
        return {"intent": "Error", "confidence": 0.0}
    
    # 输入验证
    if len(text) > MAX_INPUT_LENGTH:
        return {"intent": "Input too long", "confidence": 0.0}
    
    # 预处理文本
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    
    # 推理
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # 获取结果
    intent_labels = [
        "Exploration and Reflection",
        "Feedback and Support", 
        "Goal Setting and Planning",
        "Problem Solving and Critical Thinking",
        "Understanding and Clarification"
    ]
    
    predicted_class = torch.argmax(predictions, dim=-1).item()
    confidence = predictions[0][predicted_class].item()
    intent = intent_labels[predicted_class]
    
    return {"intent": intent, "confidence": confidence}

def main():
    st.title("🎓 MAE Intent Classifier")
    st.markdown("使用RoBERTa模型进行意图分类")
    
    # 显示使用说明
    with st.expander("📖 使用说明"):
        st.markdown("""
        **如何使用：**
        1. 在下方输入框中输入要分类的文本
        2. 点击"分类"按钮
        3. 查看分类结果和置信度
        
        **支持的语言：** 英文
        
        **输入限制：** 最多500个字符
        """)
    
    # 加载模型
    with st.spinner("加载模型中..."):
        tokenizer, model = load_model()
    
    if tokenizer and model:
        st.success("✅ 模型加载成功！")
        
        # 输入文本
        text_input = st.text_area(
            "输入要分类的文本:",
            placeholder="例如: I need help with my research direction...",
            height=100,
            max_chars=MAX_INPUT_LENGTH
        )
        
        # 显示字符计数
        st.caption(f"字符数: {len(text_input)}/{MAX_INPUT_LENGTH}")
        
        if st.button("分类", type="primary"):
            if text_input.strip():
                with st.spinner("分类中..."):
                    result = classify_intent(text_input, tokenizer, model)
                
                # 显示结果
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("意图", result["intent"])
                with col2:
                    st.metric("置信度", f"{result['confidence']:.2%}")
                
                # 可视化
                st.progress(result["confidence"])
                
                # 显示详细信息
                with st.expander("📊 详细信息"):
                    st.json(result)
            else:
                st.warning("请输入要分类的文本")
    else:
        st.error("❌ 模型加载失败，请检查模型路径")
    
    # 页脚
    st.markdown("---")
    st.markdown("**MAE Intent Classifier** - 基于RoBERTa的意图分类系统")

if __name__ == "__main__":
    main()
