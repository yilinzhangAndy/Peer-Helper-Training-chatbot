import streamlit as st
import os
import sys
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import random
import requests
import openai
import pandas as pd
import io
import uuid
from uf_navigator_api import UFNavigatorAPI
from simple_knowledge_base import SimpleKnowledgeBase

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

# Enhanced intent classifier for cloud deployment
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

# Hugging Face Inference API classifier (optional)
def _get_hf_token() -> str:
    # Prefer Streamlit Secrets; fallback to env
    try:
        return st.secrets.get("HF_TOKEN", "")
    except Exception:
        return os.getenv("HF_TOKEN", "")

def _get_hf_model() -> str:
    # Set your model repo name via Secrets or env; e.g., "zylandy/mae-intent-classifier"
    try:
        return st.secrets.get("HF_MODEL", "")
    except Exception:
        return os.getenv("HF_MODEL", "")

def hf_classify_via_api(text: str) -> Dict[str, Any]:
    token = _get_hf_token()
    model_name = _get_hf_model()
    if not token or not model_name:
        raise RuntimeError("HF token or model not configured")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    resp = requests.post(url, headers=headers, json={"inputs": text}, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Possible formats: [ {label, score}, ... ] OR [ [ {label, score}, ... ] ]
    candidates: List[Dict[str, Any]]
    if isinstance(data, list):
        if data and isinstance(data[0], list):
            candidates = data[0]
        else:
            candidates = data  # type: ignore
    else:
        raise ValueError("Unexpected HF response format")

    if not candidates:
        raise ValueError("Empty HF response")
    top = max(candidates, key=lambda x: x.get("score", 0.0))
    label = top.get("label", "Understanding and Clarification")
    score = float(top.get("score", 0.5))
    return {"intent": label, "confidence": score}

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
            "I'm trying to decide whether to pursue an internship this summer. I think it would be valuable experience, but I'm worried I'm not ready yet. Some of my friends seem so much more prepared than I am. Should I wait until I'm more confident?",
            "I want to get involved in a project team, but I'm unsure whether to prioritize technical build experience or leadership roles first. Which order would help me grow best?",
            "I like talking to faculty, but I'm not sure how to follow up after a first meeting without being awkward. What should I say next time?",
            "I feel motivated but sometimes overwhelmed by options — research, clubs, internships. How do I choose a first step that isn't too risky?",
            "I’m interested in robotics but don’t have much hands-on experience yet. What’s a good way to start building skills without getting lost?"
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
            "I failed my last exam and I'm really discouraged. I studied hard, but I still didn't do well. I'm starting to doubt if I can handle this major. Should I consider switching to something else?",
            "Group projects make me nervous because I'm afraid of letting people down. How can I contribute without feeling like I'm dragging the team?",
            "I want to ask for help but I don't know how to phrase the question without sounding like I don't belong here. Any tips on what to say?",
            "When I see others succeed, it makes me question whether I can do this. How do I stop comparing myself and focus on improving?"
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
            "I'm concerned about the job market and whether I'll be competitive when I graduate. What should I be doing now to prepare for my career and make myself stand out to employers?",
            "If I'm not into research, what are good ways to build real-world experience that employers value?",
            "I don't always feel comfortable asking questions in class. Are there quieter ways to get help without drawing attention?",
            "How can I decide whether to invest time in a club versus a part-time job if I want better career outcomes?",
            "What skills should I focus on this semester to see the biggest improvement in confidence?"
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
            "I'm really passionate about engineering and I want to explore different career paths. I'm interested in both technical and non-technical roles. How can I learn more about the various opportunities available?",
            "I'd like to pitch a new project idea to a faculty member, but I want to be respectful of their time. How can I structure that outreach well?",
            "Between grad school and startup experience, which path would help me learn fastest if I'm excited by building and iterating?",
            "I want to connect with alumni working in robotics. What's the best way to reach out without sounding generic?",
            "If I take on too many commitments, how can I prioritize so I still deliver high-quality work?"
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
        # Try Hugging Face API first if configured
        try:
            hf_result = hf_classify_via_api(text)
            if isinstance(hf_result.get("intent"), str):
                return {
                    "intent": hf_result.get("intent", "Unknown"),
                    "confidence": hf_result.get("confidence", 0.0)
                }
        except Exception:
            pass

        # Fallback to simple keyword classifier
        result = intent_classifier.classify(text)
        return {"intent": result.get("intent", "Unknown"), "confidence": result.get("confidence", 0.0)}
    except Exception as e:
        return {"intent": "Understanding and Clarification", "confidence": 0.5}

def generate_student_reply_with_rag_uf(advisor_message: str, persona: str, uf_api: UFNavigatorAPI, knowledge_base: SimpleKnowledgeBase) -> str:
    """使用RAG + UF LiteLLM API生成学生回复"""
    try:
        # 1. 检索相关知识
        relevant_docs = knowledge_base.search(advisor_message)
        knowledge_context = "\n".join(relevant_docs) if relevant_docs else ""
        
        # 2. 使用UF LiteLLM API生成回复
        reply = uf_api.generate_student_reply(advisor_message, persona, knowledge_context)
        
        if reply:
            return reply
        else:
            # Fallback到本地生成
            return generate_student_reply_fallback(advisor_message, persona)
            
    except Exception as e:
        st.warning(f"RAG + UF LiteLLM API失败: {str(e)}")
        return generate_student_reply_fallback(advisor_message, persona)

# Google Sheets logging functionality
def save_to_google_sheets(session_data: Dict[str, Any]) -> bool:
    """Save session data to Google Sheets (optional logging)"""
    try:
        # Check if logging is enabled
        if not st.session_state.get('allow_logging', False):
            return False
            
        # Get Google Sheets URL and API Key from secrets
        sheet_url = st.secrets.get("GOOGLE_SHEETS_URL", "")
        api_key = st.secrets.get("GOOGLE_API_KEY", "")
        
        if not sheet_url:
            return False
            
        # Try simple API Key method first
        if api_key:
            try:
                from simple_google_sheets import log_to_google_sheets
                return log_to_google_sheets(session_data, sheet_url, api_key)
            except ImportError:
                pass
        
        # Fallback to console logging
        print(f"Logging session: {session_data}")
        return True
        
    except Exception as e:
        print(f"Error logging to Google Sheets: {e}")
        return False

def export_session_data() -> Dict[str, Any]:
    """Export current session data for download"""
    if not st.session_state.messages:
        return {}
    
    # Generate session ID if not exists
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    
    # Prepare export data
    export_data = {
        "session_info": {
            "session_id": st.session_state.session_id,
            "persona": st.session_state.get('selected_persona', 'unknown'),
            "start_time": st.session_state.messages[0]["timestamp"].isoformat() if st.session_state.messages else "",
            "end_time": datetime.now().isoformat(),
            "message_count": len(st.session_state.messages)
        },
        "conversation": [],
        "analysis": {
            "student_intents": st.session_state.get('student_intents', []),
            "advisor_intents": st.session_state.get('advisor_intents', [])
        }
    }
    
    # Add conversation messages
    for i, message in enumerate(st.session_state.messages):
        export_data["conversation"].append({
            "turn": i + 1,
            "role": message["role"],
            "content": message["content"],
            "timestamp": message["timestamp"].isoformat()
        })
    
    return export_data

def generate_student_opening_with_uf(persona: str, uf_api: UFNavigatorAPI, knowledge_base: SimpleKnowledgeBase) -> Optional[str]:
    """Use UF LiteLLM + RAG to synthesize a persona-consistent opening question (1–2 sentences)."""
    try:
        if not uf_api:
            return None
        # Build persona profile context
        persona_data = STUDENT_PERSONAS.get(persona, {})
        traits = ", ".join(persona_data.get("traits", []))
        help_seeking = persona_data.get("help_seeking_behavior", "")
        description = persona_data.get("description", "")

        # Retrieve top knowledge
        kb_texts = []
        if knowledge_base:
            kb_texts = knowledge_base.search("MAE advising student opening prompt") or []
        knowledge_context = "\n".join(kb_texts)

        # Prompt the model
        system_msg = "You craft realistic first-turn student openings for a peer advising conversation. Always respond in English with 1–2 sentences."
        user_prompt = f"""
        Persona description: {description}
        Traits: {traits}
        Help-seeking behavior: {help_seeking}
        MAE knowledge (optional):\n{knowledge_context}

        Task: Write a natural, authentic opening message the student would say to a peer advisor. It should reflect the persona's confidence level and help-seeking style, mention a concrete topic (e.g., research, internships, clubs, specialization, confidence), and avoid clichés. Keep it 1–2 sentences.
        """

        response = uf_api.client.chat.completions.create(
            model="llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=120,
            temperature=0.8,
            top_p=0.95
        )
        text = response.choices[0].message.content.strip()
        # Basic safety: ensure ends with sentence punctuation
        if len(text) < 20:
            return None
        return text
    except Exception:
        return None

def generate_student_reply_fallback(advisor_message: str, persona: str) -> str:
    """Semantic-aware fallback reply generation based on advisor message content"""
    try:
        # Enhanced responses organized by semantic categories
        responses = {
            "alpha": {
                "encouragement": [
                    "Thank you for the encouragement! I really appreciate your support. I'm feeling more confident about this now.",
                    "That's exactly what I needed to hear. I'll definitely take your advice and keep working hard.",
                    "I'm grateful for your help. This makes me feel more optimistic about my engineering journey.",
                    "Your words really mean a lot to me. I was feeling uncertain, but now I feel more motivated.",
                    "I appreciate you believing in me. I'll do my best to follow through on your suggestions."
                ],
                "clarification": [
                    "I'm following along, but I'd like to make sure I understand completely. Could you explain that differently?",
                    "I think I understand, but I want to make sure I've got it right. Could you clarify a bit more?",
                    "I'm still a bit confused about some details. Could you help me understand this better?",
                    "I want to make sure I'm on the right track. Could you walk me through that again?",
                    "I'm getting it, but I'd like to confirm my understanding. What's the key point I should focus on?"
                ],
                "planning": [
                    "That sounds like a good plan! I'm excited to work on this. Could you help me break this down into smaller steps?",
                    "I like the idea of having a plan. What timeline do you think would be realistic for someone at my level?",
                    "This planning approach makes sense. How do I know if my goals are appropriate for my current level?",
                    "I want to make sure I'm setting realistic goals. What would you consider a good starting point for me?",
                    "I appreciate the structured approach. What milestones should I be aiming for?"
                ],
                "exploration": [
                    "This is really making me think about my future. I'm curious about exploring more options. What else should I consider?",
                    "That's an interesting perspective. I hadn't thought about it that way before. What made you consider this approach?",
                    "I'm curious about this. Could you tell me more about how this has worked for other students?",
                    "This is new to me. I'd like to explore this further. What resources would you recommend?",
                    "That's a good question. I'm still figuring out what I want to focus on. What do you think would be most valuable?"
                ]
            },
            "beta": {
                "encouragement": [
                    "I really appreciate you saying that. It means a lot to me, even though I still feel uncertain.",
                    "Thank you for being so understanding. I'm trying to believe in myself more.",
                    "Your support helps, but I'm still worried about whether I can really succeed in engineering.",
                    "I'm grateful for your patience with me. I know I can be difficult sometimes.",
                    "Thank you for not giving up on me. I'll try to be more confident in my abilities."
                ],
                "clarification": [
                    "I'm not sure I understand completely. I don't want to seem stupid, but could you explain it differently?",
                    "I'm still confused about this. Maybe I'm not cut out for engineering after all.",
                    "I don't want to bother you with more questions, but I'm still struggling to understand.",
                    "I'm sorry, but I'm still not getting it. Could you try a different approach?",
                    "I feel like I'm missing something basic. Could you help me figure out what it is?"
                ],
                "planning": [
                    "I'm not sure how to set realistic goals. What would be appropriate for someone at my level?",
                    "I feel like my goals might be too ambitious. How do I know what's achievable?",
                    "I'm worried about failing. What's a safe starting point that I can build from?",
                    "I don't want to set myself up for disappointment. What would be a reasonable first goal?",
                    "I'm nervous about committing to goals. How do I know I can actually achieve them?"
                ],
                "exploration": [
                    "I'm not sure I understand all the options. Could you explain what each path would involve?",
                    "I feel overwhelmed by all the choices. What would you recommend for someone who's just starting out?",
                    "I'm worried I might make the wrong decision. How do I know which direction is right for me?",
                    "This is all new to me. I'm not sure where to begin. Could you help me understand the basics?",
                    "I'm feeling lost with all these options. What would be a good starting point for someone like me?"
                ]
            },
            "delta": {
                "encouragement": [
                    "Thanks for the feedback! I'll definitely consider what you've said and see how it applies to my situation.",
                    "I appreciate your perspective. Let me think about this and see how I can implement your suggestions.",
                    "That's helpful advice. I'll work on incorporating that into my approach.",
                    "Your input is valuable. I'll analyze this and see how it fits with my current strategy.",
                    "Good point. I'll evaluate this feedback and determine the best way forward."
                ],
                "clarification": [
                    "I see what you mean, but I'd like to make sure I understand correctly. Could you clarify?",
                    "I think I get it, but let me make sure I've got the right approach. Could you confirm?",
                    "I understand the general idea, but I want to make sure I'm implementing it correctly.",
                    "That makes sense, but I want to verify my understanding. What's the most important aspect?",
                    "I'm following your logic, but I'd like to confirm the key principles behind this approach."
                ],
                "planning": [
                    "I like the strategic approach. I'm thinking about how to structure this for maximum impact. What's your recommendation?",
                    "That makes sense. I'm planning how to implement this effectively. What timeline would you suggest?",
                    "Good framework. I'm considering the best way to execute this plan. What resources would you recommend?",
                    "This is a solid plan. I'm analyzing the implementation strategy. What's the most critical success factor?",
                    "Excellent approach. I'm considering the long-term implications. What should I prioritize first?"
                ],
                "exploration": [
                    "That's an interesting approach. I'm considering how this aligns with my long-term goals. What are your thoughts on the strategic implications?",
                    "I appreciate the insight. I'm evaluating how this fits into my overall plan. What would you prioritize in my situation?",
                    "Good point. I'm thinking about the best way to leverage this opportunity. What's your take on the timing?",
                    "This is intriguing. I'm analyzing how this could benefit my career trajectory. What's your experience with this approach?",
                    "That's a solid perspective. I'm considering the implementation strategy. What challenges should I anticipate?"
                ]
            },
            "echo": {
                "encouragement": [
                    "Excellent! That's exactly the kind of guidance I was looking for. I'm excited to put this into practice.",
                    "Perfect! I'm confident this approach will work well for me. Thanks for the great advice!",
                    "That's fantastic! I love learning new strategies. I'm ready to take on this challenge.",
                    "Outstanding! This is exactly what I needed. I'm energized and ready to implement this.",
                    "Brilliant! I'm excited about the possibilities. This is going to be great!"
                ],
                "clarification": [
                    "I think I understand, but let me make sure I've got it right. Could you confirm the key points?",
                    "I'm following along well, but I want to make sure I'm not missing anything important.",
                    "That makes sense! I just want to double-check that I'm approaching this the right way.",
                    "I'm getting the concept, but I'd love to understand the deeper principles. Could you elaborate?",
                    "This is fascinating! I want to make sure I understand all the nuances. What else should I know?"
                ],
                "planning": [
                    "Excellent! I'm excited to create an ambitious plan. What would you consider a stretch goal for me?",
                    "That's a great framework! I'm ready to set some challenging targets. What timeline would push me to grow?",
                    "Perfect! I love having clear objectives. What would be the most impactful goals I could set?",
                    "This is fantastic! I'm ready to set some really ambitious targets. What would be the ultimate goal?",
                    "Outstanding! I'm excited about the possibilities. What would be the most challenging objective I could pursue?"
                ],
                "exploration": [
                    "That's exciting! I love exploring new possibilities. What other opportunities should I be looking into?",
                    "This is exactly what I was hoping for! I'm energized by the potential. What's the next step I should take?",
                    "Fantastic! I'm ready to dive in and make the most of this. What resources do you recommend I explore?",
                    "This is perfect! I'm excited about all the possibilities. What would be the most ambitious goal I could set?",
                    "Excellent! I'm ready to take this to the next level. What advanced strategies should I consider?"
                ]
            }
        }
        
        # Semantic analysis of advisor message
        advisor_lower = advisor_message.lower()
        
        # Determine response category based on advisor message content
        if any(word in advisor_lower for word in ['good', 'great', 'excellent', 'well done', 'proud', 'confident', 'believe', 'support', 'encourage']):
            category = "encouragement"
        elif any(word in advisor_lower for word in ['explain', 'clarify', 'understand', 'mean', 'what', 'how', 'why', 'example', 'detail']):
            category = "clarification"
        elif any(word in advisor_lower for word in ['plan', 'goal', 'strategy', 'approach', 'step', 'next', 'future', 'timeline', 'schedule']):
            category = "planning"
        elif any(word in advisor_lower for word in ['explore', 'consider', 'think about', 'option', 'possibility', 'interest', 'curious', 'discover']):
            category = "exploration"
        else:
            # Default to clarification if no clear category
            category = "clarification"
        
        # Get responses for the specific persona and category
        persona_responses = responses.get(persona, responses["alpha"])
        category_responses = persona_responses.get(category, persona_responses["clarification"])
        
        # Add some randomness to avoid exact repetition
        import time
        random.seed(int(time.time() * 1000) % 10000)
        
        return random.choice(category_responses)
        
    except Exception as e:
        return "I'm not sure how to respond to that. Could you help me understand better?"

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
    
    # How it works info - use st.info for better compatibility
    st.info("""
    **How It Works**
    
    **Choose Your Training Scenario**  
    Select a student persona (Alpha, Beta, Delta, or Echo) based on the mentoring skills you want to practice
    
    **Start Conversation Training**  
    Engage in realistic dialogue with AI-powered student personas that respond based on authentic psychological profiles
    
    **Get Real-time Feedback**  
    Our system analyzes your responses using AI classification and provides instant feedback on communication patterns
    """)
    
    # Load components
    with st.spinner("Loading AI components..."):
        intent_classifier = SimpleIntentClassifier()
        
        # Initialize UF LiteLLM API and Knowledge Base
        try:
            uf_api = UFNavigatorAPI()
            knowledge_base = SimpleKnowledgeBase()
            
            # Test UF LiteLLM API connection
            success, message = uf_api.test_connection()
            if success:
                st.success("✅ UF LiteLLM API connected successfully!")
            else:
                st.warning(f"⚠️ UF LiteLLM API connection failed: {message}")
                st.info("🔄 Using fallback responses for student replies")
                uf_api = None
                knowledge_base = None
        except Exception as e:
            st.warning(f"⚠️ Failed to initialize UF LiteLLM API: {str(e)}")
            st.info("🔄 Using fallback responses for student replies")
            uf_api = None
            knowledge_base = None
    
    # Initialize show_training state
    if "show_training" not in st.session_state:
        st.session_state.show_training = False
    
    # Main content area
    if not st.session_state.show_training:
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
                # Log current session if logging is enabled
                if st.session_state.allow_logging and st.session_state.messages:
                    session_data = {
                        "session_id": st.session_state.session_id,
                        "persona": st.session_state.get('selected_persona', 'unknown'),
                        "message_count": len(st.session_state.messages),
                        "summary": f"Conversation with {len(st.session_state.messages)} messages"
                    }
                    save_to_google_sheets(session_data)
                
                # Reset session
                st.session_state.messages = []
                st.session_state.student_intents = []
                st.session_state.advisor_intents = []
                st.session_state.session_id = str(uuid.uuid4())[:8]
                st.rerun()
            
            if st.button("🏠 Back to Home"):
                st.session_state.show_training = False
                st.rerun()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.student_intents = []
        st.session_state.advisor_intents = []
        st.session_state.allow_logging = False
        st.session_state.session_id = str(uuid.uuid4())[:8]
    
    # Main chat interface (only show in training mode)
    if st.session_state.show_training:
        st.header("💬 Training Conversation")
        
        # Display conversation history
        # Track student and advisor message counts separately
        student_count = 0
        advisor_count = 0
        
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "student":
                # Student message with intent
                intent_info = st.session_state.student_intents[student_count] if student_count < len(st.session_state.student_intents) else {"intent": "Unknown", "confidence": 0.0}
                intent_class = get_intent_badge_class(intent_info["intent"])
                
                st.markdown(f"""
                <div class="chat-message student-message">
                    <strong>👨‍🎓 Student ({selected_persona.upper()}):</strong> {message["content"]}
                    <div class="intent-badge {intent_class}">
                        {intent_info["intent"]} • Confidence: {intent_info["confidence"]:.1%}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                student_count += 1
                
            else:
                # Advisor message with intent
                intent_info = st.session_state.advisor_intents[advisor_count] if advisor_count < len(st.session_state.advisor_intents) else {"intent": "Unknown", "confidence": 0.0}
                intent_class = get_intent_badge_class(intent_info["intent"])
                
                st.markdown(f"""
                <div class="chat-message advisor-message">
                    <strong>👨‍🏫 You (Peer Advisor):</strong> {message["content"]}
                    <div class="intent-badge {intent_class}">
                        {intent_info["intent"]} • Confidence: {intent_info["confidence"]:.1%}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                advisor_count += 1
        
        # Generate initial student message if conversation is empty
        if not st.session_state.messages:
            if st.button("🎯 Start Conversation"):
                with st.spinner("Student is thinking..."):
                    opening_text = None
                    if uf_api and knowledge_base:
                        opening_text = generate_student_opening_with_uf(selected_persona, uf_api, knowledge_base)
                    if not opening_text:
                        opening_pool = STUDENT_PERSONAS[selected_persona]["opening_questions"]
                        opening_text = random.choice(opening_pool)

                    st.session_state.messages.append({
                        "role": "student",
                        "content": opening_text,
                        "timestamp": datetime.now()
                    })

                    # Analyze student intent
                    intent_result = analyze_intent(opening_text, intent_classifier, "student")
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
                            # Try RAG + UF LiteLLM API first
                            if uf_api and knowledge_base:
                                student_reply = generate_student_reply_with_rag_uf(
                                    advisor_message=advisor_input,
                                    persona=selected_persona,
                                    uf_api=uf_api,
                                    knowledge_base=knowledge_base
                                )
                            else:
                                # Fallback to semantic-aware method
                                student_reply = generate_student_reply_fallback(
                                    advisor_message=advisor_input,
                                    persona=selected_persona
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
                            # Add a fallback response only on error
                            st.session_state.messages.append({
                                "role": "student",
                                "content": "I'm not sure how to respond to that. Could you help me understand better?",
                                "timestamp": datetime.now()
                            })
                            st.session_state.student_intents.append({"intent": "Understanding and Clarification", "confidence": 0.5})
                    
                    st.rerun()
                else:
                    st.warning("Please enter a response before sending.")
        
        # Logging consent and export section
        if st.session_state.messages:
            st.header("📊 Session Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Logging consent
                st.subheader("🔒 Privacy & Logging")
                allow_logging = st.checkbox(
                    "Allow anonymous session logging for research",
                    value=st.session_state.allow_logging,
                    help="Help improve the system by allowing anonymous logging of conversation patterns. No personal information is collected."
                )
                st.session_state.allow_logging = allow_logging
                
                if allow_logging:
                    st.info("✅ Your session will be anonymously logged for research purposes")
                else:
                    st.info("🔒 Your session will not be logged")
            
            with col2:
                # Export functionality
                st.subheader("💾 Export Session")
                
                if st.button("📥 Download Session Data"):
                    export_data = export_session_data()
                    if export_data:
                        # Create JSON download
                        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="📄 Download as JSON",
                            data=json_str,
                            file_name=f"chatbot_session_{st.session_state.session_id}.json",
                            mime="application/json"
                        )
                        
                        # Create CSV download
                        df_data = []
                        for msg in export_data["conversation"]:
                            df_data.append({
                                "Turn": msg["turn"],
                                "Role": msg["role"],
                                "Content": msg["content"],
                                "Timestamp": msg["timestamp"]
                            })
                        
                        if df_data:
                            df = pd.DataFrame(df_data)
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📊 Download as CSV",
                                data=csv,
                                file_name=f"chatbot_session_{st.session_state.session_id}.csv",
                                mime="text/csv"
                            )
                    else:
                        st.warning("No conversation data to export")
        
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
            
            # Q→A pair analysis
            st.subheader("Question-Answer Pair Analysis")
            same_intent_pairs = 0
            different_intent_pairs = 0
            
            # Find student-advisor pairs
            student_count = 0
            advisor_count = 0
            
            for i in range(1, len(st.session_state.messages)):
                if (st.session_state.messages[i-1]["role"] == "student" and 
                    st.session_state.messages[i]["role"] == "advisor"):
                    
                    # Use the current counts for indexing
                    if (student_count < len(st.session_state.student_intents) and 
                        advisor_count < len(st.session_state.advisor_intents)):
                        
                        student_intent = st.session_state.student_intents[student_count]["intent"]
                        advisor_intent = st.session_state.advisor_intents[advisor_count]["intent"]
                        
                        if student_intent == advisor_intent:
                            same_intent_pairs += 1
                        else:
                            different_intent_pairs += 1
                    
                    # Update counts
                    if st.session_state.messages[i-1]["role"] == "student":
                        student_count += 1
                    if st.session_state.messages[i]["role"] == "advisor":
                        advisor_count += 1
            
            st.write(f"• **Same intent pairs**: {same_intent_pairs}")
            st.write(f"• **Different intent pairs**: {different_intent_pairs}")

if __name__ == "__main__":
    main()
