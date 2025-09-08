import streamlit as st
import os
import sys
from typing import Dict, Any, List
import json
from datetime import datetime
import random

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
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-left: 4px solid #4caf50;
        border: 1px solid #81c784;
        color: #2e7d32;
    }
    .advisor-message {
        background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
        border-left: 4px solid #2196f3;
        border: 1px solid #64b5f6;
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
    .cloud-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #5a67d8;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
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
    
    # More diverse responses based on persona and advisor intent
    if "feedback" in advisor_intent.lower() or "support" in advisor_intent.lower():
        responses = {
            "alpha": [
                "Thank you for the encouragement! I really appreciate your support. I'm feeling more confident about this now.",
                "That's exactly what I needed to hear. I'll definitely take your advice and keep working hard.",
                "I'm grateful for your help. This makes me feel more optimistic about my engineering journey.",
                "Your words really mean a lot to me. I was feeling uncertain, but now I feel more motivated.",
                "I appreciate you believing in me. I'll do my best to follow through on your suggestions."
            ],
            "beta": [
                "I really appreciate you saying that. It means a lot to me, even though I still feel uncertain.",
                "Thank you for being so understanding. I'm trying to believe in myself more.",
                "Your support helps, but I'm still worried about whether I can really succeed in engineering.",
                "I'm grateful for your patience with me. I know I can be difficult sometimes.",
                "Thank you for not giving up on me. I'll try to be more confident in my abilities."
            ],
            "delta": [
                "Thanks for the feedback! I'll definitely consider what you've said and see how it applies to my situation.",
                "I appreciate your perspective. Let me think about this and see how I can implement your suggestions.",
                "That's helpful advice. I'll work on incorporating that into my approach.",
                "Your input is valuable. I'll analyze this and see how it fits with my current strategy.",
                "Good point. I'll evaluate this feedback and determine the best way forward."
            ],
            "echo": [
                "Excellent! That's exactly the kind of guidance I was looking for. I'm excited to put this into practice.",
                "Perfect! I'm confident this approach will work well for me. Thanks for the great advice!",
                "That's fantastic! I love learning new strategies. I'm ready to take on this challenge.",
                "Outstanding! This is exactly what I needed. I'm energized and ready to implement this.",
                "Brilliant! I'm excited about the possibilities. This is going to be great!"
            ]
        }
    elif "understanding" in advisor_intent.lower() or "clarification" in advisor_intent.lower():
        responses = {
            "alpha": [
                "I'm still a bit confused about some details. Could you help me understand this better?",
                "I think I understand, but I want to make sure I've got it right. Could you clarify a bit more?",
                "I'm following along, but I'd like to make sure I understand completely. Could you explain that differently?",
                "I want to make sure I'm on the right track. Could you walk me through that again?",
                "I'm getting it, but I'd like to confirm my understanding. What's the key point I should focus on?"
            ],
            "beta": [
                "I'm not sure I understand completely. I don't want to seem stupid, but could you explain it differently?",
                "I'm still confused about this. Maybe I'm not cut out for engineering after all.",
                "I don't want to bother you with more questions, but I'm still struggling to understand.",
                "I'm sorry, but I'm still not getting it. Could you try a different approach?",
                "I feel like I'm missing something basic. Could you help me figure out what it is?"
            ],
            "delta": [
                "I see what you mean, but I'd like to make sure I understand correctly. Could you clarify?",
                "I think I get it, but let me make sure I've got the right approach. Could you confirm?",
                "I understand the general idea, but I want to make sure I'm implementing it correctly.",
                "That makes sense, but I want to verify my understanding. What's the most important aspect?",
                "I'm following your logic, but I'd like to confirm the key principles behind this approach."
            ],
            "echo": [
                "I think I understand, but let me make sure I've got it right. Could you confirm the key points?",
                "I'm following along well, but I want to make sure I'm not missing anything important.",
                "That makes sense! I just want to double-check that I'm approaching this the right way.",
                "I'm getting the concept, but I'd love to understand the deeper principles. Could you elaborate?",
                "This is fascinating! I want to make sure I understand all the nuances. What else should I know?"
            ]
        }
    elif "exploration" in advisor_intent.lower() or "reflection" in advisor_intent.lower():
        responses = {
            "alpha": [
                "That's an interesting perspective. I hadn't thought about it that way before. What made you consider this approach?",
                "I'm curious about this. Could you tell me more about how this has worked for other students?",
                "This is new to me. I'd like to explore this further. What resources would you recommend?",
                "That's a good question. I'm still figuring out what I want to focus on. What do you think would be most valuable?",
                "I'm interested in learning more about this. What's the best way for me to get started?"
            ],
            "beta": [
                "I'm not sure I understand all the options. Could you explain what each path would involve?",
                "I feel overwhelmed by all the choices. What would you recommend for someone who's just starting out?",
                "I'm worried I might make the wrong decision. How do I know which direction is right for me?",
                "This is all new to me. I'm not sure where to begin. Could you help me understand the basics?",
                "I'm feeling lost with all these options. What would be a good starting point for someone like me?"
            ],
            "delta": [
                "That's an interesting approach. I'm considering how this aligns with my long-term goals. What are your thoughts on the strategic implications?",
                "I appreciate the insight. I'm evaluating how this fits into my overall plan. What would you prioritize in my situation?",
                "Good point. I'm thinking about the best way to leverage this opportunity. What's your take on the timing?",
                "This is intriguing. I'm analyzing how this could benefit my career trajectory. What's your experience with this approach?",
                "That's a solid perspective. I'm considering the implementation strategy. What challenges should I anticipate?"
            ],
            "echo": [
                "That's exciting! I love exploring new possibilities. What other opportunities should I be looking into?",
                "This is exactly what I was hoping for! I'm energized by the potential. What's the next step I should take?",
                "Fantastic! I'm ready to dive in and make the most of this. What resources do you recommend I explore?",
                "This is perfect! I'm excited about all the possibilities. What would be the most ambitious goal I could set?",
                "Excellent! I'm ready to take this to the next level. What advanced strategies should I consider?"
            ]
        }
    elif "goal" in advisor_intent.lower() or "planning" in advisor_intent.lower():
        responses = {
            "alpha": [
                "I like the idea of having a plan. Could you help me break this down into smaller, manageable steps?",
                "That sounds like a good approach. What timeline do you think would be realistic for someone at my level?",
                "I want to make sure I'm setting realistic goals. What would you consider a good starting point for me?",
                "This planning approach makes sense. How do I know if my goals are appropriate for my current level?",
                "I appreciate the structured approach. What milestones should I be aiming for?"
            ],
            "beta": [
                "I'm not sure how to set realistic goals. What would be appropriate for someone at my level?",
                "I feel like my goals might be too ambitious. How do I know what's achievable?",
                "I'm worried about failing. What's a safe starting point that I can build from?",
                "I don't want to set myself up for disappointment. What would be a reasonable first goal?",
                "I'm nervous about committing to goals. How do I know I can actually achieve them?"
            ],
            "delta": [
                "I like the strategic approach. I'm thinking about how to structure this for maximum impact. What's your recommendation?",
                "That makes sense. I'm planning how to implement this effectively. What timeline would you suggest?",
                "Good framework. I'm considering the best way to execute this plan. What resources would you recommend?",
                "This is a solid plan. I'm analyzing the implementation strategy. What's the most critical success factor?",
                "Excellent approach. I'm considering the long-term implications. What should I prioritize first?"
            ],
            "echo": [
                "Excellent! I'm excited to create an ambitious plan. What would you consider a stretch goal for me?",
                "That's a great framework! I'm ready to set some challenging targets. What timeline would push me to grow?",
                "Perfect! I love having clear objectives. What would be the most impactful goals I could set?",
                "This is fantastic! I'm ready to set some really ambitious targets. What would be the ultimate goal?",
                "Outstanding! I'm excited about the possibilities. What would be the most challenging objective I could pursue?"
            ]
        }
    else:
        responses = {
            "alpha": [
                "That's interesting. I'd like to learn more about this topic and how it applies to my situation.",
                "I appreciate you sharing that with me. I'll think about how I can use this information.",
                "This is helpful. I'm going to consider what you've said and see how it fits with my goals.",
                "That's a good point. I hadn't considered that perspective before. Let me think about this.",
                "I'm interested in this approach. Could you tell me more about how it works in practice?"
            ],
            "beta": [
                "I'm not sure about this, but I'm trying to understand better. Maybe I can figure it out.",
                "I'm still learning about this, but I appreciate you taking the time to explain.",
                "I'm not confident about this yet, but I'll try to work through it.",
                "This is challenging for me, but I want to understand. Could you help me with the basics?",
                "I'm struggling with this concept, but I'm determined to learn. What should I focus on first?"
            ],
            "delta": [
                "I see. Let me think about this and see how it applies to my situation and goals.",
                "That's a good point. I'll consider this approach and see how it fits with my plans.",
                "I understand. Let me evaluate this and see how I can incorporate it into my strategy.",
                "That's a solid approach. I'm analyzing how this could benefit my overall plan.",
                "Good insight. I'm considering the implementation details and potential outcomes."
            ],
            "echo": [
                "That's a great point! I'm excited to explore this further and see how it can help me.",
                "Excellent! This is exactly the kind of information I was looking for. I'm ready to dive in.",
                "Perfect! I love learning about new approaches. I'm confident this will be valuable for me.",
                "This is fantastic! I'm energized by the possibilities. What's the next step?",
                "Outstanding! I'm ready to implement this right away. This is exactly what I needed!"
            ]
        }
    
    return random.choice(responses.get(persona, responses["alpha"]))

def main():
    # Header
    st.markdown('<h1 class="main-header">🎓 Peer Helper Training Chatbot</h1>', unsafe_allow_html=True)
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
    
    # Initialize show_training state
    if "show_training" not in st.session_state:
        st.session_state.show_training = False
    
    # Main content area
    if not st.session_state.show_training:
        # Show landing page
        st.markdown("""
        **1️⃣ Choose Your Training Scenario**  
        Select a student persona (Alpha, Beta, Delta, or Echo) based on the mentoring skills you want to practice
        
        **2️⃣ Start Conversation Training**  
        Engage in realistic dialogue with AI-powered student personas that respond based on authentic psychological profiles
        
        **3️⃣ Get Real-time Feedback**  
        Our system analyzes your responses using AI classification and provides instant feedback on communication patterns
        """)
        
        # Start Training Button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Training", type="primary", use_container_width=True):
                st.session_state.show_training = True
                st.rerun()
    else:
        # Show training interface
        with st.sidebar:
            st.header("👥 Choose Your Training Scenario")
            
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
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.student_intents = []
        st.session_state.advisor_intents = []
    
    # Main chat interface (only show in training mode)
    if st.session_state.show_training:
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
                    <br><br>
                    🎯 {intent_info["intent"]} • Confidence: {intent_info["confidence"]:.1%}
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
                    <br><br>
                    🎯 {intent_info["intent"]} • Confidence: {intent_info["confidence"]:.1%}
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
