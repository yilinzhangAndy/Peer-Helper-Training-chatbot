"""
Local LLM Integration Module
集成免费的本地LLM模型，替代OpenAI API
"""

import os
import sys
from typing import Dict, Any, List
import json

class LocalLLMManager:
    def __init__(self):
        self.model_type = "rule_based"  # 可以改为 "ollama", "transformers", "rule_based"
        self.ollama_available = self._check_ollama()
        self.transformers_available = self._check_transformers()
    
    def _check_ollama(self) -> bool:
        """检查是否安装了Ollama"""
        try:
            import subprocess
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_transformers(self) -> bool:
        """检查是否安装了transformers"""
        try:
            import transformers
            return True
        except:
            return False
    
    def generate_response(self, prompt: str, persona: str, context: str = "") -> str:
        """生成回复"""
        if self.model_type == "ollama" and self.ollama_available:
            return self._generate_with_ollama(prompt, persona)
        elif self.model_type == "transformers" and self.transformers_available:
            return self._generate_with_transformers(prompt, persona)
        else:
            return self._generate_rule_based(prompt, persona, context)
    
    def _generate_with_ollama(self, prompt: str, persona: str) -> str:
        """使用Ollama生成回复"""
        try:
            import subprocess
            # 使用Ollama的llama2模型
            cmd = ["ollama", "run", "llama2", prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return self._generate_rule_based(prompt, persona, "")
        except:
            return self._generate_rule_based(prompt, persona, "")
    
    def _generate_with_transformers(self, prompt: str, persona: str) -> str:
        """使用transformers生成回复"""
        try:
            from transformers import pipeline
            # 使用免费的文本生成模型
            generator = pipeline("text-generation", 
                               model="microsoft/DialoGPT-medium",
                               max_length=100,
                               do_sample=True,
                               temperature=0.7)
            
            response = generator(prompt, max_length=len(prompt.split()) + 20)
            return response[0]['generated_text'].replace(prompt, "").strip()
        except:
            return self._generate_rule_based(prompt, persona, "")
    
    def _generate_rule_based(self, prompt: str, persona: str, context: str) -> str:
        """基于规则的回复生成"""
        # 分析prompt中的关键词
        prompt_lower = prompt.lower()
        
        # 根据关键词和persona生成回复
        if "help" in prompt_lower or "advice" in prompt_lower:
            return self._get_help_response(persona)
        elif "confused" in prompt_lower or "understand" in prompt_lower:
            return self._get_clarification_response(persona)
        elif "thank" in prompt_lower:
            return self._get_thanks_response(persona)
        elif "problem" in prompt_lower or "issue" in prompt_lower:
            return self._get_problem_response(persona)
        else:
            return self._get_general_response(persona)
    
    def _get_help_response(self, persona: str) -> str:
        responses = {
            "alpha": "I really appreciate your help. I'm working on building more confidence in my engineering skills.",
            "beta": "Thank you for offering to help. I'm still a bit hesitant to ask questions, but your support means a lot.",
            "delta": "I appreciate your guidance. I'll think about what you've suggested and see how it applies to my situation.",
            "echo": "That's exactly what I needed to hear! I'm excited to try out your suggestions."
        }
        return responses.get(persona, responses["alpha"])
    
    def _get_clarification_response(self, persona: str) -> str:
        responses = {
            "alpha": "I'm still a bit confused about some details. Could you help me understand this better?",
            "beta": "I'm not sure I understand completely. I don't want to seem stupid, but could you explain it differently?",
            "delta": "I see what you mean, but I'd like to make sure I understand correctly. Could you clarify?",
            "echo": "I think I understand, but let me make sure I've got it right. Could you confirm?"
        }
        return responses.get(persona, responses["alpha"])
    
    def _get_thanks_response(self, persona: str) -> str:
        responses = {
            "alpha": "Thank you so much for your help! I feel more confident about this now.",
            "beta": "I really appreciate you taking the time to help me. It means a lot.",
            "delta": "Thanks for the advice. I'll definitely consider what you've said.",
            "echo": "Thank you! This is exactly the kind of guidance I was looking for."
        }
        return responses.get(persona, responses["alpha"])
    
    def _get_problem_response(self, persona: str) -> str:
        responses = {
            "alpha": "I'm facing some challenges, but I'm determined to work through them. Any suggestions?",
            "beta": "I'm having some difficulties and I'm not sure how to handle them. I'm worried about asking for help.",
            "delta": "I've run into some issues. I'd like to solve them on my own, but I could use some guidance.",
            "echo": "I'm encountering some challenges, but I'm confident I can overcome them with the right approach."
        }
        return responses.get(persona, responses["alpha"])
    
    def _get_general_response(self, persona: str) -> str:
        responses = {
            "alpha": "That's interesting. I'd like to learn more about this topic.",
            "beta": "I'm not sure about this, but I'm trying to understand better.",
            "delta": "I see. Let me think about this and see how it applies to my situation.",
            "echo": "That's a great point! I'm excited to explore this further."
        }
        return responses.get(persona, responses["alpha"])

class FreeChatbotPipeline:
    def __init__(self, model_path="../pre-train/balanced_finetuned_model"):
        from models.intent_classifier import IntentClassifier
        from rag_system.vector_store import VectorStore
        from personas.persona_manager import PersonaManager
        
        self.classifier = IntentClassifier(model_path)
        self.vector_store = VectorStore()
        self.persona_manager = PersonaManager()
        self.local_llm = LocalLLMManager()
    
    def process_message(self, user_input, persona="alpha"):
        """处理用户消息（免费版本）"""
        # 1. 意图分类
        intent_result = self.classifier.classify(user_input)
        intent = intent_result["intent"]
        
        # 2. 检索相关知识
        context = self.vector_store.get_relevant_context(user_input, intent, persona)
        
        # 3. 使用本地LLM生成回复
        persona_info = self.persona_manager.get_persona(persona)
        persona_name = persona_info.get("name", "Advisor")
        
        prompt = f"User question: {user_input}\nContext: {context}\nRespond as {persona_name}:"
        
        answer = self.local_llm.generate_response(prompt, persona, context)
        
        return {
            "intent": intent,
            "context": context,
            "persona": persona,
            "answer": answer
        }
    
    def generate_student_reply(self, context, persona, advisor_intent=None):
        """生成学生回复（免费版本）"""
        from student_persona_manager import StudentPersonaManager
        
        spm = StudentPersonaManager()
        persona_info = spm.get_persona(persona)
        
        prompt = f"""You are a MAE student with persona {persona.upper()}.
Recent conversation: {context}
Advisor intent: {advisor_intent if advisor_intent else 'Unknown'}
Generate a natural follow-up response as this student."""
        
        return self.local_llm.generate_response(prompt, persona, context)
