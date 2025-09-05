# 🌐 部署到云端指南

## 方法一：Streamlit Cloud (推荐)

### 步骤 1: 准备 GitHub 仓库
```bash
# 初始化 Git 仓库
git init
git add .
git commit -m "Initial commit: MAE Chatbot System"

# 创建 GitHub 仓库并推送
# 在 GitHub 上创建新仓库，然后：
git remote add origin https://github.com/你的用户名/mae-chatbot.git
git push -u origin main
```

### 步骤 2: 部署到 Streamlit Cloud
1. 访问 https://share.streamlit.io/
2. 点击 "New app"
3. 连接你的 GitHub 仓库
4. 选择 `web_app.py` 作为主文件
5. 点击 "Deploy"

### 步骤 3: 配置环境变量
在 Streamlit Cloud 设置中添加：
```
OPENAI_API_KEY = 你的OpenAI API密钥
```

## 方法二：Heroku

### 步骤 1: 安装 Heroku CLI
```bash
# Mac
brew install heroku/brew/heroku

# 或下载安装包
# https://devcenter.heroku.com/articles/heroku-cli
```

### 步骤 2: 创建 Procfile
```bash
echo "web: streamlit run web_app.py --server.port \$PORT --server.address 0.0.0.0" > Procfile
```

### 步骤 3: 部署
```bash
heroku login
heroku create your-app-name
heroku config:set OPENAI_API_KEY=你的API密钥
git push heroku main
```

## 方法三：Railway

### 步骤 1: 安装 Railway CLI
```bash
npm install -g @railway/cli
```

### 步骤 2: 部署
```bash
railway login
railway init
railway up
```

## 🔧 部署前检查清单

- [ ] 所有依赖都在 `requirements.txt` 中
- [ ] 环境变量已设置 (OPENAI_API_KEY)
- [ ] 模型文件路径正确
- [ ] 没有硬编码的本地路径
- [ ] 测试过本地运行

## 📱 部署后的功能

部署成功后，你的应用将：
- ✅ 24/7 在线运行
- ✅ 全球可访问
- ✅ 自动更新 (GitHub 推送时)
- ✅ 支持多用户同时使用
- ✅ 移动端友好

## 🎯 预期网址格式

- **Streamlit Cloud**: `https://mae-chatbot-你的用户名.streamlit.app`
- **Heroku**: `https://your-app-name.herokuapp.com`
- **Railway**: `https://your-app-name.railway.app`

## 🆘 常见问题

### Q: 部署后模型加载失败？
A: 检查模型文件路径，可能需要上传到云端或使用在线模型

### Q: OpenAI API 调用失败？
A: 确保在云端设置了正确的环境变量

### Q: 应用启动慢？
A: 这是正常的，首次启动需要下载模型文件

## 🚀 快速部署命令

```bash
# 一键部署到 Streamlit Cloud
git add .
git commit -m "Deploy to cloud"
git push origin main
# 然后在 https://share.streamlit.io/ 创建应用
```
