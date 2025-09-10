# RAG + UF Navigator API Deployment Guide

## 🚀 **最新部署：RAG + UF Navigator API集成**

### **系统架构**
```
用户输入 → RoBERTa分类 → ChromaDB检索 → UF Navigator API (GPT-4) → 智能回复
```

### **核心优势**
- ✅ **完全免费**：UF Navigator API无限制使用
- ✅ **效果最佳**：GPT-4 + 专业知识库
- ✅ **稳定可靠**：学校服务器支持
- ✅ **专业性强**：基于MAE知识库
- ✅ **智能检索**：RAG增强回复质量

### **技术栈**
- **前端**：Streamlit
- **LLM**：UF Navigator API (GPT-4)
- **向量数据库**：ChromaDB
- **嵌入模型**：SentenceTransformers
- **意图分类**：RoBERTa (HF Inference API)
- **部署平台**：Streamlit Cloud

### **文件结构**
```
chatbot/
├── web_app_cloud_simple.py    # 主应用
├── uf_navigator_api.py        # UF Navigator API集成
├── mae_knowledge_base.py      # MAE知识库
├── requirements.txt           # 依赖包
└── README_RAG_UF_DEPLOYMENT.md # 部署说明
```

### **部署步骤**

#### **1. 自动部署（推荐）**
代码已推送到GitHub，Streamlit Cloud会自动检测并部署：
- Repository: `yilinzhangandy/peer-helper-training-chatbot`
- Branch: `main`
- Main file: `web_app_cloud_simple.py`

#### **2. 手动部署**
如果需要手动部署：
1. 访问 [Streamlit Cloud](https://share.streamlit.io/)
2. 连接GitHub仓库
3. 选择分支：`main`
4. 主文件：`web_app_cloud_simple.py`
5. 点击"Deploy"

### **功能特性**

#### **智能回复生成**
- **RAG增强**：基于MAE专业知识库检索
- **GPT-4质量**：UF Navigator API提供高质量生成
- **语义理解**：智能分析advisor消息内容
- **个性化回复**：基于4种学生persona特点

#### **知识库内容**
- **课程信息**：MAE课程要求、专业方向
- **职业发展**：就业方向、实习机会
- **学术政策**：毕业要求、GPA要求
- **学习技巧**：时间管理、学习方法

#### **Fallback机制**
- **多层保障**：UF API → 语义Fallback → 基础Fallback
- **智能分类**：基于advisor消息语义选择回复类型
- **多样化回复**：每个persona 20种不同回复

### **使用说明**

#### **访问网站**
- URL: `https://peer-apper-training-chatbot-an46q5yl8sqbcyqchwgnin.streamlit.app/`
- 无需注册，直接使用
- 支持全球访问

#### **训练流程**
1. **选择Persona**：Alpha/Beta/Delta/Echo
2. **开始对话**：点击"Start Conversation"
3. **回复学生**：输入你的advisor回复
4. **获得反馈**：实时意图分类和分析

#### **分析功能**
- **意图分布**：学生和advisor的意图统计
- **对话分析**：Q→A配对分析
- **实时分类**：每条消息的意图识别

### **技术细节**

#### **UF Navigator API配置**
```python
api_key = "sk-FEhqmwbGafXtX9sv07rZLw"
api_base = "https://navigator.ufl.edu/api/v1"
model = "gpt-4"
```

#### **知识库检索**
```python
# 检索相关文档
relevant_docs = knowledge_base.search(advisor_message)
# 构建增强prompt
enhanced_prompt = f"基于以下MAE专业知识：{knowledge_context}"
```

#### **智能Fallback**
```python
# 语义分析advisor消息
if "encouragement" in advisor_message:
    category = "encouragement"
elif "clarification" in advisor_message:
    category = "clarification"
# 选择对应回复
```

### **性能优化**

#### **缓存机制**
- Streamlit `@st.cache_resource` 缓存组件
- 知识库初始化缓存
- API连接状态缓存

#### **错误处理**
- 多层异常捕获
- 优雅降级机制
- 用户友好的错误提示

### **监控和维护**

#### **API状态监控**
- 实时连接测试
- 自动重连机制
- 状态指示器

#### **性能指标**
- 回复生成时间
- API调用成功率
- 用户满意度

### **未来扩展**

#### **知识库扩展**
- 添加更多MAE专业知识
- 集成最新政策信息
- 支持多语言知识库

#### **功能增强**
- 对话历史保存
- 个性化推荐
- 高级分析功能

### **故障排除**

#### **常见问题**
1. **API连接失败**：检查网络连接和API密钥
2. **知识库加载慢**：首次加载需要时间，后续会缓存
3. **回复质量差**：检查知识库内容和prompt设计

#### **技术支持**
- 检查Streamlit Cloud日志
- 验证GitHub代码同步
- 测试本地运行环境

### **总结**

RAG + UF Navigator API集成提供了：
- **最佳效果**：GPT-4 + 专业知识
- **完全免费**：学校API无限制使用
- **稳定可靠**：多层保障机制
- **易于维护**：模块化设计

这个方案完美解决了成本、效果和稳定性的平衡，是当前最佳的部署方案。
