"""
Llama 3.1 8B Instruct Integration for MAE Chatbot
集成 Llama 3.1 模型，替代 OpenAI API
"""

import subprocess
import json
import time
from typing import Dict, Any, List
import re

class Llama3Manager:
    def __init__(self, model_name="llama3.1:8b"):
        self.model_name = model_name
        self.max_retries = 3
        self.timeout = 30
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """使用 Llama 3.1 生成回复"""
        
        # 构建完整的提示
        full_prompt = self._build_prompt(prompt, system_prompt)
        
        for attempt in range(self.max_retries):
            try:
                # 调用 Ollama
                result = subprocess.run([
                    "ollama", "run", self.model_name, full_prompt
                ], capture_output=True, text=True, timeout=self.timeout)
                
                if result.returncode == 0:
                    response = result.stdout.strip()
                    # 清理响应
                    response = self._clean_response(response, prompt)
                    return response
                else:
                    print(f"Ollama error (attempt {attempt + 1}): {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"Timeout (attempt {attempt + 1})")
            except Exception as e:
                print(f"Error (attempt {attempt + 1}): {e}")
            
            if attempt < self.max_retries - 1:
                time.sleep(2)  # 等待后重试
        
        # 如果所有尝试都失败，返回默认回复
        return "I'm sorry, I'm having trouble responding right now. Could you please try again?"
    
    def _build_prompt(self, prompt: str, system_prompt: str = None) -> str:
        """构建完整的提示"""
        if system_prompt:
            return f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        else:
            return f"User: {prompt}\n\nAssistant:"
    
    def _clean_response(self, response: str, original_prompt: str) -> str:
        """清理响应，移除重复的提示内容"""
        # 移除可能重复的提示部分
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 跳过包含原始提示的行
            if original_prompt.lower() not in line.lower():
                # 移除 "Assistant:" 前缀
                if line.startswith("Assistant:"):
                    line = line[10:].strip()
                cleaned_lines.append(line)
        
        cleaned_response = '\n'.join(cleaned_lines).strip()
        
        # 如果响应太短或为空，返回默认回复
        if len(cleaned_response) < 10:
            return "Thank you for your question. I'll do my best to help you."
        
        return cleaned_response

class Llama3ChatbotPipeline:
    def __init__(self, model_path="../pre-train/balanced_finetuned_model"):
        from models.intent_classifier import IntentClassifier
        from rag_system.vector_store import VectorStore
        from personas.persona_manager import PersonaManager
        
        self.classifier = IntentClassifier(model_path)
        self.vector_store = VectorStore()
        self.persona_manager = PersonaManager()
        self.llama3 = Llama3Manager()
    
    def process_message(self, user_input, persona="alpha"):
        """处理用户消息（使用 Llama 3.1）"""
        # 1. 意图分类
        intent_result = self.classifier.classify(user_input)
        intent = intent_result["intent"]
        
        # 2. 检索相关知识
        context = self.vector_store.get_relevant_context(user_input, intent, persona)
        
        # 3. 构建系统提示
        persona_info = self.persona_manager.get_persona(persona)
        persona_name = persona_info.get("name", "Advisor")
        persona_desc = persona_info.get("description", "")
        
        system_prompt = f"""You are a helpful MAE (Mechanical and Aerospace Engineering) peer advisor named {persona_name}.
Your characteristics: {persona_desc}
User's intent: {intent}
Relevant context: {context}

Please provide helpful, encouraging advice in the style of {persona_name}. Keep your response concise (2-3 sentences) and supportive."""
        
        # 4. 使用 Llama 3.1 生成回复
        answer = self.llama3.generate_response(user_input, system_prompt)
        
        return {
            "intent": intent,
            "context": context,
            "persona": persona,
            "answer": answer
        }
    
    def generate_student_reply(self, context, persona, advisor_intent=None):
        """生成学生回复（使用 Llama 3.1）"""
        from student_persona_manager import StudentPersonaManager
        
        spm = StudentPersonaManager()
        persona_info = spm.get_persona(persona)
        
        # 构建系统提示
        system_prompt = f"""You are a MAE student with the following characteristics:
Persona: {persona.upper()}
Description: {persona_info['description']}
Traits: {persona_info['traits']}
Help Seeking Behavior: {persona_info['help_seeking_behavior']}

The advisor just responded with intent: {advisor_intent if advisor_intent else 'Unknown'}

Generate a natural follow-up response as this student. Your response should:
1. Be consistent with your persona's traits and help-seeking behavior
2. Show appropriate engagement with the advisor's response
3. Be natural and conversational
4. Be 1-2 sentences long
5. Reflect your personality and confidence level"""
        
        # 构建用户提示
        user_prompt = f"Recent conversation:\n{context}\n\nGenerate a student response:"
        
        # 使用 Llama 3.1 生成回复
        return self.llama3.generate_response(user_prompt, system_prompt)

def test_llama3_integration():
    """测试 Llama 3.1 集成"""
    print("🧪 Testing Llama 3.1 integration...")
    
    try:
        pipeline = Llama3ChatbotPipeline()
        
        # 测试 advisor 回复
        print("Testing advisor response...")
        advisor_result = pipeline.process_message(
            "I'm struggling with my engineering classes. What should I do?",
            persona="alpha"
        )
        print(f"Advisor response: {advisor_result['answer']}")
        
        # 测试学生回复
        print("\nTesting student response...")
        student_reply = pipeline.generate_student_reply(
            context="advisor: You should seek help from professors and join study groups.\nstudent: I'm considering applying for a research position...",
            persona="alpha",
            advisor_intent="Feedback and Support"
        )
        print(f"Student response: {student_reply}")
        
        print("\n✅ Llama 3.1 integration test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    test_llama3_integration()
