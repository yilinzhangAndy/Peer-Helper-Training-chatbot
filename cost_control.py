"""
Cost Control Module for MAE Chatbot
限制API使用量，控制成本
"""

import streamlit as st
import json
import time
from datetime import datetime, timedelta
import hashlib

class CostController:
    def __init__(self):
        self.daily_limit = 50  # 每日对话限制
        self.user_limit = 10   # 每用户每日限制
        self.session_limit = 5  # 每会话限制
        
    def check_user_limit(self, user_id):
        """检查用户使用限制"""
        if 'usage_stats' not in st.session_state:
            st.session_state.usage_stats = {}
        
        today = datetime.now().strftime('%Y-%m-%d')
        user_key = f"{user_id}_{today}"
        
        if user_key not in st.session_state.usage_stats:
            st.session_state.usage_stats[user_key] = {
                'count': 0,
                'last_reset': today
            }
        
        return st.session_state.usage_stats[user_key]['count'] < self.user_limit
    
    def increment_usage(self, user_id):
        """增加使用计数"""
        today = datetime.now().strftime('%Y-%m-%d')
        user_key = f"{user_id}_{today}"
        
        if user_key not in st.session_state.usage_stats:
            st.session_state.usage_stats[user_key] = {
                'count': 0,
                'last_reset': today
            }
        
        st.session_state.usage_stats[user_key]['count'] += 1
    
    def get_usage_info(self, user_id):
        """获取使用信息"""
        today = datetime.now().strftime('%Y-%m-%d')
        user_key = f"{user_id}_{today}"
        
        if user_key not in st.session_state.usage_stats:
            return 0, self.user_limit
        
        return (st.session_state.usage_stats[user_key]['count'], 
                self.user_limit)
    
    def check_session_limit(self):
        """检查会话限制"""
        if 'session_count' not in st.session_state:
            st.session_state.session_count = 0
        
        return st.session_state.session_count < self.session_limit
    
    def increment_session(self):
        """增加会话计数"""
        if 'session_count' not in st.session_state:
            st.session_state.session_count = 0
        st.session_state.session_count += 1

def get_user_id():
    """获取用户ID (基于IP和浏览器)"""
    # 简单的用户识别方法
    user_agent = st.get_option("browser.gatherUsageStats")
    return hashlib.md5(str(user_agent).encode()).hexdigest()[:8]

def show_usage_warning(remaining, total):
    """显示使用量警告"""
    if remaining <= 2:
        st.warning(f"⚠️ 今日剩余使用次数: {remaining}/{total}")
    elif remaining <= 5:
        st.info(f"ℹ️ 今日剩余使用次数: {remaining}/{total}")
    else:
        st.success(f"✅ 今日剩余使用次数: {remaining}/{total}")

def show_cost_info():
    """显示成本信息"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💰 使用说明")
    st.sidebar.markdown("""
    - 每用户每日限制: 10次对话
    - 每会话限制: 5次对话
    - 免费使用，无需注册
    - 支持多轮对话训练
    """)
    
    st.sidebar.markdown("### 🎯 使用建议")
    st.sidebar.markdown("""
    - 选择合适的学生角色
    - 充分利用每次对话
    - 查看分析结果
    - 分享给其他同学
    """)
