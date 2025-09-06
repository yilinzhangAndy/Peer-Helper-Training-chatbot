import streamlit as st

# 设置页面配置
st.set_page_config(
    page_title="MAE Chatbot - Test Version",
    page_icon="🎓",
    layout="wide"
)

# 添加自定义CSS
st.markdown("""
<style>
    .test-box {
        background-color: #ff6b6b;
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 2rem 0;
    }
    .success-box {
        background-color: #51cf66;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 主标题
st.title("🎓 MAE Chatbot - Test Version")
st.markdown("---")

# 测试框
st.markdown('<div class="test-box">🚀 如果你看到这个红色框，说明部署成功了！</div>', unsafe_allow_html=True)

# 成功信息
st.markdown('<div class="success-box">✅ 背景颜色测试 - 这应该是绿色背景</div>', unsafe_allow_html=True)

# 说明
st.info("""
**测试说明：**
- 如果你看到红色和绿色的框，说明 CSS 样式正在工作
- 这证明我们的背景颜色修改是有效的
- 现在可以回到主应用查看效果
""")

# 链接到主应用
st.markdown("""
### 🔗 访问主应用：
- **简化版**: `web_app_cloud_simple.py`
- **完整版**: `web_app_cloud.py`
""")

st.success("🎉 部署测试完成！")
