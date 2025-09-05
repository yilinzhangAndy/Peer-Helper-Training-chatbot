import streamlit as st
import os
import sys
from typing import Dict, Any, List
import json
from datetime import datetime
import random

# Page configuration
st.set_page_config(
    page_title="MAE Peer Advisor Training System",
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
    .cloud-badge {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    .cloud-info {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Simple intent classifier for cloud deployment
class SimpleIntentClassifier:
    def __init__(self):
        self.intent_keywords = {
            "Exploration and Reflection": [
                "explore", "think", "consider", "wonder", "curious", "interest", 
                "research", "direction", "future", "career", "path"
            ],
            "Feedback and Support": [
                "help", "support", "encourage", "thank", "appreciate", "good", 
                "great", "excellent", "wonderful", "amazing"
            ],
            "Goal Setting and Planning": [
                "goal", "plan", "planning", "schedule", "timeline", "deadline", 
                "objective", "target", "aim", "strategy"
            ],
            "Problem Solving and Critical Thinking": [
                "problem", "issue", "challenge", "difficult", "struggle", 
                "solve", "solution", "fix", "trouble", "stuck"
            ],
            "Understanding and Clarification": [
                "understand", "clarify", "explain", "confused", "unclear", 
                "question", "ask", "what", "how", "why"
            ]
        }
    
    def classify(self, text):
        text_lower = text.lower()
        scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[intent] = score
        
        if not any(scores.values()):
            intent = "Understanding and Clarification"
            confidence = 0.5
        else:
            intent = max(scores, key=scores.get)
            confidence = min(0.9, 0.5 + (scores[intent] * 0.1))
        
        return {"intent": intent, "confidence": confidence}

# Student persona data
STUDENT_PERSONAS = {
    "alpha": {
        "description": "Moderately below average self-efficacy and sense of belonging. Positive about seeking help. Interested in clubs and faculty interaction, unsure about internships.",
        "traits": [
            "Works hard",
            "Average confidence in major choice", 
            "Willing to ask questions",
            "Interested in clubs/teams",
            "Unsure about internships"
        ],
        "help_seeking_behavior": "Well above average; not worried about asking for help.",
        "opening_questions": [
            "I'm considering applying for a research position, but I'm not sure if I have the right background. I'm willing to learn, but I don't want to waste a professor's time if I'm not qualified. How do I know if I'm ready?",
            "I've been thinking about joining some engineering clubs, but I'm not sure which ones would be best for someone like me. I want to get involved but I'm worried I might not fit in with the typical engineering student crowd. What clubs would you recommend?",
            "I'm doing okay in my classes, but I feel like I'm not as confident as some of my classmates. I'm willing to work hard and ask questions, but I'm not sure if I'm on the right track for a successful engineering career. How can I build more confidence?",
            "I'm interested in working with faculty on research projects, but I'm not sure how to approach professors. I don't want to seem like I'm bothering them, but I really want to get involved. What's the best way to start?",
            "I'm trying to decide whether to pursue an internship this summer. I think it would be valuable experience, but I'm worried I'm not ready yet. Some of my friends seem so much more prepared than I am. Should I wait until I'm more confident?"
        ]
    },
    "beta": {
        "description": "Very low sense of belonging and self-efficacy. Hesitant to seek help, avoids faculty and clubs, unsure about major.",
        "traits": [
            "Low confidence",
            "Avoids asking questions", 
            "Sensitive to peer perception",
            "Avoids clubs and faculty",
            "Some interest in research"
        ],
        "help_seeking_behavior": "Well below average; embarrassed to ask for help.",
        "opening_questions": [
            "I'm really struggling in my classes and I don't know what to do. I feel like everyone else understands the material except me, but I'm too embarrassed to ask for help. I don't want my classmates to think I'm stupid. Should I just try to figure it out on my own?",
            "I'm starting to think I made a mistake choosing engineering. The classes are so much harder than I expected, and I don't feel like I belong here. Everyone else seems so confident and smart. Maybe I should switch to something easier?",
            "I've been avoiding going to office hours because I'm afraid the professor will think I'm not smart enough for this major. But I'm really falling behind in my coursework. I don't know how to get help without feeling embarrassed.",
            "I see other students joining clubs and getting involved, but I just don't feel comfortable in those social situations. I'm worried people will judge me or think I'm not good enough. Is it okay if I just focus on my classes?",
            "I failed my last exam and I'm really discouraged. I studied hard, but I still didn't do well. I'm starting to doubt if I can handle this major. Should I consider switching to something else?"
        ]
    },
    "delta": {
        "description": "Moderately above average self-confidence and belonging. Hesitant to seek help, not interested in research, open to clubs/internships.",
        "traits": [
            "Good self-confidence",
            "Worries about others' opinions", 
            "Not interested in research",
            "Open to clubs and internships",
            "Prefers practical applications"
        ],
        "help_seeking_behavior": "Below average; hesitant to seek help.",
        "opening_questions": [
            "I'm doing well in my classes, but I'm not sure if I'm taking the right approach to my engineering education. I want to make sure I'm preparing myself for a successful career. What should I be focusing on?",
            "I'm interested in getting some hands-on experience through internships, but I'm not sure how to go about finding opportunities. I want to make sure I'm competitive when I apply. Any advice?",
            "I've been thinking about joining some engineering clubs, but I'm not sure which ones would be most beneficial for my career goals. I want to make the most of my time here. What would you recommend?",
            "I'm trying to decide between different engineering specializations. I want to choose something that will lead to good job opportunities, but I also want to make sure I'll enjoy the work. How can I explore my options?",
            "I'm concerned about the job market and whether I'll be competitive when I graduate. What should I be doing now to prepare for my career and make myself stand out to employers?"
        ]
    },
    "echo": {
        "description": "Very high self-confidence and belonging. Positive about seeking help, interested in research and internships, club interest is average.",
        "traits": [
            "Very confident",
            "Strong sense of belonging", 
            "Asks for help freely",
            "Interested in research",
            "Active in internships"
        ],
        "help_seeking_behavior": "Above average; asks for help without concern.",
        "opening_questions": [
            "I'm really excited about the research opportunities in MAE! I've been looking into different labs and I'm interested in several areas. How can I best prepare myself to be competitive for research positions?",
            "I want to make the most of my time here and I'm interested in both research and industry experience. How can I balance these interests and build a strong foundation for my future career?",
            "I'm thinking about pursuing graduate school after my bachelor's degree. What should I be doing now to prepare for that path and make myself a strong candidate?",
            "I'm interested in getting involved in some leadership roles in engineering organizations. I want to develop my leadership skills and make a positive impact. What opportunities would you recommend?",
            "I'm really passionate about engineering and I want to explore different career paths. I'm interested in both technical and non-technical roles. How can I learn more about the various opportunities available?"
        ]
    }
}

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
    try:
        result = intent_classifier.classify(text)
        return {
            "intent": result.get("intent", "Unknown"),
            "confidence": result.get("confidence", 0.0)
        }
    except Exception as e:
        return {"intent": "Understanding and Clarification", "confidence": 0.5}

def generate_student_reply(context: str, persona: str, advisor_intent: str) -> str:
    """Generate student reply based on persona and context"""
    persona_info = STUDENT_PERSONAS.get(persona, STUDENT_PERSONAS["alpha"])
    
    # Simple response generation based on persona and advisor intent
    if "feedback" in advisor_intent.lower() or "support" in advisor_intent.lower():
        responses = {
            "alpha": [
                "Thank you for the encouragement! I really appreciate your support. I'm feeling more confident about this now.",
                "That's exactly what I needed to hear. I'll definitely take your advice and keep working hard.",
                "I'm grateful for your help. This makes me feel more optimistic about my engineering journey."
            ],
            "beta": [
                "I really appreciate you saying that. It means a lot to me, even though I still feel uncertain.",
                "Thank you for being so understanding. I'm trying to believe in myself more.",
                "Your support helps, but I'm still worried about whether I can really succeed in engineering."
            ],
            "delta": [
                "Thanks for the feedback! I'll definitely consider what you've said and see how it applies to my situation.",
                "I appreciate your perspective. Let me think about this and see how I can implement your suggestions.",
                "That's helpful advice. I'll work on incorporating that into my approach."
            ],
            "echo": [
                "Excellent! That's exactly the kind of guidance I was looking for. I'm excited to put this into practice.",
                "Perfect! I'm confident this approach will work well for me. Thanks for the great advice!",
                "That's fantastic! I love learning new strategies. I'm ready to take on this challenge."
            ]
        }
    elif "understanding" in advisor_intent.lower() or "clarification" in advisor_intent.lower():
        responses = {
            "alpha": [
                "I'm still a bit confused about some details. Could you help me understand this better?",
                "I think I understand, but I want to make sure I've got it right. Could you clarify a bit more?",
                "I'm following along, but I'd like to make sure I understand completely. Could you explain that differently?"
            ],
            "beta": [
                "I'm not sure I understand completely. I don't want to seem stupid, but could you explain it differently?",
                "I'm still confused about this. Maybe I'm not cut out for engineering after all.",
                "I don't want to bother you with more questions, but I'm still struggling to understand."
            ],
            "delta": [
                "I see what you mean, but I'd like to make sure I understand correctly. Could you clarify?",
                "I think I get it, but let me make sure I've got the right approach. Could you confirm?",
                "I understand the general idea, but I want to make sure I'm implementing it correctly."
            ],
            "echo": [
                "I think I understand, but let me make sure I've got it right. Could you confirm the key points?",
                "I'm following along well, but I want to make sure I'm not missing anything important.",
                "That makes sense! I just want to double-check that I'm approaching this the right way."
            ]
        }
    else:
        responses = {
            "alpha": [
                "That's interesting. I'd like to learn more about this topic and how it applies to my situation.",
                "I appreciate you sharing that with me. I'll think about how I can use this information.",
                "This is helpful. I'm going to consider what you've said and see how it fits with my goals."
            ],
            "beta": [
                "I'm not sure about this, but I'm trying to understand better. Maybe I can figure it out.",
                "I'm still learning about this, but I appreciate you taking the time to explain.",
                "I'm not confident about this yet, but I'll try to work through it."
            ],
            "delta": [
                "I see. Let me think about this and see how it applies to my situation and goals.",
                "That's a good point. I'll consider this approach and see how it fits with my plans.",
                "I understand. Let me evaluate this and see how I can incorporate it into my strategy."
            ],
            "echo": [
                "That's a great point! I'm excited to explore this further and see how it can help me.",
                "Excellent! This is exactly the kind of information I was looking for. I'm ready to dive in.",
                "Perfect! I love learning about new approaches. I'm confident this will be valuable for me."
            ]
        }
    
    return random.choice(responses.get(persona, responses["alpha"]))

def main():
    # Header
    st.markdown('<h1 class="main-header">🎓 MAE Peer Advisor Training System</h1>', unsafe_allow_html=True)
    st.markdown('<div class="cloud-badge">☁️ Cloud Version - Free & Global Access</div>', unsafe_allow_html=True)
    
    # Cloud info
    st.markdown("""
    <div class="cloud-info">
        <h4>🌐 Cloud Features</h4>
        <ul>
            <li><strong>Global Access:</strong> Available worldwide 24/7</li>
            <li><strong>Free to Use:</strong> No registration required</li>
            <li><strong>Privacy Protected:</strong> All processing happens securely</li>
            <li><strong>Academic Research:</strong> Designed for MAE education</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Load components
    with st.spinner("Loading AI components..."):
        intent_classifier = SimpleIntentClassifier()
    
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
            persona_info = STUDENT_PERSONAS[selected_persona]
            st.markdown(f"""
            <div class="persona-card">
                <h4>{selected_persona.upper()}</h4>
                <p><strong>Description:</strong> {persona_info['description']}</p>
                <p><strong>Traits:</strong> {', '.join(persona_info['traits'])}</p>
                <p><strong>Help Seeking:</strong> {persona_info['help_seeking_behavior']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Cloud features
        st.header("☁️ Cloud Features")
        st.markdown("""
        - ✅ **Global Access**: Available worldwide
        - ✅ **Free to Use**: No costs or limits
        - ✅ **Privacy Protected**: Secure processing
        - ✅ **Academic Research**: MAE education focus
        - ✅ **Real-time Analysis**: Intent classification
        - ✅ **Multi-turn Dialogue**: Interactive training
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
                opening_questions = STUDENT_PERSONAS[selected_persona]["opening_questions"]
                opening_question = random.choice(opening_questions)
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
                with st.spinner("☁️ Generating student response..."):
                    try:
                        # Get recent conversation context
                        recent_messages = st.session_state.messages[-4:]
                        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
                        
                        # Generate student reply
                        student_reply = generate_student_reply(
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
