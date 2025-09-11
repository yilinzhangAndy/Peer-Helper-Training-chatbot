import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import gradio as gr

# 设置页面配置
st.set_page_config(
    page_title="MAE Intent Classifier",
    page_icon="🎓",
    layout="wide"
)

# 加载模型
@st.cache_resource
def load_model():
    try:
        # 从Hugging Face Hub加载你的模型
        model_name = "your-username/mae-intent-classifier"  # 替换为你的模型名
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
    
    # 加载模型
    with st.spinner("加载模型中..."):
        tokenizer, model = load_model()
    
    if tokenizer and model:
        st.success("✅ 模型加载成功！")
        
        # 输入文本
        text_input = st.text_area(
            "输入要分类的文本:",
            placeholder="例如: I need help with my research direction...",
            height=100
        )
        
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
            else:
                st.warning("请输入要分类的文本")
    else:
        st.error("❌ 模型加载失败，请检查模型路径")

if __name__ == "__main__":
    main()
