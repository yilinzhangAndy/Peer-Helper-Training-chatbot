"""
Local LLM Fallback Module
当API限制达到时，使用本地模型或规则回复
"""

import random
from typing import Dict, Any

class LocalLLMFallback:
    def __init__(self):
        self.fallback_responses = {
            "alpha": [
                "That's helpful, thank you. I'm still a bit unsure about some details though.",
                "I appreciate your advice. Could you help me understand this better?",
                "This makes sense. I'll think about what you've said.",
                "Thank you for your guidance. I'm still working on building confidence."
            ],
            "beta": [
                "I'm not sure if I understand completely. Could you explain that differently?",
                "I'm still confused about this. Maybe I'm not cut out for engineering.",
                "I don't want to bother you with more questions, but I'm still struggling.",
                "I'm embarrassed to ask, but I still don't get it."
            ],
            "delta": [
                "I see what you mean. I'll think about that approach.",
                "That's an interesting perspective. Let me consider it.",
                "I understand your point. I'll work on that.",
                "Thanks for the advice. I'll keep that in mind."
            ],
            "echo": [
                "That makes sense! I'm excited to try that out.",
                "Great advice! I'm confident this will work for me.",
                "Perfect! I'm ready to take on this challenge.",
                "Excellent! I love learning new approaches."
            ]
        }
    
    def generate_response(self, persona: str, advisor_intent: str = None) -> str:
        """生成本地回复"""
        responses = self.fallback_responses.get(persona, self.fallback_responses["alpha"])
        
        # 根据advisor意图调整回复
        if advisor_intent:
            if "feedback" in advisor_intent.lower():
                return random.choice([
                    "Thank you for the encouragement!",
                    "I appreciate your support.",
                    "That means a lot to me."
                ])
            elif "understanding" in advisor_intent.lower():
                return random.choice([
                    "I'm still not sure I understand completely.",
                    "Could you explain that in a different way?",
                    "I need more clarification on this."
                ])
        
        return random.choice(responses)

class CostAwarePipeline:
    def __init__(self, original_pipeline, cost_controller):
        self.original_pipeline = original_pipeline
        self.cost_controller = cost_controller
        self.local_fallback = LocalLLMFallback()
    
    def generate_student_reply(self, context, persona, advisor_intent=None, user_id=None):
        """成本感知的学生回复生成"""
        
        # 检查使用限制
        if user_id and not self.cost_controller.check_user_limit(user_id):
            st.warning("⚠️ 今日使用次数已达上限，使用本地回复模式")
            return self.local_fallback.generate_response(persona, advisor_intent)
        
        # 检查会话限制
        if not self.cost_controller.check_session_limit():
            st.warning("⚠️ 会话使用次数已达上限，使用本地回复模式")
            return self.local_fallback.generate_response(persona, advisor_intent)
        
        try:
            # 使用原始API
            response = self.original_pipeline.generate_student_reply(context, persona, advisor_intent)
            
            # 增加使用计数
            if user_id:
                self.cost_controller.increment_usage(user_id)
            self.cost_controller.increment_session()
            
            return response
            
        except Exception as e:
            st.error(f"API调用失败: {str(e)}")
            return self.local_fallback.generate_response(persona, advisor_intent)
