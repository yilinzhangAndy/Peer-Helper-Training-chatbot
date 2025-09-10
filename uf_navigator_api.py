import openai
import streamlit as st

class UFNavigatorAPI:
    def __init__(self):
        # 使用UF的LiteLLM代理API
        self.api_key = "sk-FEhqmwbGafXtX9sv07rZLw"
        self.api_base = "https://api.ai.it.ufl.edu"
        
        try:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            self.working_endpoint = self.api_base
            print(f"✅ UF LiteLLM API initialized successfully: {self.api_base}")
        except Exception as e:
            print(f"❌ Failed to initialize UF LiteLLM API: {str(e)}")
            self.client = None
            self.working_endpoint = "fallback"
    
    def generate_student_reply(self, advisor_message, persona, knowledge_context=""):
        """使用UF LiteLLM API生成学生回复"""
        try:
            if not self.client:
                return None
            
            # 构建增强prompt
            if knowledge_context:
                prompt = f"""
                Based on the following MAE professional knowledge:
                {knowledge_context}
                
                Peer Advisor said: {advisor_message}
                
                Please respond as a {persona} student based on the above information.
                Your response should:
                1. Reference relevant knowledge if applicable
                2. Match the {persona} student characteristics
                3. Be natural and conversational
                4. Be moderate length (1-3 sentences)
                5. Show the student's thinking process
                
                Response:
                """
            else:
                prompt = f"""
                You are a {persona} type student having a conversation with a peer advisor.
                
                Peer Advisor said: {advisor_message}
                
                Please generate a natural and authentic response based on the {persona} student characteristics.
                Your response should:
                1. Match the {persona} student personality traits
                2. Be natural and conversational
                3. Be moderate length (1-3 sentences)
                4. Show the student's thinking process
                
                Response:
                """
            
            # 调用UF LiteLLM API - 使用可用的模型
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instruct",  # 使用UF可用的模型
                messages=[
                    {"role": "system", "content": "You are a professional academic conversation assistant. Always respond in English."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.warning(f"UF LiteLLM API调用失败: {str(e)}")
            return None
    
    def test_connection(self):
        """测试API连接"""
        try:
            if not self.client:
                return False, "No client available"
            
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instruct",  # 使用UF可用的模型
                messages=[
                    {"role": "user", "content": "Hello, this is a test."}
                ],
                max_tokens=50
            )
            return True, f"✅ Connected to UF LiteLLM API: {response.choices[0].message.content}"
        except Exception as e:
            return False, f"❌ Failed to connect to UF LiteLLM API: {str(e)}"
