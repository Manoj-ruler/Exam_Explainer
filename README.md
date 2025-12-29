# 🎓 Exam Explainer Bot

An AI-powered chatbot that explains examination and evaluation processes for students, built with **Streamlit** and **Google Gemini Flash**.

## ✨ Features

- **💬 AI Chat Interface**: Natural language conversations about academic processes
- **🌐 Multi-language Support**: Hindi, Telugu, Tamil, Kannada, and 5+ Indian languages
- **📊 Session Analytics**: Track questions asked, topics explored, and session duration
- **🛡️ Ethical Guardrails**: Won't predict grades or provide exam answers
- **⚡ Quick Actions**: One-click buttons for common queries
- **📚 Knowledge Base**: Extensible with custom academic regulations

## 🚀 Quick Start

### 1. Clone & Setup
```bash
cd exam-explainer-bot
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
copy .env.example .env
# Edit .env and add your Google AI Studio API key
```

Or enter the API key directly in the app sidebar.

### 4. Run the App
```bash
streamlit run app.py
```

Visit `http://localhost:8501` 🎉

## 📁 Project Structure

```
exam-explainer-bot/
├── app.py              # Main Streamlit application
├── gemini_client.py    # Google Gemini API integration
├── prompts.py          # System prompts & safety guardrails
├── knowledge_base.py   # Academic regulations knowledge base
├── analytics.py        # Session analytics tracking
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore file
└── data/
    └── regulations.json  # Academic regulations (auto-generated)
```

## 🧪 Test Queries

Try these sample queries:
- "Explain internal and external evaluation"
- "What is the revaluation process?"
- "Explain the grading system"
- "What are the exam rules?"
- "How is CGPA calculated?"

## 🛡️ Ethical Guidelines

This bot is designed with academic integrity in mind:

✅ **Will do:**
- Explain exam patterns and evaluation methods
- Clarify grading systems and calculations
- Describe revaluation processes
- Interpret academic regulations

❌ **Will NOT do:**
- Predict grades or exam outcomes
- Provide answers to exam questions
- Solve assignments or assessments
- Share confidential exam information

## 🔧 Customizing Knowledge Base

To add your institution's specific regulations:

1. Edit `data/regulations.json`
2. Or upload a PDF in the app (coming soon)

## 🌐 Supported Languages

- English
- Hindi (हिंदी)
- Telugu (తెలుగు)
- Tamil (தமிழ்)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)
- Marathi (मराठी)
- Bengali (বাংলা)
- Gujarati (ગુજરાતી)

## 📄 Tech Stack

- **Frontend**: Streamlit
- **AI**: Google Gemini 1.5 Flash
- **Language**: Python 3.10+

## 📄 License

MIT License

---

Built with ❤️ for students
