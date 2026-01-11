import streamlit as st
import os
import sys
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import random
import requests
import openai
import uuid
# (Disabled optional logging/export dependencies)
# import pandas as pd
# import io
# import uuid
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

def get_smart_conversation_history(conversation_history: List[Dict], 
                                  current_message: str,
                                  max_messages: int = 6) -> str:
    """
    智能选择最相关的对话历史
    
    Args:
        conversation_history: 完整对话历史
        current_message: 当前advisor消息
        max_messages: 最大消息数量
    
    Returns:
        格式化的对话历史文本
    """
    if not conversation_history:
        return ""
    
    # 提取当前消息的关键词
    current_words = set(current_message.lower().split())
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                 'to', 'of', 'and', 'or', 'but', 'in', 'on', 'at', 'for', 
                 'with', 'by', 'from', 'as', 'this', 'that', 'these', 'those',
                 'so', 'do', 'does', 'did', 'can', 'could', 'will', 'would',
                 'have', 'has', 'had', 'what', 'which', 'when', 'where', 'why', 'how',
                 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    current_words = current_words - stop_words
    
    # 为每条历史消息评分
    scored_messages = []
    for msg in conversation_history:
        msg_text = msg.get('content', '').lower()
        msg_words = set(msg_text.split()) - stop_words
        
        # 计算相关性（共同关键词）
        common_words = current_words & msg_words
        relevance = len(common_words)
        
        # 问题消息加分（通常更重要）
        if msg.get('role') == 'advisor':
            relevance += 1
        
        # 最近的消息加分（时间衰减）
        msg_index = conversation_history.index(msg)
        recency_bonus = max(0, (len(conversation_history) - msg_index) * 0.1)
        relevance += recency_bonus
        
        scored_messages.append((relevance, msg_index, msg))
    
    # 选择最相关的消息
    scored_messages.sort(key=lambda x: x[0], reverse=True)
    selected_indices = set()
    selected_messages = []
    
    for relevance, msg_index, msg in scored_messages[:max_messages * 2]:  # 多选一些，然后筛选
        if len(selected_messages) >= max_messages:
            break
        if msg_index not in selected_indices:
            selected_indices.add(msg_index)
            selected_messages.append((msg_index, msg))
    
    # 按时间顺序排序
    selected_messages.sort(key=lambda x: x[0])
    
    # 格式化
    context_parts = []
    for _, msg in selected_messages:
        role_label = "Advisor" if msg["role"] == "advisor" else "Student"
        context_parts.append(f"{role_label}: {msg['content']}")
    
    return "\n".join(context_parts) if context_parts else ""

def get_realtime_uf_mae_info(query_text: str, max_results: int = 3) -> str:
    """
    通用函数：实时搜索 UF MAE 网站获取最新信息
    可以在任何需要时调用（开场问题、对话回复等）
    
    Args:
        query_text: 查询文本（可以是 advisor 消息、学生问题等）
        max_results: 最大结果数
    
    Returns:
        搜索到的信息文本（如果没有结果则返回空字符串）
    """
    try:
        from uf_mae_web_scraper import UFMAEWebScraper
        
        # 扩展搜索关键词：不仅限于课程，还包括研究、资源、联系方式等
        search_keywords = [
            # 课程相关
            'course', 'class', 'schedule', 'semester', 'spring', 'summer', 'fall', 
            'EML', 'what classes', 'what courses', 'taking', 'enrolled', 'curriculum',
            # 研究相关
            'research', 'lab', 'faculty', 'professor', 'advisor', 'mentor',
            'robotics', 'aerospace', 'mechanical', 'space', 'energy', 'design',
            # 资源相关
            'resource', 'opportunity', 'internship', 'club', 'organization',
            'funding', 'scholarship', 'financial aid', 'support',
            # 联系相关
            'contact', 'email', 'phone', 'office hours', 'appointment',
            # 其他
            'MAE', 'program', 'degree', 'graduate', 'undergraduate'
        ]
        
        # 检查是否包含任何搜索关键词
        query_lower = query_text.lower()
        should_search = any(keyword in query_lower for keyword in search_keywords)
        
        if should_search:
            scraper = UFMAEWebScraper()
            web_results = scraper.search_website(query_text, max_results=max_results)
            if web_results:
                web_context = "\n".join([f"Real-time UF MAE website info: {r}" for r in web_results])
                return web_context
        
        return ""
    except Exception as e:
        print(f"⚠️ Real-time website search failed: {e}")
        return ""

def generate_student_reply_with_rag_uf(advisor_message: str, persona: str, uf_api: UFNavigatorAPI, 
                                      knowledge_base: SimpleKnowledgeBase, advisor_intent: str = None,
                                      conversation_history: List[Dict] = None,
                                      persona_info: Optional[Dict[str, Any]] = None,
                                      preferred_model: Optional[str] = None) -> str:
    """使用RAG + UF LiteLLM API生成学生回复（支持多模型fallback）"""
    try:
        # 1. 检索相关知识
        relevant_docs = knowledge_base.search(advisor_message)
        knowledge_context = "\n".join(relevant_docs) if relevant_docs else ""
        
        # 1.5. 实时搜索 UF MAE 网站（通用搜索，适用于所有场景）
        web_context = get_realtime_uf_mae_info(advisor_message, max_results=3)
        if web_context:
            knowledge_context = f"{knowledge_context}\n\n{web_context}" if knowledge_context else web_context
        
        # 2. 智能选择对话上下文（改进：选择最相关的消息，而不是固定3轮）
        context_text = ""
        if conversation_history:
            context_text = get_smart_conversation_history(
                conversation_history, 
                advisor_message,
                max_messages=6
            )
        
        # 3. 如果有上下文，添加到 advisor_message 中
        if context_text:
            full_advisor_message = f"""Previous conversation:
{context_text}

Now the advisor says: {advisor_message}"""
        else:
            full_advisor_message = advisor_message
        
        # 4. 使用UF LiteLLM API生成回复（传递intent、persona_info、preferred_model用于Few-Shot和模型选择）
        reply = uf_api.generate_student_reply(
            advisor_message=full_advisor_message, 
            persona=persona, 
            knowledge_context=knowledge_context,
            use_few_shot=True,
            intent=advisor_intent,  # 传递intent用于Few-Shot示例选择
            persona_info=persona_info,  # ✅ 传递persona_info
            preferred_model=preferred_model  # ✅ 传递preferred_model
        )
        
        if reply:
            return reply
        else:
            # Fallback到本地生成
            error_msg = uf_api.last_error if uf_api else "Unknown error"
            # 如果是 meta tensor 错误，提供更友好的提示（但不要每次都显示，避免刷屏）
            if "meta tensor" in error_msg.lower() or "cannot copy out of meta tensor" in error_msg.lower():
                # 只在第一次出现时显示，避免重复提示
                if "uf_api_meta_tensor_warned" not in st.session_state:
                    st.session_state.uf_api_meta_tensor_warned = True
                    # 检测环境以显示正确语言
                    is_local_env = (
                        os.getenv("STREAMLIT_SERVER_ENABLE_CORS") is None and
                        "streamlit" not in str(os.getenv("HOSTNAME", "")).lower()
                    )
                    fallback_msg = (
                        "⚠️ UF API server-side model loading issue. Switched to local fallback response. "
                        "System will continue using fallback until API recovers."
                    ) if not is_local_env else (
                        "⚠️ UF API 服务器端模型加载问题，已切换到本地 fallback 响应。系统将继续使用 fallback 直到 API 恢复。"
                    )
                    st.info(fallback_msg)
            # 其他错误不显示，避免干扰用户体验
            return generate_student_reply_fallback(advisor_message, persona)
            
    except Exception as e:
        error_msg = str(e)
        # 检查是否是 meta tensor 错误
        if "meta tensor" in error_msg.lower() or "cannot copy out of meta tensor" in error_msg.lower():
            # 只在第一次出现时显示
            if "uf_api_meta_tensor_warned" not in st.session_state:
                st.session_state.uf_api_meta_tensor_warned = True
                # 检测环境以显示正确语言
                is_local_env = (
                    os.getenv("STREAMLIT_SERVER_ENABLE_CORS") is None and
                    "streamlit" not in str(os.getenv("HOSTNAME", "")).lower()
                )
                fallback_msg = (
                    "⚠️ UF API server-side model loading error. Switched to local fallback response. "
                    "System will continue using fallback until API recovers."
                ) if not is_local_env else (
                    "⚠️ UF API 服务器端模型加载错误，已切换到本地 fallback 响应。系统将继续使用 fallback 直到 API 恢复。"
                )
                st.info(fallback_msg)
        # 其他错误静默处理，避免干扰
        return generate_student_reply_fallback(advisor_message, persona)

# Google Sheets logging functionality
def save_to_google_sheets(session_data: Dict[str, Any]) -> bool:
    """Disabled: logging removed per user request."""
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

def generate_student_opening_with_uf(
    persona: str,
    uf_api: UFNavigatorAPI,
    knowledge_base: SimpleKnowledgeBase,
    preferred_model: str = None
) -> Optional[str]:
    """Use UF LiteLLM + RAG to synthesize a persona-consistent opening message (with model fallback)."""
    try:
        if not uf_api or not uf_api.client:
            return None

        persona_data = STUDENT_PERSONAS.get(persona, {})
        traits = ", ".join(persona_data.get("traits", []))
        help_seeking = persona_data.get("help_seeking_behavior", "")
        description = persona_data.get("description", "")

        kb_texts = knowledge_base.search("MAE advising student opening prompt") if knowledge_base else []
        knowledge_context = "\n".join(kb_texts or [])
        
        # 实时搜索 UF MAE 网站获取最新信息（用于生成更真实的开场问题）
        # 根据 persona 调整搜索关键词：DELTA 不感兴趣研究，应该搜索 internships/clubs 相关信息
        if persona.lower() == "delta":
            search_query = "MAE internships clubs career opportunities spring"
        else:
            search_query = "MAE courses research opportunities spring"
        web_context = get_realtime_uf_mae_info(search_query, max_results=2)
        if web_context:
            knowledge_context = f"{knowledge_context}\n{web_context}" if knowledge_context else web_context

        system_msg = {
            "role": "system",
            "content": "You craft realistic first-turn student openings for a peer advising conversation. Always respond in English with 1–2 sentences."
        }
        # 为 DELTA persona 添加特殊指导（不感兴趣研究、不太愿意求助）
        delta_guidance = ""
        if persona.lower() == "delta":
            delta_guidance = """
CRITICAL FOR DELTA PERSONA:
- DO NOT mention research or research opportunities (Delta is NOT interested in research)
- DO NOT directly ask for help or advice (Delta is hesitant to seek help)
- Instead: Frame questions indirectly, show hesitation, or express uncertainty without explicitly asking
- Focus on: internships, clubs, career preparation, practical applications, job market concerns
- Language style: More indirect, less direct questions, shows concern about others' opinions
- Example good style: "I've been thinking about internships, but I'm not sure if I'm competitive enough..." (indirect, hesitant)
- Example bad style: "Do you have any advice on research opportunities?" (too direct, mentions research)
"""
        
        user_msg = {
            "role": "user",
            "content": f"""
Persona description: {description}
Traits: {traits}
Help-seeking behavior: {help_seeking}
{delta_guidance}
MAE knowledge (optional):
{knowledge_context}

Task: Write a natural, authentic opening message the student would say to a peer advisor.
It should reflect the persona's confidence level and help-seeking style, mention a concrete topic
(e.g., internships, clubs, specialization, career preparation - but NOT research for Delta), 
avoid clichés, and be 1–2 sentences.

IMPORTANT: For Delta persona, the message should be indirect and hesitant, NOT directly asking for help.
"""
        }

        # ✅ 用 UFNavigatorAPI 的"多模型 fallback"机制：借用 generate_student_reply 的模型选择逻辑
        opening = uf_api.generate_student_reply(
            advisor_message=user_msg["content"],
            persona=persona,
            knowledge_context=knowledge_context,
            use_few_shot=False,
            intent=None,
            persona_info=persona_data,
            preferred_model=preferred_model,
        )
        return opening

    except Exception as e:
        # 出错就让上层走本地 fallback opening
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

def init_session_state():
    """初始化 session_state（使用 setdefault 更安全）"""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("student_intents", [])
    st.session_state.setdefault("advisor_intents", [])
    st.session_state.setdefault("selected_persona", "alpha")
    st.session_state.setdefault("allow_logging", False)
    st.session_state.setdefault("session_id", str(uuid.uuid4())[:8])
    st.session_state.setdefault("show_training", False)
    # ✅ 关键：控制输入框动态 key
    st.session_state.setdefault("advisor_box_id", 0)
    # ✅ 关键：存储 API 和知识库（避免每次 rerun 重新初始化）
    # 注意：不要在这里设置为 None，让初始化逻辑在 main() 中处理

def main():
    # ===== 关键修复1：session_state 初始化必须在最开头（任何使用之前） =====
    # Initialize session state FIRST - before any other code that might access it
    init_session_state()
    
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

        # 初始化一次：不要在启动阶段 test_connection / chat
        if "uf_api" not in st.session_state or st.session_state.uf_api is None:
            st.session_state.uf_api = UFNavigatorAPI()
        if "knowledge_base" not in st.session_state or st.session_state.knowledge_base is None:
            st.session_state.knowledge_base = SimpleKnowledgeBase()

        uf_api = st.session_state.uf_api
        knowledge_base = st.session_state.knowledge_base

        # 检测是否为本地环境：更可靠的方法（必须在 get_error_message 之前定义）
        def is_local_environment():
            """检测是否在本地环境运行（不在 Streamlit Cloud）
            
            策略：默认假设是云端（更安全），只有在明确检测到本地特征时才返回 True
            """
            try:
                # 方法 1: 检查 Streamlit Cloud 特定的环境变量（最可靠）
                streamlit_cloud_vars = [
                    "STREAMLIT_SERVER_ENABLE_CORS",
                    "STREAMLIT_SERVER_PORT",
                    "STREAMLIT_SERVER_ADDRESS",
                    "STREAMLIT_SERVER_HEADLESS"
                ]
                for var in streamlit_cloud_vars:
                    if os.getenv(var) is not None:
                        return False  # 在 Streamlit Cloud 上
                
                # 方法 2: 检查主机名
                import socket
                hostname = socket.gethostname()
                if "streamlit" in hostname.lower() or "cloud" in hostname.lower():
                    return False
                
                # 方法 3: 检查是否在 Streamlit Cloud 的典型路径
                # Streamlit Cloud 通常在 /mount/src/ 下
                import sys
                if any("/mount/src/" in str(path) for path in sys.path):
                    return False
                
                # 方法 4: 检查 HOME 目录（本地通常有用户目录）
                home = os.getenv("HOME", "")
                if not home:
                    # 没有 HOME，可能是云端容器
                    return False
                
                # 方法 5: 检查是否是典型的本地开发环境
                # 本地通常有：用户目录（/Users/ 或 /home/），且不在 /mount/ 下
                if ("Users" in home or "/home/" in home) and "/mount/" not in home:
                    # 可能是本地，但还要做最后的双重检查
                    # 检查是否有明显的云端特征
                    if os.getenv("STREAMLIT_CLOUD") is not None:
                        return False
                    # 如果都没有，假设是本地
                    return True
                
                # 默认假设是云端（更安全：不显示调试功能）
                return False
            except Exception as e:
                # 如果检测失败，默认假设是云端（更安全：不显示调试功能）
                print(f"⚠️ Environment detection error: {e}")
                return False
        
        is_local = is_local_environment()
        
        # 双重检查：确保真的是本地环境（更严格的检查，用于隐藏调试功能）
        # 策略：使用最严格的方法，有任何云端特征就认为是云端（更安全）
        import socket
        import sys
        
        # 方法 1: 检查是否是 Streamlit Cloud 的明确特征（使用 OR 逻辑：任何一个匹配就是云端）
        is_cloud_detected = (
            os.getenv("STREAMLIT_SERVER_ENABLE_CORS") is not None or  # Cloud 环境变量
            os.getenv("STREAMLIT_CLOUD") is not None or  # Cloud 标记
            any("/mount/src/" in str(path) for path in sys.path) or  # Cloud 路径
            any("/mount/" in str(path) for path in sys.path) or  # Cloud 路径（更宽泛）
            "streamlit" in str(socket.gethostname()).lower() or  # Cloud 主机名
            "cloud" in str(socket.gethostname()).lower() or  # Cloud 主机名
            os.getenv("HOME", "") == "" or  # 没有 HOME（云端容器特征）
            "/mount/" in os.getenv("HOME", "")  # HOME 在 /mount/ 下（云端特征）
        )
        
        # 方法 2: 尝试使用 Streamlit 运行时信息（如果可用）
        try:
            import streamlit.runtime.scriptrunner.script_runner as script_runner
            # 检查是否有 Streamlit Cloud 的运行时特征
            # 注意：这个方法可能在不同版本中有所不同
        except:
            pass
        
        # 方法 3: 检查当前工作目录（最可靠的方法）
        try:
            cwd = os.getcwd()
            if "/mount/src/" in cwd or "/mount/" in cwd:
                is_cloud_detected = True
        except:
            pass
        
        # 方法 4: 检查 __file__ 路径（如果可用）
        try:
            current_file = __file__ if '__file__' in globals() else ""
            if "/mount/src/" in current_file or "/mount/" in current_file:
                is_cloud_detected = True
        except:
            pass
        
        # 只有在明确不是云端，且基础检测通过时，才认为是本地
        # 默认假设是云端（更安全：不显示调试功能）
        is_really_local = is_local and not is_cloud_detected
        
        # 最终安全检查：如果任何检测不确定，强制隐藏（最安全）
        # 只有在 100% 确定是本地时才显示调试工具
        if not is_really_local:
            # 明确不是本地，确保隐藏
            is_really_local = False  # 强制设置为 False
        
        # 使用闭包捕获 is_local 的值，避免 UnboundLocalError
        _is_local_value = is_local  # 保存到局部变量，供闭包使用
        
        # 语言切换函数：云端显示英文，本地显示中文（必须在调用之前定义）
        def get_error_message(key: str, **kwargs) -> str:
            """根据环境返回不同语言的消息"""
            messages = {
                "api_not_initialized": {
                    "zh": "⚠️ **UF LiteLLM API 未初始化**",
                    "en": "⚠️ **UF LiteLLM API Not Initialized**"
                },
                "api_not_configured": {
                    "zh": "⚠️ **UF LiteLLM API 未配置**",
                    "en": "⚠️ **UF LiteLLM API Not Configured**"
                },
                "api_init_failed": {
                    "zh": "⚠️ **UF LiteLLM API 初始化失败**",
                    "en": "⚠️ **UF LiteLLM API Initialization Failed**"
                },
                "api_server_error": {
                    "zh": "⚠️ **UF LiteLLM API 服务器端模型加载错误**",
                    "en": "⚠️ **UF LiteLLM API Server-Side Model Loading Error**"
                },
                "using_fallback": {
                    "zh": "🔄 Using fallback responses for student replies",
                    "en": "🔄 Using fallback responses for student replies"
                },
                "server_loading_issue": {
                    "zh": "ℹ️ 注意：检测到服务器端模型加载问题，系统将自动使用 fallback 机制。",
                    "en": "ℹ️ Server-side model loading issue detected. System will automatically use fallback mechanism."
                },
                "api_initialized": {
                    "zh": "✅ UF LiteLLM client initialized (API will be used on demand).",
                    "en": "✅ UF LiteLLM client initialized (API will be used on demand)."
                },
                "api_initialized_fallback": {
                    "zh": "✅ UF LiteLLM client initialized (API will be used on demand, fallback enabled).",
                    "en": "✅ UF LiteLLM client initialized (API will be used on demand, fallback enabled)."
                },
                "error_details": {
                    "zh": "错误详情",
                    "en": "Error Details"
                },
                "problem_description": {
                    "zh": "**问题说明：** 这是 UF LiteLLM API 服务器端的问题，不是您的代码问题。",
                    "en": "**Problem:** This is a server-side issue with UF LiteLLM API, not a problem with your code."
                },
                "possible_causes": {
                    "zh": "**可能原因：**",
                    "en": "**Possible Causes:**"
                },
                "server_init": {
                    "zh": "- 服务器正在初始化或重新加载模型",
                    "en": "- Server is initializing or reloading models"
                },
                "server_config": {
                    "zh": "- 服务器端 PyTorch 模型加载配置问题",
                    "en": "- Server-side PyTorch model loading configuration issue"
                },
                "server_resources": {
                    "zh": "- 服务器资源不足",
                    "en": "- Insufficient server resources"
                },
                "solutions": {
                    "zh": "**解决方案：**",
                    "en": "**Solutions:**"
                },
                "wait_retry": {
                    "zh": "- 等待几分钟后重试",
                    "en": "- Wait a few minutes and try again"
                },
                "auto_fallback": {
                    "zh": "- 系统会自动使用 fallback 响应",
                    "en": "- System will automatically use fallback responses"
                },
                "contact_it": {
                    "zh": "- 如果问题持续，请联系 UF IT 部门",
                    "en": "- If the problem persists, contact UF IT department"
                },
                "technical_error": {
                    "zh": "**技术错误：**",
                    "en": "**Technical Error:**"
                },
                "server_loading": {
                    "zh": "ℹ️ UF LiteLLM 服务器正在加载/更新模型（server-side）。我先用 fallback 回复；稍后再试通常会恢复。",
                    "en": "ℹ️ UF LiteLLM server is loading/updating models (server-side). Using fallback response for now; retry later usually resolves this."
                },
                "api_call_failed": {
                    "zh": "⚠️ UF API 调用失败",
                    "en": "⚠️ UF API call failed"
                }
            }
            
            # 使用闭包中捕获的 _is_local_value
            lang = "zh" if _is_local_value else "en"
            msg_template = messages.get(key, {}).get(lang, key)
            
            # 替换占位符
            if kwargs:
                msg_template = msg_template.format(**kwargs)
            
            return msg_template

        # 只显示本地状态（不触发任何远端调用）
        # 统一错误处理逻辑：优先显示配置错误，然后是运行时错误
        if not uf_api:
            st.warning(get_error_message("api_not_initialized"))
            st.info(get_error_message("using_fallback"))
        elif not uf_api.client:
            # Client 未创建，检查原因
            error_msg = uf_api.last_error if uf_api else ""
            
            # 优先检查是否是配置问题（API key 或 base URL 未提供）
            if "not provided" in error_msg.lower() or "api key not provided" in error_msg.lower() or "base url not provided" in error_msg.lower():
                st.warning(get_error_message("api_not_configured"))
                with st.expander("📖 如何配置 API（点击展开）", expanded=False):
                    st.markdown("""
                    **配置方法（根据部署环境选择）：**
                    
                    ### 🌐 云端部署（Streamlit Cloud）
                    
                    **⚠️ 重要：云端不能通过创建文件配置！**
                    
                    1. **访问 Streamlit Cloud Dashboard**
                       - 打开 https://share.streamlit.io/
                       - 登录你的 GitHub 账号
                    
                    2. **找到你的应用并进入 Settings**
                       - 点击应用名称（不是 "Open app"）
                       - 查找 "Settings" 或 "Secrets" 标签/菜单
                       - 点击 "Edit secrets" 或 "Manage secrets"
                    
                    3. **在 Secrets 编辑器中添加：**
                       ```toml
                       UF_LITELLM_BASE_URL = "https://api.ai.it.ufl.edu"
                       UF_LITELLM_API_KEY = "sk-FEhqmwbGafXtX9sv07rZLw"
                       ```
                    
                    4. **保存并等待自动重新部署**（1-3分钟）
                    
                    **详细步骤：** 查看 `QUICK_SECRETS_FIX.md` 或 `STREAMLIT_CLOUD_SECRETS_STEP_BY_STEP.md`
                    
                    ---
                    
                    ### 💻 本地开发
                    
                    1. **创建文件 `.streamlit/secrets.toml`**
                       ```toml
                       UF_LITELLM_BASE_URL = "https://api.ai.it.ufl.edu"
                       UF_LITELLM_API_KEY = "your-api-key-here"
                       ```
                    
                    2. **重启应用**
                    
                    ---
                    
                    **注意：** 即使未配置 API，应用仍可正常工作（使用本地 fallback 响应）
                    """)
            # 检查是否是 meta tensor 错误（服务器端问题）
            elif "meta tensor" in error_msg.lower() or "cannot copy out of meta tensor" in error_msg.lower():
                st.warning(get_error_message("api_server_error"))
                error_info = (
                    f"{get_error_message('problem_description')}\n\n"
                    f"{get_error_message('possible_causes')}\n"
                    f"{get_error_message('server_init')}\n"
                    f"{get_error_message('server_config')}\n"
                    f"{get_error_message('server_resources')}\n\n"
                    f"{get_error_message('solutions')}\n"
                    f"{get_error_message('wait_retry')}\n"
                    f"{get_error_message('auto_fallback')}\n"
                    f"{get_error_message('contact_it')}\n\n"
                    f"{get_error_message('technical_error')} {error_msg[:200]}"
                )
                st.info(error_info)
            # 其他错误
            else:
                st.warning(get_error_message("api_init_failed"))
                if error_msg:
                    st.caption(f"{get_error_message('error_details')}: {error_msg[:200]}")
            
            st.info(get_error_message("using_fallback"))
        else:
            # Client 已创建，检查是否有运行时错误
            if uf_api.last_error and ("meta tensor" in uf_api.last_error.lower() or "cannot copy out of meta tensor" in uf_api.last_error.lower()):
                # 只在第一次显示，避免重复
                if "uf_api_runtime_error_shown" not in st.session_state:
                    st.session_state.uf_api_runtime_error_shown = True
                    st.info(get_error_message("server_loading_issue"))
                st.success(get_error_message("api_initialized_fallback"))
            else:
                st.success(get_error_message("api_initialized"))
        
        # 只在本地环境显示调试功能（云端隐藏，更安全）
        # 使用之前定义的 is_really_local（双重检查）
        # 额外安全：明确检查是否为 True（防止任何意外情况）
        if is_really_local is True:  # 明确检查是否为 True
            with st.sidebar:
                st.markdown("---")
                st.caption("🔧 调试工具（仅本地）")
                if st.button("🔍 检查 Secrets 配置", help="检查 Streamlit Secrets 是否正确配置"):
                    st.write("### Secrets 配置检查")
                    try:
                        # 检查 Streamlit secrets
                        base_url_secret = st.secrets.get("UF_LITELLM_BASE_URL", "❌ 未找到")
                        api_key_secret = st.secrets.get("UF_LITELLM_API_KEY", "❌ 未找到")
                        
                        st.write("**从 Streamlit Secrets 读取：**")
                        st.write(f"- `UF_LITELLM_BASE_URL`: {base_url_secret if base_url_secret != '❌ 未找到' else '❌ 未找到'}")
                        st.write(f"- `UF_LITELLM_API_KEY`: {'✅ 已设置' if api_key_secret != '❌ 未找到' else '❌ 未找到'}")
                        
                        # 检查环境变量（作为备用）
                        base_url_env = os.getenv("UF_LITELLM_BASE_URL", "未设置")
                        api_key_env = os.getenv("UF_LITELLM_API_KEY", "未设置")
                        
                        st.write("**从环境变量读取（备用）：**")
                        st.write(f"- `UF_LITELLM_BASE_URL`: {base_url_env}")
                        st.write(f"- `UF_LITELLM_API_KEY`: {'✅ 已设置' if api_key_env != '未设置' else '❌ 未设置'}")
                        
                        # 检查实际使用的值
                        st.write("**实际使用的配置：**")
                        st.write(f"- Base URL: {uf_api.base_url if uf_api else 'N/A'}")
                        st.write(f"- API Key: {'✅ 已设置' if (uf_api and uf_api.api_key) else '❌ 未设置'}")
                        st.write(f"- Client 状态: {'✅ 已创建' if (uf_api and uf_api.client) else '❌ 未创建'}")
                        
                        if uf_api and uf_api.last_error:
                            st.warning(f"**错误信息**: {uf_api.last_error}")
                        
                    except Exception as e:
                        st.error(f"检查 Secrets 时出错: {e}")
                        st.info("💡 **提示**: 如果看到 'secrets' 相关的错误，说明 Streamlit Cloud 的 Secrets 没有正确配置。")
                        st.info("请按照 `CLOUD_SECRETS_TROUBLESHOOTING.md` 中的步骤配置 Secrets。")
        
        # Debug: 添加手动测试 API 按钮（仅在本地显示，云端隐藏）
        # 额外安全：明确检查 is_really_local 是否为 True
        if is_really_local is True and uf_api and uf_api.client:
            with st.sidebar:
                st.markdown("---")
                if st.button("🔧 Test UF API (debug)", help="Test API connection and model loading. Step 1: models.list() (no model loading). Step 2: chat.completions (tests actual model)"):
                    with st.spinner("Testing..."):
                        try:
                            st.write("**Base URL:**", uf_api.base_url)
                            st.write("**API key present:**", bool(uf_api.api_key))
                            
                            if not uf_api.api_key:
                                st.error("❌ **No API key configured!** Please set UF_LITELLM_API_KEY in Streamlit secrets.")
                                st.stop()
                            
                            # 第一步：测试 models.list()（不会触发模型加载）
                            st.write("\n**Step 1: Testing models.list()...**")
                            st.write("*(This only tests connectivity/auth, does NOT load models)*")
                            ms = uf_api.client.models.list()
                            st.success(f"✅ models.list() OK, found {len(ms.data)} models")
                            
                            # 显示可用模型列表（前10个）
                            if ms.data:
                                st.write("**Available models (first 10):**")
                                for model in ms.data[:10]:
                                    st.write(f"  - {model.id}")
                            
                            # 第二步：测试最小对话（使用小模型）
                            st.write("\n**Step 2: Testing chat.completions with llama-3.1-8b-instruct...**")
                            st.write("*(This will trigger model loading on the server)*")
                            model_name = "llama-3.1-8b-instruct"
                            r = uf_api.client.chat.completions.create(
                                model=model_name,
                                messages=[{"role": "user", "content": "Say hi in one sentence."}],
                                max_tokens=20,
                                timeout=30.0
                            )
                            st.success("✅ chat.completions OK")
                            st.write("**Response:**", r.choices[0].message.content)
                            
                            st.success("🎉 All tests passed! API is working correctly.")
                        except Exception as e:
                            error_msg = str(e)
                            st.error(f"❌ UF API test failed")
                            st.write("**Error:**", error_msg)
                            
                            # 判断错误类型
                            if "meta tensor" in error_msg.lower() or "torch" in error_msg.lower():
                                st.warning("⚠️ **Server-side model loading error**")
                                st.write("This error occurs when UF's server tries to load a PyTorch model but fails. This is **NOT a client-side issue**.")
                                st.info("💡 **Diagnosis:**")
                                st.write("  - If Step 1 (models.list) passed but Step 2 failed → The model `llama-3.1-8b-instruct` is failing to load on UF's server")
                                st.write("  - **Solution:** Contact UF IT or wait for server-side fix. You cannot fix this from your code.")
                            elif "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg.lower():
                                st.error("⚠️ **Authentication error**")
                                st.write("Your API key may be invalid or expired. Please check your `UF_LITELLM_API_KEY` in Streamlit secrets.")
                            elif "404" in error_msg or "not found" in error_msg.lower():
                                st.error("⚠️ **URL/Endpoint error**")
                                st.write(f"Check your base_url: `{uf_api.base_url}`. The endpoint may not exist.")
                            elif "timeout" in error_msg.lower():
                                st.warning("⚠️ **Timeout error**")
                                st.write("The server took too long to respond. This could indicate server overload or model loading issues.")
                            else:
                                st.write("**Full error traceback:**")
                                import traceback
                                st.code(traceback.format_exc()[:1000], language="python")
    
    # Main content area
    if not st.session_state.show_training:
        # Start Training Button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Training", type="primary", use_container_width=True):
                st.session_state.show_training = True
                # 不需要rerun，Streamlit会自动刷新
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
                format_func=lambda x: f"{x.upper()} - {persona_descriptions[x][:50]}...",
                index=personas.index(st.session_state.selected_persona) if st.session_state.selected_persona in personas else 0
            )
            
            # ===== 关键修复2：立即同步到 session_state =====
            st.session_state.selected_persona = selected_persona
            
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
                        "persona": st.session_state.selected_persona,
                        "message_count": len(st.session_state.messages),
                        "summary": f"Conversation with {len(st.session_state.messages)} messages"
                    }
                    save_to_google_sheets(session_data)
                
                # Reset session
                st.session_state.messages = []
                st.session_state.student_intents = []
                st.session_state.advisor_intents = []
                st.session_state.session_id = str(uuid.uuid4())[:8]
                
                # ✅ 关键：新对话输入框从 0 开始
                st.session_state.advisor_box_id = 0
                
                # ✅ 可选：清掉旧的 widget state（更干净）
                for k in list(st.session_state.keys()):
                    if k.startswith("advisor_input_"):
                        del st.session_state[k]
                
                st.rerun()
            
            if st.button("🏠 Back to Home"):
                st.session_state.show_training = False
                # 不需要rerun，Streamlit会自动刷新
    
    # --- 聊天界面修正版（方案2）---
    if st.session_state.show_training:
        st.header("💬 Training Conversation")

        # 1. 定义专门用于渲染的函数（解决乱码）
        # 消息列表中只存纯文本，标签只在渲染时动态生成
        def render_chat_bubble(role, content, intent_info=None):
            if not content:
                return
            
            from html import escape
            import re
            
            # 清理并转义内容（防止HTML注入和乱码）
            clean_content = re.sub(r'<[^>]+>', '', content)  # 先移除HTML标签
            escaped_content = escape(clean_content)  # 再转义特殊字符
            
            # 动态生成 Intent Badge 的 HTML（转义intent名称）
            badge_html = ""
            if intent_info:
                i_class = get_intent_badge_class(intent_info["intent"])
                i_name = escape(str(intent_info["intent"]))  # 转义intent名称
                i_conf = intent_info["confidence"]
                badge_html = f'<div class="intent-badge {i_class}">{i_name} • {i_conf:.1%}</div>'

            if role == "student":
                # 从 session_state 读取 persona（修复作用域问题）
                persona_display = st.session_state.selected_persona.upper()
                st.markdown(f"""
                <div class="chat-message student-message">
                    <strong>👨‍🎓 Student ({persona_display}):</strong> {escaped_content}
                    {badge_html}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message advisor-message">
                    <strong>👨‍🏫 You (Peer Advisor):</strong> {escaped_content}
                    {badge_html}
                </div>
                """, unsafe_allow_html=True)

        # 2. 先渲染历史消息
        s_idx, a_idx = 0, 0
        for msg in st.session_state.messages:
            if msg["role"] == "student":
                info = st.session_state.student_intents[s_idx] if s_idx < len(st.session_state.student_intents) else None
                render_chat_bubble("student", msg["content"], info)
                s_idx += 1
            else:
                info = st.session_state.advisor_intents[a_idx] if a_idx < len(st.session_state.advisor_intents) else None
                render_chat_bubble("advisor", msg["content"], info)
                a_idx += 1

        # 3. 初始化首条消息（如果是空的）
        if not st.session_state.messages:
            if st.button("🎯 Start Conversation"):
                with st.spinner("Student is thinking..."):
                    opening_text = None
                    if uf_api and knowledge_base:
                        opening_text = generate_student_opening_with_uf(
                            persona=st.session_state.selected_persona,
                            uf_api=uf_api,
                            knowledge_base=knowledge_base,
                            preferred_model=st.session_state.get("preferred_model", None)
                        )
                    if not opening_text:
                        opening_pool = STUDENT_PERSONAS[st.session_state.selected_persona]["opening_questions"]
                        opening_text = random.choice(opening_pool)

                    # 存储数据（只存纯文本！）
                    st.session_state.messages.append({
                        "role": "student",
                        "content": opening_text,
                        "timestamp": datetime.now()
                    })
                    st.session_state.student_intents.append(analyze_intent(opening_text, intent_classifier, "student"))
                    st.rerun()  # 仅在第一次启动对话时刷新

        # 4. Advisor input - 动态key强制重建输入框（最稳，100%清空）
        # ✅ 只保留这一段，确保没有其他输入框实现
        if st.session_state.messages:
            import re

            # 每次用一个全新的 key，保证输入框一定是"新建的空框"
            advisor_key = f"advisor_input_{st.session_state.advisor_box_id}"

            with st.form(f"advisor_form_{st.session_state.advisor_box_id}", clear_on_submit=True):
                advisor_input = st.text_area(
                    "Your response as peer advisor:",
                    placeholder="Type your response here...",
                    height=120,
                    key=advisor_key,
                )
                submitted = st.form_submit_button("📤 Send Response", use_container_width=True)

            if submitted:
                clean_input = re.sub(r"<[^>]+>", "", advisor_input or "").strip()

                try:
                    if clean_input:
                        a_intent = analyze_intent(clean_input, intent_classifier, "advisor")

                        st.session_state.messages.append({
                            "role": "advisor",
                            "content": clean_input,
                            "timestamp": datetime.now()
                        })
                        st.session_state.advisor_intents.append(a_intent)

                        with st.spinner("☁️ Student is typing..."):
                            # ✅ 改动2：真正生成回复时才调用 API；失败只 fallback，不要 kill client
                            uf_api = st.session_state.uf_api
                            knowledge_base = st.session_state.knowledge_base
                            
                            def _is_server_loading_error(msg: str) -> bool:
                                """判断是否是服务器端模型加载错误"""
                                m = (msg or "").lower()
                                return ("meta tensor" in m) or ("torch" in m)
                            
                            student_reply = None
                            
                            if uf_api and uf_api.client and knowledge_base:
                                try:
                                    # 这里才真正打 API
                                    persona_info = STUDENT_PERSONAS.get(st.session_state.selected_persona, {})
                                    preferred_model = st.session_state.get("preferred_model", None)
                                    
                                    student_reply = generate_student_reply_with_rag_uf(
                                        advisor_message=clean_input,
                                        persona=st.session_state.selected_persona,
                                        uf_api=uf_api,
                                        knowledge_base=knowledge_base,
                                        advisor_intent=a_intent["intent"],
                                        conversation_history=st.session_state.messages,
                                        persona_info=persona_info,          # ✅ 加上
                                        preferred_model=preferred_model     # ✅ 加上
                                    )
                                except Exception as e:
                                    emsg = str(e)
                                    if _is_server_loading_error(emsg):
                                        st.info(get_error_message("server_loading"))
                                    else:
                                        st.warning(f"{get_error_message('api_call_failed')}: {emsg[:200]}")
                                    # 不把 uf_api 设为 None，保留客户端以便后续重试
                            
                            # fallback（如果 API 返回 None 或调用失败）
                            if not student_reply:
                                student_reply = generate_student_reply_fallback(
                                    clean_input,
                                    st.session_state.selected_persona
                                )

                        student_reply_clean = re.sub(r"<[^>]+>", "", student_reply or "").strip()
                        s_intent = analyze_intent(student_reply_clean, intent_classifier, "student")

                        st.session_state.messages.append({
                            "role": "student",
                            "content": student_reply_clean,
                            "timestamp": datetime.now()
                        })
                        st.session_state.student_intents.append(s_intent)

                except Exception as e:
                    st.error(f"Error: {e}")

                finally:
                    # ✅ 无论成功失败，都换 key：下一次输入框一定是空白
                    st.session_state.advisor_box_id += 1
                    st.rerun()

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
