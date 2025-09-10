import openai
import streamlit as st

class UFNavigatorAPI:
    def __init__(self):
        # UF Navigator API目前不可用，将使用fallback机制
        self.api_key = "sk-FEhqmwbGafXtX9sv07rZLw"
        self.client = None
        self.working_endpoint = "fallback"
        print("UF Navigator API not available, using fallback responses")
    
    def generate_student_reply(self, advisor_message, persona, knowledge_context=""):
        """使用UF Navigator API生成学生回复"""
        # UF Navigator API目前不可用，返回None以触发fallback
        return None
    
    def test_connection(self):
        """测试API连接"""
        return False, "UF Navigator API not available, using fallback responses"
