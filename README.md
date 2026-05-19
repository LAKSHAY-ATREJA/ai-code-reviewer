# 🔍 AI Code Reviewer & Test Generator

> Instant code quality scores, bug detection, security analysis, performance review, and automated pytest generation for Python code.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-Llama3-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

## 🚀 Live Demo

**[👉 Try it live here](https://your-app.streamlit.app)** ← Update after deployment

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 Code Review | Quality score 1-10 with detailed breakdown |
| 🐛 Bug Detection | Identifies bugs with line numbers and fix suggestions |
| 🔒 Security Analysis | Flags SQL injection, hardcoded credentials, unsafe file handling |
| ⚡ Performance Review | Identifies inefficient loops, memory issues, slow patterns |
| ✨ Improved Code | Auto-generates a fixed version of your code |
| 🧪 Test Generation | Creates comprehensive pytest tests with edge cases |
| 💡 Code Explanation | Plain English explanation for any code |
| 📊 Review History | Track scores across multiple sessions |

## 🏗️ Architecture

```
Python Code Input
     │
     ├──► Review Pipeline
     │       Groq LLM → Structured Analysis
     │       → Bug Report (line numbers + fixes)
     │       → Security Issues + Fixes
     │       → Performance Issues + Fixes
     │       → Improved Code Version
     │       → Quality Score (1-10)
     │
     ├──► Test Pipeline
     │       Groq LLM → pytest Tests
     │       → Happy paths
     │       → Edge cases
     │       → Error handling
     │       → Parametrised tests
     │
     └──► Explain Pipeline
             Groq LLM → Plain English Explanation
             → Function breakdown
             → Issues to watch
             → Improvement suggestions
```

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Groq (Llama3-8b-8192) |
| Orchestration | LangChain |
| Prompt Engineering | Structured output prompts |

## ⚡ Quick Start

```bash
git clone https://github.com/LAKSHAY-ATREJA/ai-code-reviewer
cd ai-code-reviewer

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

streamlit run app.py
```

## 🌐 Deploy Free on Streamlit Cloud

1. Fork this repo
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub → select this repo → deploy

## 🔍 What Gets Detected

```python
# Example: This code has bugs, security issues, and performance problems
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection!
    f = open("config.txt")  # Unclosed file handle!
    for i in range(len(items)):  # Inefficient loop!
        ...
```

The reviewer will catch all of these with line numbers and suggested fixes.

---

Built by [Lakshay Atreja](https://linkedin.com/in/lakshay-atreja) | [GitHub](https://github.com/LAKSHAY-ATREJA)
