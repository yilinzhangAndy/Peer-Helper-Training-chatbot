# Peer Helper Training Chatbot

A web-based training system for peer advisors to practice conversations with different types of MAE (Master of Arts in Education) students. The system uses AI-powered student personas and real-time intent classification to provide realistic training scenarios.

## 🌟 Features

- **🤖 AI-Powered Student Personas**: Four distinct student types (Alpha, Beta, Delta, Echo) with unique communication styles
- **🎯 Real-time Intent Classification**: Automatic classification using fine-tuned RoBERTa model (87% accuracy)
- **🧠 RAG-Enhanced Responses**: Student replies generated using Retrieval-Augmented Generation with MAE knowledge base
- **📊 Conversation Analysis**: Detailed statistics on talk-move distribution and transition patterns
- **🌐 Cloud Deployment**: Fully deployed on Streamlit Cloud for 24/7 global access
- **💬 Multi-turn Conversations**: Dynamic, context-aware dialogue with follow-up questions
- **🎓 Academic Focus**: Specialized for MAE (Master of Arts in Education) peer advisor training

## 🚀 Live Demo

**Access the training system**: [Peer Helper Training Chatbot](https://peer-apper-training-chatbot-an46q5yl8sqbcyqchwgnin.streamlit.app/)

> **Note**: The system is fully functional with real-time intent classification, AI-powered student personas, and conversation analysis. No registration required!

## ⚡ Quick Start

1. **🌐 Try the Web App**: Click the live demo link above
2. **👤 Select a Student Persona**: Choose from Alpha, Beta, Delta, or Echo
3. **💬 Start Training**: Begin a conversation with the AI student
4. **📊 Analyze Results**: View real-time intent classification and conversation statistics

## 🏗️ Architecture

### Core Components

- **`web_app_cloud_simple.py`**: Main Streamlit web application
- **`uf_navigator_api.py`**: UF LiteLLM API client for student reply generation
- **`simple_knowledge_base.py`**: RAG knowledge base with MAE program information
- **`student_persona_manager.py`**: Manages four distinct student personas
- **`models/intent_classifier.py`**: RoBERTa-based intent classification system

### Technology Stack

- **Frontend**: Streamlit web interface
- **LLM**: UF LiteLLM API with Llama 3.1 8B Instruct
- **Intent Classification**: RoBERTa model via Hugging Face Inference API
- **RAG**: SimpleKnowledgeBase with SentenceTransformers embeddings
- **Deployment**: Streamlit Cloud

## 👥 Student Personas

### Alpha Student
- **Characteristics**: Confident, goal-oriented, proactive
- **Communication Style**: Direct, assertive, asks specific questions
- **Typical Concerns**: Career planning, leadership opportunities, competitive advantages

### Beta Student
- **Characteristics**: Analytical, detail-oriented, methodical
- **Communication Style**: Thoughtful, asks clarifying questions, seeks comprehensive information
- **Typical Concerns**: Academic requirements, research opportunities, technical skills

### Delta Student
- **Characteristics**: Collaborative, relationship-focused, team-oriented
- **Communication Style**: Warm, inclusive, values peer connections
- **Typical Concerns**: Networking, group projects, community involvement

### Echo Student
- **Characteristics**: Creative, innovative, unconventional
- **Communication Style**: Expressive, asks open-ended questions, explores possibilities
- **Typical Concerns**: Creative projects, interdisciplinary opportunities, unique career paths

## 🎯 Intent Classification

The system classifies conversation intents into five categories:

1. **Exploration and Reflection**: Questions about interests, goals, and self-discovery
2. **Goal Setting and Planning**: Specific planning and decision-making discussions
3. **Problem Solving and Critical Thinking**: Analytical problem-solving approaches
4. **Feedback and Support**: Providing encouragement and constructive feedback
5. **Understanding and Clarification**: Seeking or providing clarification and information

## 📊 Conversation Analysis

The system provides detailed analysis including:

- **Intent Distribution**: Count of each intent type for both student and advisor
- **Question-Answer Pair Analysis**: Comparison of student and advisor intent matching
- **Talk-Move Patterns**: Analysis of conversation flow and transitions

## 🛠️ Local Development

### Prerequisites

- Python 3.11+
- Conda environment manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yilinzhangAndy/Peer-Helper-Training-chatbot.git
   cd Peer-Helper-Training-chatbot/chatbot
   ```

2. **Create and activate conda environment**:
   ```bash
   conda create -n chatbot python=3.11
   conda activate chatbot
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   streamlit run web_app_cloud_simple.py
   ```

### Local CLI Training Scripts

For local development and testing, the repository includes several CLI training scripts:

- **`advisor_training_multiturn_with_intent.py`**: Full-featured CLI training with intent classification and conversation analysis
- **`advisor_training_multiturn.py`**: Basic CLI training with multi-turn conversations
- **`advisor_training.py`**: Simple CLI training script
- **`direct_test.py`**: Direct testing script for components
- **`test_pipeline.py`**: Pipeline testing script
- **`test_step2.py`**: Step 2 testing script

To run CLI training:
```bash
python advisor_training_multiturn_with_intent.py
```

### Environment Variables

The application uses the following API keys (configured in the code):

- **UF LiteLLM API**: For student reply generation (configured in `uf_navigator_api.py`)
- **Hugging Face API**: For intent classification (configured in `models/intent_classifier.py`)

## 📁 Project Structure

```
chatbot/
├── web_app_cloud_simple.py                    # Main Streamlit application
├── uf_navigator_api.py                        # UF LiteLLM API client
├── simple_knowledge_base.py                   # RAG knowledge base
├── student_persona_manager.py                 # Student persona management
├── advisor_training_multiturn_with_intent.py  # Local CLI training script
├── advisor_training_multiturn.py              # Basic CLI training script
├── advisor_training.py                        # Simple CLI training script
├── direct_test.py                             # Direct testing script
├── test_pipeline.py                           # Pipeline testing script
├── test_step2.py                              # Step 2 testing script
├── models/
│   ├── __init__.py
│   └── intent_classifier.py                   # RoBERTa intent classifier
├── core/
│   └── chatbot_pipeline.py                    # Core chatbot pipeline
├── personas/
│   ├── __init__.py
│   └── persona_manager.py                     # Persona management system
├── analysis/
│   └── __init__.py                            # Analysis module
├── knowledge_base/
│   ├── faq_knowledge.json                     # FAQ knowledge base
│   ├── scenario_knowledge.json                # Scenario-based knowledge
│   └── training_knowledge.json                # Training resources
├── requirements.txt                           # Python dependencies
└── README.md                                  # This file
```

## 🔧 Configuration

### UF LiteLLM API Setup

The system uses UF's LiteLLM API with the following configuration:

- **Endpoint**: `https://api.ai.it.ufl.edu`
- **Model**: `llama-3.1-8b-instruct`
- **API Key**: Configured in `uf_navigator_api.py`

### Hugging Face API Setup

Intent classification uses Hugging Face Inference API:

- **Model**: `zylandy/mae-intent-classifier`
- **API Key**: Configured in `models/intent_classifier.py`

## 🚀 Deployment

The application is automatically deployed to Streamlit Cloud:

- **Repository**: `yilinzhangandy/peer-helper-training-chatbot`
- **Branch**: `main`
- **Entry Point**: `web_app_cloud_simple.py`

### Deployment Process

1. Push changes to the `main` branch
2. Streamlit Cloud automatically detects changes and redeploys
3. The application is available at the provided URL

## 📈 Usage Statistics

The system tracks and analyzes:

- **Conversation Length**: Number of exchanges per session
- **Intent Distribution**: Frequency of different conversation intents
- **Persona Engagement**: Which student types are most commonly practiced with
- **Advisor Performance**: Patterns in advisor responses and effectiveness

## 🔬 Research Applications

This system is designed for:

- **🎓 Peer Advisor Training**: Practice conversations with diverse student types
- **📈 Conversation Analysis**: Study talk-move patterns and intent transitions
- **🔍 Educational Research**: Analyze advisor-student interaction patterns
- **💡 Skill Development**: Improve communication and advising skills
- **📊 Data Collection**: Gather conversation data for academic research
- **🤖 AI in Education**: Explore AI-assisted training methodologies

## 🤝 Contributing

This is a research project for MAE education. For contributions or questions:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is developed for academic research purposes in MAE education.

## 🙏 Acknowledgments

- **University of Florida**: For providing the LiteLLM API access
- **Hugging Face**: For the inference API and model hosting
- **Streamlit**: For the web application framework
- **Meta**: For the Llama 3.1 8B Instruct model

## 📞 Support

For technical issues or questions about the system:

- Check the live demo for current functionality
- Review the code comments for implementation details
- Contact the development team for research collaboration

---

## 📈 System Status

- **✅ Web Application**: Fully operational on Streamlit Cloud
- **✅ Intent Classification**: RoBERTa model with 87% accuracy
- **✅ Student Personas**: Four distinct AI personas active
- **✅ RAG System**: Knowledge base with MAE program information
- **✅ Conversation Analysis**: Real-time statistics and patterns
- **✅ API Integration**: UF LiteLLM API with Llama 3.1 8B Instruct

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready & Research Active
