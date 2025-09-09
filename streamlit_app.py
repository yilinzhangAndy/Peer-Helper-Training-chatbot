import streamlit as st
import os
import sys
from typing import Dict, Any, List
import json
from datetime import datetime
import random
import requests

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
</style>
""", unsafe_allow_html=True)

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

def _get_hf_token() -> str:
    """Get Hugging Face token from Streamlit secrets or environment"""
    try:
        return st.secrets.get("HF_TOKEN", "")
    except Exception:
        return os.getenv("HF_TOKEN", "")

def generate_student_reply_with_hf_api(advisor_message: str, persona: str) -> str:
    """Generate student reply using Hugging Face Inference API with Llama 3.1 8B"""
    try:
        token = _get_hf_token()
        if not token:
            # Fallback to rule-based if no token
            return generate_student_reply_fallback(advisor_message, persona)
        
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct"
        
        # Create persona-specific prompt
        persona_info = STUDENT_PERSONAS.get(persona, {})
        persona_description = persona_info.get("description", "")
        persona_traits = persona_info.get("traits", "")
        persona_style = persona_info.get("communication_style", "")
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a {persona} student in an engineering program. Your characteristics:
- Description: {persona_description}
- Traits: {persona_traits}
- Communication style: {persona_style}

Respond naturally as this student would, staying in character. Keep responses conversational and authentic. Respond in 1-2 sentences.<|eot_id|><|start_header_id|>user<|end_header_id|>

The peer advisor just said: "{advisor_message}"

How would you respond as a {persona} student?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get('generated_text', '').strip()
            if generated_text:
                return generated_text
        
        # Fallback if API response is empty
        return generate_student_reply_fallback(advisor_message, persona)
        
    except Exception as e:
        st.warning(f"HF API failed: {str(e)}. Using fallback response.")
        return generate_student_reply_fallback(advisor_message, persona)

def generate_student_reply_fallback(advisor_message: str, persona: str) -> str:
    """Fallback rule-based student reply generation with more variety"""
    try:
        # Enhanced responses with more variety and context awareness
        responses = {
            "alpha": [
                "That sounds like a good plan! I'm excited to work on this. Could you help me break this down into smaller steps?",
                "I really appreciate your guidance. I want to make sure I'm on the right track - what should I focus on first?",
                "This is exactly what I needed to hear! I'm feeling more confident about my direction now. How do I get started?",
                "Thank you for the clear direction! I'm ready to take action. What would be the best way to begin?",
                "I love how structured this approach is! I'm motivated to start working on these goals. Can you help me prioritize?",
                "I'm following along, but I'd like to make sure I understand completely. Could you explain that differently?",
                "This is really helpful! I'm starting to see the connections. What would be the next step in this process?",
                "I appreciate you breaking this down for me. I think I understand, but could you give me an example?",
                "This makes a lot of sense now! I'm feeling more confident about tackling this problem. How should I approach it?",
                "Thank you for the clear explanation! I'm ready to try this approach. What should I do if I run into issues?"
            ],
            "beta": [
                "I'm not sure if I'm ready for this level of planning. I feel like I might be getting ahead of myself. What do you think?",
                "This sounds overwhelming to me. I'm worried I might not be able to follow through. Could we start smaller?",
                "I appreciate the guidance, but I'm feeling uncertain about my ability to achieve these goals. Is this realistic for me?",
                "I want to try, but I'm afraid I might fail. Do you think someone like me can really do this?",
                "This seems like a lot to take on. I'm not sure I have the confidence to pursue such ambitious goals. What would you suggest?",
                "I'm trying to understand, but I feel like I'm missing something. Could you explain it in simpler terms?",
                "I'm sorry, but I'm still confused. I don't want to waste your time, but could you help me understand better?",
                "I feel like I should understand this, but I'm struggling. Am I overthinking this?",
                "I'm worried I'm not smart enough to figure this out. Could you break it down even more?",
                "I don't want to seem stupid, but I'm having trouble following. Could you help me step by step?"
            ],
            "delta": [
                "This is a solid approach. I can see the strategic value in this plan. What are the potential risks I should consider?",
                "I appreciate the structured approach. I want to make sure I'm considering all angles. What contingencies should I plan for?",
                "This makes sense from a planning perspective. I'm thinking about the long-term implications. How does this align with my overall strategy?",
                "I like the systematic nature of this plan. I want to ensure I'm not missing any important factors. What should I prioritize?",
                "This is a well-thought-out approach. I'm considering the practical implementation. What resources will I need to succeed?",
                "I can see the logic in this approach. Let me think through the implications. What are the potential outcomes of this solution?",
                "This is an interesting problem-solving strategy. I'm analyzing the different components. How do these elements work together?",
                "I appreciate the analytical approach. I'm considering the cause-and-effect relationships. What factors should I monitor?",
                "This solution makes sense logically. I'm thinking about the broader context. How does this fit into the bigger picture?",
                "I can follow the reasoning here. I want to understand the underlying principles. What are the key assumptions in this approach?"
            ],
            "echo": [
                "This is exactly what I was looking for! I'm excited to dive into this plan. What's the first step I should take?",
                "Perfect! I love how ambitious and well-structured this approach is. I'm ready to tackle this challenge. How can I get started immediately?",
                "This is fantastic guidance! I'm feeling energized and motivated. What resources do I need to make this happen?",
                "Excellent! I'm confident I can achieve these goals. I want to make sure I'm maximizing my potential. What's the best way to proceed?",
                "This is exactly the kind of challenge I thrive on! I'm ready to take this to the next level. How can I exceed expectations?",
                "This is a brilliant approach! I can see how this will solve the problem effectively. What's the implementation timeline?",
                "Excellent problem-solving strategy! I'm excited to apply this methodology. How can I adapt this to other challenges?",
                "This is exactly the kind of analytical thinking I enjoy! I'm ready to implement this solution. What are the next steps?",
                "Perfect! I love how systematic and thorough this approach is. I'm confident this will work. How can I optimize the process?",
                "This is outstanding! I'm impressed by the depth of analysis. I want to master this approach. What advanced techniques should I learn?"
            ]
        }
        
        # Get responses for the specific persona
        persona_responses = responses.get(persona, responses["alpha"])
        
        # Add some randomness to avoid exact repetition
        import time
        random.seed(int(time.time() * 1000) % 10000)
        
        return random.choice(persona_responses)
        
    except Exception as e:
        return "I'm not sure how to respond to that. Could you help me understand better?"

def analyze_intent(text: str, intent_classifier, role: str) -> Dict[str, Any]:
    """Analyze intent using HF API or fallback classifier"""
    try:
        # Try HF API first
        try:
            hf_result = hf_classify_via_api(text)
            if isinstance(hf_result.get("intent"), str):
                return {"intent": hf_result.get("intent", "Unknown"),
                        "confidence": hf_result.get("confidence", 0.0)}
        except Exception:
            pass  # Fallback to simple classifier if HF API fails
        
        # Fallback to simple classifier
        result = intent_classifier.classify(text)
        return {"intent": result.get("intent", "Unknown"),
                "confidence": result.get("confidence", 0.0)}
    except Exception:
        return {"intent": "Understanding and Clarification", "confidence": 0.5}

def hf_classify_via_api(text: str) -> Dict[str, Any]:
    """Classify intent using Hugging Face Inference API"""
    try:
        token = _get_hf_token()
        if not token:
            raise RuntimeError("HF token not configured")
        
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api-inference.huggingface.co/models/zylandy/mae-intent-classifier"
        
        payload = {"inputs": text}
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, list):
            candidates = data[0] if data and isinstance(data[0], list) else data
        else:
            raise ValueError("Unexpected HF response format")
        
        if not candidates:
            raise ValueError("Empty HF response")
        
        top = max(candidates, key=lambda x: x.get("score", 0.0))
        return {"intent": top.get("label", "Understanding and Clarification"),
                "confidence": float(top.get("score", 0.5))}
    except Exception as e:
        raise RuntimeError(f"HF API classification failed: {str(e)}")

class SimpleIntentClassifier:
    def __init__(self):
        # Comprehensive keyword lists for each category
        self.intent_keywords = {
            "Goal Setting and Planning": [
                # Academic planning
                'goal', 'goals', 'objective', 'objectives', 'target', 'targets', 'aim', 'aims',
                'plan', 'planning', 'schedule', 'timeline', 'roadmap', 'pathway', 'strategy',
                'course', 'courses', 'curriculum', 'semester', 'year', 'graduation', 'graduate',
                'degree', 'major', 'minor', 'specialization', 'concentration', 'track',
                'prerequisite', 'prerequisites', 'requirement', 'requirements', 'credit', 'credits',
                
                # Career planning
                'career', 'profession', 'job', 'internship', 'co-op', 'employment', 'work',
                'industry', 'company', 'organization', 'position', 'role', 'opportunity',
                'resume', 'cv', 'portfolio', 'application', 'interview', 'networking',
                'skill', 'skills', 'competency', 'competencies', 'qualification', 'certification',
                
                # Time management & structure
                'deadline', 'due date', 'priority', 'priorities', 'organize', 'structure',
                'milestone', 'milestones', 'step', 'steps', 'phase', 'stages', 'progress',
                'achieve', 'accomplish', 'attain', 'reach', 'complete', 'finish',
                
                # Future orientation
                'future', 'next', 'upcoming', 'long-term', 'short-term', 'eventually',
                'aspire', 'aspiration', 'vision', 'dream', 'hope', 'intention', 'want to',
                'going to', 'will', 'shall', 'expect', 'anticipate'
            ],
            
            "Problem Solving and Critical Thinking": [
                # Problem identification
                'problem', 'problems', 'issue', 'issues', 'challenge', 'challenges', 'difficulty',
                'difficulties', 'obstacle', 'obstacles', 'barrier', 'barriers', 'trouble',
                'struggle', 'conflict', 'dilemma', 'concern', 'worry', 'question',
                
                # Analysis & thinking
                'analysis', 'analyze', 'analytical', 'examine', 'evaluate', 'assessment',
                'consider', 'think', 'thinking', 'reason', 'reasoning', 'logic', 'logical',
                'critical', 'systematic', 'methodical', 'approach', 'method', 'methodology',
                'process', 'procedure', 'technique', 'framework', 'model',
                
                # Solution development
                'solution', 'solutions', 'solve', 'resolve', 'fix', 'address', 'handle',
                'deal with', 'tackle', 'approach', 'strategy', 'strategies', 'plan',
                'alternative', 'alternatives', 'option', 'options', 'choice', 'choices',
                'decision', 'decide', 'determine', 'figure out', 'work out',
                
                # Engineering specific
                'design', 'algorithm', 'calculation', 'formula', 'equation', 'code', 'coding',
                'debug', 'troubleshoot', 'optimize', 'efficiency', 'performance',
                'test', 'testing', 'experiment', 'simulation', 'model', 'prototype',
                
                # Cognitive processes
                'brainstorm', 'creativity', 'innovative', 'research', 'investigation',
                'hypothesis', 'theory', 'concept', 'principle', 'assumption',
                'compare', 'contrast', 'synthesize', 'integrate', 'pattern', 'trend'
            ],
            
            "Understanding and Clarification": [
                # Seeking understanding
                'understand', 'understanding', 'comprehend', 'grasp', 'get it', 'see',
                'realize', 'recognize', 'know', 'learn', 'figure out', 'make sense',
                'clear', 'unclear', 'confused', 'confusing', 'puzzled', 'lost',
                
                # Requesting explanation
                'explain', 'explanation', 'clarify', 'clarification', 'define', 'definition',
                'describe', 'description', 'elaborate', 'detail', 'specify', 'illustrate',
                'example', 'examples', 'instance', 'demonstrate', 'show', 'tell',
                'what', 'how', 'why', 'when', 'where', 'which', 'who',
                
                # Information seeking
                'question', 'questions', 'ask', 'asking', 'wonder', 'wondering',
                'curious', 'unsure', 'uncertain', 'doubt', 'confirm', 'verification',
                'check', 'verify', 'validate', 'ensure', 'make sure',
                'information', 'detail', 'details', 'fact', 'facts', 'data',
                
                # Learning process
                'study', 'studying', 'read', 'reading', 'review', 'revise', 'practice',
                'exercise', 'homework', 'assignment', 'material', 'content', 'topic',
                'subject', 'concept', 'theory', 'principle', 'rule', 'guideline',
                
                # Communication
                'mean', 'meaning', 'interpret', 'interpretation', 'translate',
                'paraphrase', 'rephrase', 'repeat', 'summarize', 'summary',
                'context', 'background', 'basis', 'foundation', 'fundamental'
            ],
            
            "Feedback and Support": [
                # Positive feedback
                'good', 'great', 'excellent', 'outstanding', 'impressive', 'wonderful',
                'amazing', 'fantastic', 'brilliant', 'perfect', 'right', 'correct',
                'well done', 'nice job', 'keep up', 'proud', 'congratulations',
                'success', 'successful', 'achievement', 'accomplish', 'progress',
                
                # Constructive feedback
                'feedback', 'advice', 'suggestion', 'suggestions', 'recommend', 'recommendation',
                'improve', 'improvement', 'better', 'enhance', 'strengthen', 'develop',
                'consider', 'try', 'attempt', 'practice', 'work on', 'focus on',
                'change', 'modify', 'adjust', 'revise', 'edit', 'correction',
                
                # Emotional support
                'support', 'supportive', 'encourage', 'encouragement', 'motivate', 'motivation',
                'inspire', 'inspiration', 'confidence', 'believe', 'trust', 'faith',
                'comfort', 'reassure', 'calm', 'relax', 'stress', 'pressure',
                'worry', 'anxiety', 'fear', 'nervous', 'overwhelmed', 'difficult',
                
                # Help and guidance
                'help', 'helping', 'assist', 'assistance', 'aid', 'guidance', 'guide',
                'mentor', 'coach', 'tutor', 'teach', 'instruct', 'train', 'direct',
                'lead', 'show', 'demonstrate', 'model', 'example', 'resource', 'tool',
                
                # Validation and empathy
                'understand', 'normal', 'common', 'typical', 'natural', 'okay',
                'fine', 'alright', 'valid', 'reasonable', 'legitimate', 'justified',
                'feel', 'feeling', 'emotion', 'experience', 'situation', 'challenge',
                'struggle', 'difficulty', 'hard', 'tough', 'overwhelming', 'stressful',
                
                # Relationship building
                'care', 'concern', 'listen', 'hear', 'respect', 'appreciate',
                'value', 'important', 'matter', 'significant', 'worthwhile'
            ],
            
            "Exploration and Reflection": [
                # Self-reflection
                'reflect', 'reflection', 'reflective', 'think about', 'consider',
                'contemplate', 'ponder', 'meditate', 'introspect', 'self-examine',
                'look back', 'review', 'evaluate', 'assess', 'analyze yourself',
                'personal', 'self', 'own', 'individual', 'unique', 'perspective',
                
                # Self-awareness
                'self-awareness', 'self-knowledge', 'identity', 'personality', 'character',
                'values', 'beliefs', 'principles', 'philosophy', 'worldview',
                'strength', 'strengths', 'weakness', 'weaknesses', 'limitation',
                'ability', 'abilities', 'talent', 'gift', 'potential', 'capacity',
                
                # Exploration and discovery
                'explore', 'exploration', 'discover', 'discovery', 'investigate',
                'examine', 'research', 'study', 'learn about', 'find out',
                'curious', 'curiosity', 'wonder', 'question', 'possibility',
                'opportunity', 'option', 'alternative', 'path', 'direction',
                
                # Growth and development
                'grow', 'growth', 'develop', 'development', 'evolve', 'change',
                'transform', 'transformation', 'progress', 'advance', 'improve',
                'learn', 'learning', 'experience', 'journey', 'process', 'stage',
                
                # Career and life exploration
                'career', 'profession', 'field', 'industry', 'area', 'domain',
                'interest', 'interests', 'passion', 'passionate', 'love', 'enjoy',
                'fulfill', 'fulfillment', 'satisfaction', 'purpose', 'meaning',
                'calling', 'vocation', 'life', 'lifestyle', 'balance', 'priorities',
                
                # Future thinking
                'future', 'vision', 'dream', 'aspiration', 'goal', 'hope',
                'imagine', 'envision', 'picture', 'see yourself', 'become',
                'want to be', 'wish', 'desire', 'ambition', 'plan', 'intention',
                
                # Questioning and wondering
                'what if', 'suppose', 'imagine', 'consider', 'think about',
                'wonder', 'curious', 'question', 'doubt', 'uncertain',
                'maybe', 'perhaps', 'possibly', 'might', 'could', 'would'
            ]
        }
        
        # High priority multi-word phrases (given extra weight)
        self.high_priority_keywords = {
            "Goal Setting and Planning": [
                'academic plan', 'graduation plan', 'career path', 'course selection',
                'degree plan', 'study plan', 'time management', 'goal setting',
                'career goals', 'academic goals', 'long term goals', 'short term goals',
                'internship application', 'job search', 'skill development'
            ],
            "Problem Solving and Critical Thinking": [
                'problem solving', 'critical thinking', 'analytical thinking',
                'troubleshooting', 'decision making', 'root cause', 'systematic approach',
                'engineering design', 'design process', 'solution development',
                'critical analysis', 'logical reasoning', 'problem analysis'
            ],
            "Understanding and Clarification": [
                'detailed explanation', 'clarify confusion', 'help me understand',
                'what does this mean', 'can you explain', 'i dont understand',
                'make it clear', 'break it down', 'step by step', 'in simple terms',
                'for example', 'what exactly', 'how does this work'
            ],
            "Feedback and Support": [
                'constructive feedback', 'personalized advice', 'emotional support',
                'positive reinforcement', 'encouragement', 'you can do it',
                'keep going', 'dont give up', 'believe in yourself', 'well done',
                'good job', 'making progress', 'on the right track'
            ],
            "Exploration and Reflection": [
                'self reflection', 'career exploration', 'personal growth',
                'self awareness', 'think about yourself', 'what interests you',
                'your strengths', 'your values', 'life goals', 'personal development',
                'explore options', 'discover yourself', 'reflect on experience'
            ]
        }
    
    def classify(self, text):
        text_lower = text.lower()
        scores = {category: 0 for category in self.intent_keywords.keys()}
        
        # High priority multi-word phrases (weight = 3)
        for category, category_keywords in self.high_priority_keywords.items():
            for keyword in category_keywords:
                if keyword in text_lower:
                    scores[category] += 3
        
        # Individual keywords (weight = 1)
        for category, category_keywords in self.intent_keywords.items():
            for keyword in category_keywords:
                if keyword in text_lower:
                    scores[category] += 1
        
        # Select the category with the highest score
        max_score = max(scores.values())
        if max_score == 0:
            intent = "Understanding and Clarification"
            confidence = 0.5
        else:
            intent = max(scores, key=scores.get)
            # Calculate confidence based on score strength
            confidence = min(0.95, 0.5 + (max_score * 0.05))
        
        return {"intent": intent, "confidence": confidence}

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
    st.markdown('<div class="cloud-badge">🤖 Powered by Llama 3.1 8B + RoBERTa via HF API</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if "show_training" not in st.session_state:
        st.session_state.show_training = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.student_intents = []
        st.session_state.advisor_intents = []
    
    # Initialize intent classifier
    intent_classifier = SimpleIntentClassifier()
    
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
                    
                    # Generate student response using HF API
                    with st.spinner("🤖 Generating student response with Llama 3.1 8B..."):
                        try:
                            student_reply = generate_student_reply_with_hf_api(advisor_input, selected_persona)
                            
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
