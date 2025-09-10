import openai
import streamlit as st

class UFNavigatorAPI:
    def __init__(self):
        # 设置UF Navigator API
        self.api_key = "sk-FEhqmwbGafXtX9sv07rZLw"
        self.api_base = "https://navigator.ufl.edu/api/v1"
        
        # 配置OpenAI客户端 (新版本)
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
    
    def generate_student_reply(self, advisor_message, persona, knowledge_context=""):
        """使用UF Navigator API生成学生回复"""
        try:
            # 构建增强prompt
            if knowledge_context:
                prompt = f"""
                基于以下MAE专业知识：
                {knowledge_context}
                
                Peer Advisor说：{advisor_message}
                
                请作为{persona}学生，基于以上信息生成回复。
                回复应该：
                1. 引用相关知识（如果相关）
                2. 符合{persona}学生特点
                3. 自然流畅，像真实对话
                4. 长度适中（1-3句话）
                5. 体现学生的思考过程
                
                回复：
                """
            else:
                prompt = f"""
                你是一个{persona}类型的学生，正在与peer advisor对话。
                
                Peer Advisor说：{advisor_message}
                
                请基于{persona}学生的特点，生成一个自然、真实的回复。
                回复应该：
                1. 符合{persona}学生的性格特点
                2. 自然流畅，像真实对话
                3. 长度适中（1-3句话）
                4. 体现学生的思考过程
                
                回复：
                """
            
            # 调用UF Navigator API (新版本)
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的学术对话助手。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.warning(f"UF Navigator API调用失败: {str(e)}")
            return None
    
    def test_connection(self):
        """测试API连接"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": "Hello, this is a test."}
                ],
                max_tokens=50
            )
            return True, response.choices[0].message.content
        except Exception as e:
            return False, str(e)
