import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification
import os
import random
from datetime import datetime
from typing import Dict, Any, List

# Page configuration
st.set_page_config(
    page_title="Peer Helper Training Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .student-message {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-left: 4px solid #4caf50;
        color: #2e7d32;
    }
    .advisor-message {
        background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
        border-left: 4px solid #2196f3;
        color: #1565c0;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-left: 0.8rem;
        border: 2px solid transparent;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .intent-exploration { 
        background: linear-gradient(45deg, #fff3e0, #ffe0b2); 
        color: #e65100; 
        border-color: #ff9800;
    }
    .intent-feedback { 
        background: linear-gradient(45deg, #e8f5e8, #c8e6c9); 
        color: #2e7d32; 
        border-color: #4caf50;
    }
    .intent-goal { 
        background: linear-gradient(45deg, #fff3e0, #ffcc80); 
        color: #e65100; 
        border-color: #ff9800;
    }
    .intent-problem { 
        background: linear-gradient(45deg, #ffebee, #ffcdd2); 
        color: #c62828; 
        border-color: #f44336;
    }
    .intent-understanding { 
        background: linear-gradient(45deg, #f3e5f5, #e1bee7); 
        color: #6a1b9a; 
        border-color: #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

# Load models
@st.cache_resource
def load_models():
    """Load Llama 3.1 8B for generation and RoBERTa for classification"""
    try:
        # Load Llama 3.1 8B Instruct for generation
        llama_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
        llama_model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-3.1-8B-Instruct",
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # Load RoBERTa for classification
        roberta_tokenizer = AutoTokenizer.from_pretrained("zylandy/mae-intent-classifier")
        roberta_model = AutoModelForSequenceClassification.from_pretrained("zylandy/mae-intent-classifier")
        
        return llama_tokenizer, llama_model, roberta_tokenizer, roberta_model
    except Exception as e:
        st.error(f"Model loading failed: {e}")
        return None, None, None, None

# Student persona data
STUDENT_PERSONAS = {
    "alpha": {
        "description": "Moderately below average self-efficacy and sense of belonging. Positive about seeking help.",
        "traits": "Works hard, average confidence in major choice, willing to ask questions, interested in clubs/teams, unsure about internships",
        "communication_style": "Grateful, appreciative, willing to learn, asks for clarification when needed"
    },
    "beta": {
        "description": "Very low sense of belonging and self-efficacy. Hesitant to seek help.",
        "traits": "Low confidence, avoids asking questions, sensitive to peer perception, avoids clubs and faculty",
        "communication_style": "Hesitant, self-doubting, apologetic, needs reassurance"
    },
    "delta": {
        "description": "Moderately above average self-confidence and belonging. Hesitant to seek help.",
        "traits": "Good self-confidence, worries about others' opinions, not interested in research, open to clubs and internships",
        "communication_style": "Analytical, strategic, considers implications, methodical"
    },
    "echo": {
        "description": "Very high self-confidence and belonging. Positive about seeking help.",
        "traits": "Very confident, strong sense of belonging, asks for help freely, interested in research, active in internships",
        "communication_style": "Enthusiastic, confident, proactive, ambitious"
    }
}

def generate_student_reply_with_llama(context: str, persona: str, advisor_message: str, llama_tokenizer, llama_model):
    """Generate student reply using Llama 3.1 8B"""
    persona_info = STUDENT_PERSONAS[persona]
    
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a {persona} student in an engineering program. Your characteristics:
- Description: {persona_info['description']}
- Traits: {persona_info['traits']}
- Communication style: {persona_info['communication_style']}

Respond naturally as this student would, staying in character. Keep responses conversational and authentic.<|eot_id|><|start_header_id|>user<|end_header_id|>

The peer advisor just said: "{advisor_message}"

How would you respond as a {persona} student?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    
    try:
        inputs = llama_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        inputs = {k: v.to(llama_model.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = llama_model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True,
                pad_token_id=llama_tokenizer.eos_token_id
            )
        
        response = llama_tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        return response.strip()
    except Exception as e:
        st.error(f"Generation failed: {e}")
        return "I'm not sure how to respond to that. Could you help me understand better?"

def classify_intent(text: str, roberta_tokenizer, roberta_model):
    """Classify intent using RoBERTa"""
    try:
        inputs = roberta_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        
        with torch.no_grad():
            outputs = roberta_model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
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
    except Exception as e:
        return {"intent": "Understanding and Clarification", "confidence": 0.5}

def get_intent_badge_class(intent: str) -> str:
    """Get CSS class for intent badge"""
    intent_lower = intent.lower().replace(" ", "_")
    if "exploration" in intent_lower:
        return "intent-exploration"
    elif "feedback" in intent_lower:
        return "intent-feedback"
    elif "goal" in intent_lower:
        return "intent-goal"
    elif "problem" in intent_lower:
        return "intent-problem"
    elif "understanding" in intent_lower:
        return "intent-understanding"
    else:
        return "intent-understanding"

def main():
    # Header
    st.markdown('<h1 class="main-header">🎓 Peer Helper Training Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<div style="background: linear-gradient(45deg, #FF6B6B, #4ECDC4); color: white; padding: 0.5rem 1rem; border-radius: 20px; text-align: center; margin: 1rem 0;">🤖 Powered by Llama 3.1 8B + RoBERTa</div>', unsafe_allow_html=True)
    
    # Load models
    with st.spinner("Loading AI models..."):
        llama_tokenizer, llama_model, roberta_tokenizer, roberta_model = load_models()
    
    if not all([llama_tokenizer, llama_model, roberta_tokenizer, roberta_model]):
        st.error("❌ Failed to load models. Please check the Space configuration.")
        return
    
    st.success("✅ Models loaded successfully!")
    
    # Initialize session state
    if "show_training" not in st.session_state:
        st.session_state.show_training = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.student_intents = []
        st.session_state.advisor_intents = []
    
    # Main content area
    if not st.session_state.show_training:
        # Landing page
        st.info("""
        **How It Works**
        
        **Choose Your Training Scenario**  
        Select a student persona (Alpha, Beta, Delta, or Echo) based on the mentoring skills you want to practice
        
        **Start Conversation Training**  
        Engage in realistic dialogue with AI-powered student personas that respond based on authentic psychological profiles
        
        **Get Real-time Feedback**  
        Our system analyzes your responses using AI classification and provides instant feedback on communication patterns
        """)
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Training", type="primary", use_container_width=True):
                st.session_state.show_training = True
                st.rerun()
    else:
        # Training interface
        with st.sidebar:
            st.header("👥 Choose Your Training Scenario")
            
            personas = ["alpha", "beta", "delta", "echo"]
            persona_descriptions = {
                "alpha": "Moderately below average self-efficacy and sense of belonging. Positive about seeking help.",
                "beta": "Very low sense of belonging and self-efficacy. Hesitant to seek help.",
                "delta": "Moderately above average self-confidence and belonging. Hesitant to seek help.",
                "echo": "Very high self-confidence and belonging. Positive about seeking help."
            }
            
            selected_persona = st.selectbox(
                "Choose a student persona:",
                personas,
                format_func=lambda x: f"{x.upper()} - {persona_descriptions[x][:50]}..."
            )
            
            # Display selected persona details
            if selected_persona:
                persona_info = STUDENT_PERSONAS[selected_persona]
                st.markdown(f"""
                **{selected_persona.upper()}**
                - **Description**: {persona_info['description']}
                - **Traits**: {persona_info['traits']}
                - **Style**: {persona_info['communication_style']}
                """)
            
            # Session controls
            st.header("🎮 Session Controls")
            if st.button("🔄 Start New Conversation"):
                st.session_state.messages = []
                st.session_state.student_intents = []
                st.session_state.advisor_intents = []
                st.rerun()
            
            if st.button("🏠 Back to Home"):
                st.session_state.show_training = False
                st.rerun()
        
        # Main chat interface
        st.header("💬 Training Conversation")
        
        # Display conversation history
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "student":
                # Student message with intent
                intent_info = st.session_state.student_intents[i] if i < len(st.session_state.student_intents) else {"intent": "Unknown", "confidence": 0.0}
                
                st.markdown(f"""
                <div class="chat-message student-message">
                    <strong>👨‍🎓 Student ({selected_persona.upper()}):</strong> {message["content"]}
                    <div>Classification Result: {intent_info["intent"]} • Confidence: {intent_info["confidence"]:.1%}</div>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                # Advisor message with intent
                advisor_idx = len([m for m in st.session_state.messages[:i+1] if m["role"] == "advisor"]) - 1
                intent_info = st.session_state.advisor_intents[advisor_idx] if advisor_idx < len(st.session_state.advisor_intents) else {"intent": "Unknown", "confidence": 0.0}
                
                st.markdown(f"""
                <div class="chat-message advisor-message">
                    <strong>👨‍🏫 You (Peer Advisor):</strong> {message["content"]}
                    <div>Classification Result: {intent_info["intent"]} • Confidence: {intent_info["confidence"]:.1%}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Generate initial student message if conversation is empty
        if not st.session_state.messages:
            if st.button("🎯 Start Conversation"):
                with st.spinner("Student is thinking..."):
                    opening_questions = [
                        "I'm interested in working with faculty on research projects, but I'm not sure how to approach professors. What's the best way to start?",
                        "I'm considering applying for internships, but I feel like I'm not ready yet. How do I know when I'm prepared?",
                        "I'm struggling with time management between classes and extracurricular activities. Do you have any advice?",
                        "I'm thinking about changing my major, but I'm worried about falling behind. What should I consider?",
                        "I want to get involved in engineering clubs, but I'm not sure which ones would be best for me."
                    ]
                    opening_question = random.choice(opening_questions)
                    st.session_state.messages.append({
                        "role": "student",
                        "content": opening_question,
                        "timestamp": datetime.now()
                    })
                    
                    # Analyze student intent
                    intent_result = classify_intent(opening_question, roberta_tokenizer, roberta_model)
                    st.session_state.student_intents.append(intent_result)
                    
                    st.rerun()
        
        # Advisor input
        if st.session_state.messages:
            advisor_input = st.text_area(
                "Your response as peer advisor:",
                height=100,
                placeholder="Type your response here..."
            )
            
            if st.button("📤 Send Response"):
                if advisor_input.strip():
                    # Add advisor message
                    st.session_state.messages.append({
                        "role": "advisor",
                        "content": advisor_input,
                        "timestamp": datetime.now()
                    })
                    
                    # Analyze advisor intent
                    intent_result = classify_intent(advisor_input, roberta_tokenizer, roberta_model)
                    st.session_state.advisor_intents.append(intent_result)
                    
                    # Generate student response using Llama
                    with st.spinner("🤖 Generating student response with Llama 3.1 8B..."):
                        try:
                            student_reply = generate_student_reply_with_llama(
                                context="",  # Could use conversation history
                                persona=selected_persona,
                                advisor_message=advisor_input,
                                llama_tokenizer=llama_tokenizer,
                                llama_model=llama_model
                            )
                            
                            # Add student response
                            st.session_state.messages.append({
                                "role": "student",
                                "content": student_reply,
                                "timestamp": datetime.now()
                            })
                            
                            # Analyze student intent
                            student_intent_result = classify_intent(student_reply, roberta_tokenizer, roberta_model)
                            st.session_state.student_intents.append(student_intent_result)
                            
                        except Exception as e:
                            st.error(f"Error generating student response: {str(e)}")
                    
                    st.rerun()
                else:
                    st.warning("Please enter a response before sending.")
        
        # Analysis section
        if st.session_state.messages:
            st.header("Conversation Analysis")
            
            # Calculate statistics
            student_intent_counts = {}
            advisor_intent_counts = {}
            
            for intent_info in st.session_state.student_intents:
                intent = intent_info["intent"]
                student_intent_counts[intent] = student_intent_counts.get(intent, 0) + 1
            
            for intent_info in st.session_state.advisor_intents:
                intent = intent_info["intent"]
                advisor_intent_counts[intent] = advisor_intent_counts.get(intent, 0) + 1
            
            # Display statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👨‍🎓 Student Intent Distribution")
                if student_intent_counts:
                    for intent, count in student_intent_counts.items():
                        st.write(f"• **{intent}**: {count} times")
                else:
                    st.write("No student messages yet.")
            
            with col2:
                st.subheader("👨‍🏫 Advisor Intent Distribution")
                if advisor_intent_counts:
                    for intent, count in advisor_intent_counts.items():
                        st.write(f"• **{intent}**: {count} times")
                else:
                    st.write("No advisor messages yet.")

if __name__ == "__main__":
    main()
