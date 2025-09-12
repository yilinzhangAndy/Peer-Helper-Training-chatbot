import os
from models.intent_classifier import IntentClassifier
from rag_system.vector_store import VectorStore
from personas.persona_manager import PersonaManager
import openai
from dotenv import load_dotenv

# 自动加载.env文件
load_dotenv()

class ChatbotPipeline:
    def __init__(self, model_path="../pre-train/balanced_finetuned_model"):
        self.classifier = IntentClassifier(model_path)
        self.vector_store = VectorStore()
        self.persona_manager = PersonaManager()
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = openai.OpenAI(api_key=api_key)

    def process_message(self, user_input, persona="alpha"):
        # 1. 意图分类
        intent_result = self.classifier.classify(user_input)
        intent = intent_result["intent"]

        # 2. 检索相关知识
        context = self.vector_store.get_relevant_context(user_input, intent, persona)

        # 3. 构建prompt，调用OpenAI生成回复
        persona_info = self.persona_manager.get_persona(persona)
        persona_name = persona_info.get("name", "Advisor")
        persona_desc = persona_info.get("description", "")

        prompt = (
            f"You are a MAE peer advisor, persona: {persona_name} ({persona_desc}).\n"
            f"User intent: {intent}\n"
            f"User question: {user_input}\n"
            f"Relevant context: {context}\n"
            f"Please answer in the style of {persona_name}, using the context if possible."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful MAE peer advisor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"(LLM error: {e})\nContext: {context}"

        # 4. 返回结果
        return {
            "intent": intent,
            "context": context,
            "persona": persona,
            "answer": answer
        }
    
    def generate_student_reply(self, context, persona, advisor_intent=None):
        """Generate a student reply based on conversation context and advisor's response"""
        from student_persona_manager import StudentPersonaManager
        
        # Get student persona information
        spm = StudentPersonaManager()
        persona_info = spm.get_persona(persona)
        
        # Build prompt for student response
        prompt = f"""You are a MAE student with the following characteristics:
Persona: {persona.upper()}
Description: {persona_info['description']}
Traits: {persona_info['traits']}
Help Seeking Behavior: {persona_info['help_seeking_behavior']}

Recent conversation:
{context}

The advisor just responded with intent: {advisor_intent if advisor_intent else 'Unknown'}

Based on your persona characteristics and the conversation so far, generate a natural follow-up response as this student. 
Your response should:
1. Be consistent with your persona's traits and help-seeking behavior
2. Show appropriate engagement with the advisor's response
3. Be natural and conversational
4. Be 1-3 sentences long

Student response:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a MAE student responding to a peer advisor. Stay in character based on your persona."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Fallback responses based on persona
            fallback_responses = {
                "alpha": "That's helpful, thank you. I'm still a bit unsure about some details though.",
                "beta": "I'm not sure if I understand completely. Could you explain that differently?",
                "delta": "I see what you mean. I'll think about that approach.",
                "echo": "That makes sense! I'm excited to try that out."
            }
            return fallback_responses.get(persona, "Thank you for your help. I'll consider what you've said.") 