import streamlit as st
import os
import sys
from typing import Dict, Any, List
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our chatbot components
from models.intent_classifier import IntentClassifier
from student_persona_manager import StudentPersonaManager
from local_llm_integration import FreeChatbotPipeline

# Page configuration
st.set_page_config(
    page_title="MAE Peer Advisor Training System (Free)",
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
    .free-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .student-message {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
    .advisor-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .intent-exploration { background-color: #ffeb3b; color: #000; }
    .intent-feedback { background-color: #4caf50; color: #fff; }
    .intent-goal { background-color: #ff9800; color: #fff; }
    .intent-problem { background-color: #f44336; color: #fff; }
    .intent-understanding { background-color: #9c27b0; color: #fff; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_components():
    """Load chatbot components with caching"""
    try:
        # Load intent classifier with model path
        model_path = "../pre-train/balanced_finetuned_model"
        intent_classifier = IntentClassifier(model_path)
        
        # Load student persona manager
        spm = StudentPersonaManager()
        
        # Load free chatbot pipeline
        pipeline = FreeChatbotPipeline()
        
        return intent_classifier, spm, pipeline
    except Exception as e:
        st.error(f"Error loading components: {str(e)}")
        return None, None, None

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

def analyze_intent(text: str, intent_classifier, role: str) -> Dict[str, Any]:
    """Analyze intent of a message"""
    if not intent_classifier:
        return {"intent": "Unknown", "confidence": 0.0}
    
    try:
        result = intent_classifier.classify(text)
        return {
            "intent": result.get("intent", "Unknown"),
            "confidence": result.get("confidence", 0.0)
        }
    except Exception as e:
        st.error(f"Intent analysis error: {str(e)}")
        return {"intent": "Error", "confidence": 0.0}

def main():
    # Header
    st.markdown('<h1 class="main-header">🎓 MAE Peer Advisor Training System</h1>', unsafe_allow_html=True)
    st.markdown('<div class="free-badge">🆓 100% FREE - No API Costs - Local Processing</div>', unsafe_allow_html=True)
    
    # Load components
    with st.spinner("Loading AI components..."):
        intent_classifier, spm, pipeline = load_components()
    
    if not all([intent_classifier, spm, pipeline]):
        st.error("Failed to load system components. Please check your setup.")
        return
    
    # Sidebar for persona selection
    with st.sidebar:
        st.header("🎭 Student Persona Selection")
        
        # Display persona options
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
            persona_info = spm.get_persona(selected_persona)
            st.markdown(f"""
            <div class="persona-card">
                <h4>{selected_persona.upper()}</h4>
                <p><strong>Description:</strong> {persona_info['description']}</p>
                <p><strong>Traits:</strong> {persona_info['traits']}</p>
                <p><strong>Help Seeking:</strong> {persona_info['help_seeking_behavior']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Free version info
        st.header("🆓 Free Version Features")
        st.markdown("""
        - ✅ No API costs
        - ✅ Local processing
        - ✅ 4 student personas
        - ✅ Intent classification
        - ✅ Multi-turn dialogue
        - ✅ Conversation analysis
        - ✅ Privacy protected
        """)
        
        # Session controls
        st.header("🎮 Session Controls")
        if st.button("🔄 Start New Conversation"):
            st.session_state.messages = []
            st.session_state.student_intents = []
            st.session_state.advisor_intents = []
            st.rerun()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.student_intents = []
        st.session_state.advisor_intents = []
    
    # Main chat interface
    st.header("💬 Training Conversation")
    
    # Display conversation history
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "student":
            # Student message with intent
            intent_info = st.session_state.student_intents[i] if i < len(st.session_state.student_intents) else {"intent": "Unknown", "confidence": 0.0}
            intent_class = get_intent_badge_class(intent_info["intent"])
            
            st.markdown(f"""
            <div class="chat-message student-message">
                <strong>👨‍🎓 Student ({selected_persona.upper()}):</strong> {message["content"]}
                <span class="intent-badge {intent_class}">
                    {intent_info["intent"]} ({intent_info["confidence"]:.2f})
                </span>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # Advisor message with intent
            advisor_idx = len([m for m in st.session_state.messages[:i+1] if m["role"] == "advisor"]) - 1
            intent_info = st.session_state.advisor_intents[advisor_idx] if advisor_idx < len(st.session_state.advisor_intents) else {"intent": "Unknown", "confidence": 0.0}
            intent_class = get_intent_badge_class(intent_info["intent"])
            
            st.markdown(f"""
            <div class="chat-message advisor-message">
                <strong>👨‍🏫 You (Peer Advisor):</strong> {message["content"]}
                <span class="intent-badge {intent_class}">
                    {intent_info["intent"]} ({intent_info["confidence"]:.2f})
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    # Generate initial student message if conversation is empty
    if not st.session_state.messages:
        if st.button("🎯 Start Conversation"):
            with st.spinner("Student is thinking..."):
                opening_question = spm.get_random_opening_question(selected_persona)
                st.session_state.messages.append({
                    "role": "student",
                    "content": opening_question,
                    "timestamp": datetime.now()
                })
                
                # Analyze student intent
                intent_result = analyze_intent(opening_question, intent_classifier, "student")
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
                intent_result = analyze_intent(advisor_input, intent_classifier, "advisor")
                st.session_state.advisor_intents.append(intent_result)
                
                # Generate student response
                with st.spinner("Student is thinking..."):
                    try:
                        # Get recent conversation context
                        recent_messages = st.session_state.messages[-4:]
                        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
                        
                        # Generate student reply using free pipeline
                        student_reply = pipeline.generate_student_reply(
                            context=context,
                            persona=selected_persona,
                            advisor_intent=intent_result["intent"]
                        )
                        
                        # Add student response
                        st.session_state.messages.append({
                            "role": "student",
                            "content": student_reply,
                            "timestamp": datetime.now()
                        })
                        
                        # Analyze student intent
                        student_intent_result = analyze_intent(student_reply, intent_classifier, "student")
                        st.session_state.student_intents.append(student_intent_result)
                        
                    except Exception as e:
                        st.error(f"Error generating student response: {str(e)}")
                        # Add a fallback response
                        st.session_state.messages.append({
                            "role": "student",
                            "content": "I'm not sure how to respond to that. Could you help me understand better?",
                            "timestamp": datetime.now()
                        })
                        st.session_state.student_intents.append({"intent": "Understanding and Clarification", "confidence": 0.5})
                
                st.rerun()
            else:
                st.warning("Please enter a response before sending.")
    
    # Analysis section
    if st.session_state.messages:
        st.header("📊 Conversation Analysis")
        
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
        
        # Q→A pair analysis
        st.subheader("🔄 Question-Answer Pair Analysis")
        same_intent_pairs = 0
        different_intent_pairs = 0
        
        for i in range(1, len(st.session_state.messages)):
            if (st.session_state.messages[i-1]["role"] == "student" and 
                st.session_state.messages[i]["role"] == "advisor"):
                
                student_idx = len([m for m in st.session_state.messages[:i] if m["role"] == "student"]) - 1
                advisor_idx = len([m for m in st.session_state.messages[:i+1] if m["role"] == "advisor"]) - 1
                
                if (student_idx < len(st.session_state.student_intents) and 
                    advisor_idx < len(st.session_state.advisor_intents)):
                    
                    student_intent = st.session_state.student_intents[student_idx]["intent"]
                    advisor_intent = st.session_state.advisor_intents[advisor_idx]["intent"]
                    
                    if student_intent == advisor_intent:
                        same_intent_pairs += 1
                    else:
                        different_intent_pairs += 1
        
        st.write(f"• **Same intent pairs**: {same_intent_pairs}")
        st.write(f"• **Different intent pairs**: {different_intent_pairs}")

if __name__ == "__main__":
    main()
