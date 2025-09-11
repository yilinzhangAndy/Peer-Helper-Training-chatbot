# 🌐 部署到云端指南

## 🚀 快速部署到 Streamlit Cloud

### 步骤 1: 准备 GitHub 仓库

```bash
# 在 chatbot 目录中初始化 Git
cd /Users/zhangyilin/Documents/UF/Ph.D/Chatbot/chatbot
git init
git add .
git commit -m "Initial commit: MAE Chatbot System for Cloud Deployment"
```

### 步骤 2: 创建 GitHub 仓库

1. 访问 [GitHub.com](https://github.com)
2. 点击 "New repository"
3. 仓库名：`mae-chatbot-system`
4. 描述：`MAE Peer Advisor Training System - AI-powered chatbot for engineering education`
5. 设为 Public（免费部署需要）
6. 点击 "Create repository"

### 步骤 3: 推送代码到 GitHub

```bash
# 添加远程仓库
git remote add origin https://github.com/你的用户名/mae-chatbot-system.git

# 推送代码
git push -u origin main
```

### 步骤 4: 部署到 Streamlit Cloud

1. 访问 [share.streamlit.io](https://share.streamlit.io)
2. 点击 "New app"
3. 连接你的 GitHub 账户
4. 选择仓库：`mae-chatbot-system`
5. 主文件：`web_app_cloud.py`
6. 点击 "Deploy"

### 步骤 5: 配置环境变量（如果需要）

在 Streamlit Cloud 设置中添加：
```
PYTHONPATH = .
```

## 🎯 部署后的功能

### ✅ 全球可访问
- 网址：`https://mae-chatbot-system-你的用户名.streamlit.app`
- 24/7 在线运行
- 无需你的电脑运行

### ✅ 完全免费
- 无 API 费用
- 无使用限制
- 开源可商用

### ✅ 功能完整
- 4种学生角色
- 实时意图分类
- 多轮对话训练
- 对话分析统计

## 🔄 更新部署

```bash
# 修改代码后
git add .
git commit -m "Update: 描述你的更新"
git push origin main

# 云端自动更新（1-3分钟）
```

## 📱 使用方式

1. **访问网站**：打开部署的网址
2. **选择角色**：选择要训练的学生类型
3. **开始对话**：作为 peer advisor 回答学生问题
4. **查看分析**：实时查看意图分类和统计
5. **分享给他人**：发送网址给其他同学/老师

## 🛠️ 故障排除

### 如果部署失败：
1. 检查 `requirements_cloud.txt` 是否包含所有依赖
2. 确保主文件是 `web_app_cloud.py`
3. 检查代码中是否有硬编码路径

### 如果模型加载失败：
1. 确保模型文件路径正确
2. 检查文件大小限制（Streamlit Cloud 有 1GB 限制）

## 🎉 预期结果

部署成功后，你将拥有：
- 🌐 **全球可访问的网站**
- 🆓 **完全免费的 AI 训练系统**
- 📊 **实时对话分析**
- 🎓 **专业的 MAE 教育工具**

## 📞 支持

如果遇到问题：
1. 检查 Streamlit Cloud 日志
2. 查看 GitHub Issues
3. 联系技术支持

---

**开始部署吧！让全世界都能使用你的 MAE 训练系统！** 🚀
