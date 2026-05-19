import os
import streamlit as st
from langchain_groq import ChatGroq
from datetime import datetime

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', sans-serif; }

.hero {
    background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
    padding: 2.5rem 2rem;
    border-radius: 20px;
    color: white;
    margin-bottom: 2rem;
}
.hero h1 { font-size: 2.5rem; font-weight: 800; margin: 0; }
.hero p { opacity: 0.8; margin: 0.5rem 0 0 0; font-size: 1.05rem; }
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    font-size: 0.78rem;
    margin: 0.5rem 0.2rem 0;
}

.score-card {
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    color: white;
    margin: 0.5rem 0;
}
.score-high { background: linear-gradient(135deg, #22c55e, #16a34a); }
.score-med { background: linear-gradient(135deg, #f59e0b, #d97706); }
.score-low { background: linear-gradient(135deg, #ef4444, #dc2626); }
.score-num { font-size: 3.5rem; font-weight: 800; line-height: 1; }
.score-lbl { font-size: 0.9rem; opacity: 0.9; margin-top: 0.3rem; }

.issue-card {
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    border-left: 4px solid;
}
.issue-bug { background: #fef2f2; border-color: #ef4444; }
.issue-security { background: #faf5ff; border-color: #8b5cf6; }
.issue-perf { background: #fffbeb; border-color: #f59e0b; }
.issue-style { background: #eff6ff; border-color: #3b82f6; }
.issue-ok { background: #f0fdf4; border-color: #22c55e; }

.issue-title { font-weight: 600; font-size: 0.9rem; }
.issue-desc { font-size: 0.83rem; color: #666; margin-top: 0.3rem; line-height: 1.5; }
.issue-fix { font-size: 0.82rem; color: #16a34a; margin-top: 0.3rem; font-style: italic; }

.stat-box {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.stat-val { font-size: 1.8rem; font-weight: 700; }
.stat-lbl { font-size: 0.72rem; color: #9ca3af; margin-top: 0.2rem; }

.code-block {
    background: #1e1e2e;
    border-radius: 12px;
    padding: 1.5rem;
    color: #cdd6f4;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.83rem;
    overflow-x: auto;
    line-height: 1.6;
}

.strength-card {
    background: #f0fdf4;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    border-left: 3px solid #22c55e;
    font-size: 0.88rem;
    color: #166534;
}

.history-item {
    background: #f9fafb;
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin: 0.3rem 0;
    font-size: 0.82rem;
    border-left: 3px solid #6366f1;
}

.test-header {
    background: linear-gradient(135deg, #1e1e2e, #2d2b55);
    border-radius: 12px 12px 0 0;
    padding: 0.8rem 1.2rem;
    color: white;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

EXAMPLE_CODE = '''def calculate_user_discount(price, discount_percent, user_type):
    if user_type == "admin":
        discount_percent = discount_percent + 20
    
    discount = price * discount_percent / 100
    final_price = price - discount
    
    if final_price < 0:
        final_price = 0
    
    return final_price


def authenticate_user(username, password):
    if password == "admin123":
        return {"user": username, "role": "admin", "token": "abc123"}
    else:
        return {"user": username, "role": "standard", "token": "xyz789"}


def read_config(filename):
    f = open(filename, "r")
    data = f.read()
    return data


def process_items(items):
    results = []
    for i in range(len(items)):
        item = items[i]
        if item not in results:
            results.append(item)
    return results


def get_user_data(user_id):
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()
'''

REVIEW_PROMPT = """You are a senior software engineer. Review this Python code thoroughly.

```python
{code}
```

Respond EXACTLY in this format:

OVERALL_SCORE: [1-10]

SUMMARY:
[2-3 sentence assessment]

BUGS:
- LINE [N]: [bug description] | FIX: [fix]
[or write "None found"]

SECURITY:
- [security issue] | FIX: [fix]
[or write "None found"]

PERFORMANCE:
- LINE [N]: [performance issue] | FIX: [improvement]
[or write "None found"]

STYLE:
- [style issue] | FIX: [suggestion]
[or write "Follows best practices"]

STRENGTHS:
- [strength 1]
- [strength 2]

IMPROVED_CODE:
```python
[complete improved version with all fixes applied]
```"""

TEST_PROMPT = """You are a senior test engineer. Write comprehensive pytest tests for this code.

```python
{code}
```

Include:
- Happy path tests
- Edge cases (None, empty, boundary values)
- Error/exception tests
- Parametrised tests where suitable

Return ONLY the test code:

```python
import pytest
{code_summary}
# Tests below
```"""

EXPLAIN_PROMPT = """Explain this Python code clearly for a junior developer.

```python
{code}
```

Cover:
## What This Code Does
[Plain English overview]

## Function by Function Breakdown
[Explain each function simply]

## Potential Issues to Watch
[2-3 things a developer should know]

## How to Improve It
[3 concrete suggestions]"""

# ── Session state ─────────────────────────────────────────────
if "review" not in st.session_state:
    st.session_state.review = None
if "tests" not in st.session_state:
    st.session_state.tests = None
if "explanation" not in st.session_state:
    st.session_state.explanation = None
if "history" not in st.session_state:
    st.session_state.history = []
if "code_input" not in st.session_state:
    st.session_state.code_input = ""


def get_llm(api_key, temp=0):
    return ChatGroq(model_name="llama3-8b-8192", temperature=temp, groq_api_key=api_key, max_tokens=2000)


def parse_score(text):
    for line in text.split("\n"):
        if "OVERALL_SCORE:" in line:
            try:
                return int(line.split(":")[-1].strip())
            except:
                pass
    return 7


def parse_section(text, section):
    items = []
    in_section = False
    sections = ["BUGS:", "SECURITY:", "PERFORMANCE:", "STYLE:", "STRENGTHS:", "IMPROVED_CODE:", "SUMMARY:"]
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped == section:
            in_section = True
            continue
        if in_section:
            if stripped in sections:
                break
            if stripped.startswith("-"):
                items.append(stripped[1:].strip())
    return [i for i in items if i and "none found" not in i.lower() and "follows best" not in i.lower()]


def parse_improved_code(text):
    if "IMPROVED_CODE:" in text and "```python" in text.split("IMPROVED_CODE:")[-1]:
        part = text.split("IMPROVED_CODE:")[-1]
        code = part.split("```python")[-1].split("```")[0]
        return code.strip()
    return ""


# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🔍 AI Code Reviewer</h1>
    <p>Instant code quality scores, bug detection, security analysis, and automated test generation for Python code</p>
    <div>
        <span class="hero-badge">🐛 Bug Detection</span>
        <span class="hero-badge">🔒 Security Analysis</span>
        <span class="hero-badge">⚡ Performance Review</span>
        <span class="hero-badge">🧪 Test Generation</span>
        <span class="hero-badge">✨ Code Improvement</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", help="Free at console.groq.com")

    st.divider()
    st.header("📝 Quick Load")
    if st.button("Load Example Code", use_container_width=True):
        st.session_state.code_input = EXAMPLE_CODE
        st.rerun()
    if st.button("Clear Code", use_container_width=True):
        st.session_state.code_input = ""
        st.session_state.review = None
        st.session_state.tests = None
        st.session_state.explanation = None
        st.rerun()

    if st.session_state.history:
        st.divider()
        st.header("📊 Review History")
        for item in reversed(st.session_state.history[-5:]):
            emoji = "🟢" if item["score"] >= 8 else "🟡" if item["score"] >= 6 else "🔴"
            st.markdown(f"""
<div class="history-item">
    {emoji} Score: <strong>{item['score']}/10</strong> · {item['bugs']} bugs · {item['security']} security<br>
    <small style="color:#9ca3af">{item['time']}</small>
</div>""", unsafe_allow_html=True)

if not api_key:
    st.info("👈 Enter your Groq API key to get started. Free at [console.groq.com](https://console.groq.com)")
    st.stop()

# ── Code Input ────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📝 Python Code")
    code_input = st.text_area(
        "Code",
        value=st.session_state.code_input,
        height=420,
        label_visibility="collapsed",
        placeholder="Paste your Python code here, or click 'Load Example Code' in the sidebar...",
        key="code_area"
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        review_btn = st.button("🔍 Review", use_container_width=True, type="primary")
    with c2:
        test_btn = st.button("🧪 Tests", use_container_width=True)
    with c3:
        explain_btn = st.button("💡 Explain", use_container_width=True)

with col2:
    if not st.session_state.review and not st.session_state.tests and not st.session_state.explanation:
        st.subheader("📊 Results")
        st.markdown("""
<div style="text-align:center;padding:3rem;color:#9ca3af">
    <div style="font-size:3rem;margin-bottom:1rem">🔍</div>
    <h3 style="color:#6b7280">Ready to Review</h3>
    <p>Paste code and click Review, Tests, or Explain</p>
</div>""", unsafe_allow_html=True)

# ── Actions ───────────────────────────────────────────────────
if review_btn and code_input.strip():
    llm = get_llm(api_key)
    with st.spinner("Reviewing your code..."):
        st.session_state.review = llm.invoke(REVIEW_PROMPT.format(code=code_input)).content
        st.session_state.tests = None
        st.session_state.explanation = None
    score = parse_score(st.session_state.review)
    bugs = parse_section(st.session_state.review, "BUGS:")
    security = parse_section(st.session_state.review, "SECURITY:")
    st.session_state.history.append({
        "score": score, "bugs": len(bugs), "security": len(security),
        "time": datetime.now().strftime("%H:%M")
    })

if test_btn and code_input.strip():
    llm = get_llm(api_key, 0.2)
    with st.spinner("Generating unit tests..."):
        raw = llm.invoke(TEST_PROMPT.format(code=code_input, code_summary="")).content
        if "```python" in raw:
            raw = raw.split("```python")[-1].split("```")[0]
        st.session_state.tests = raw.strip()
        st.session_state.review = None
        st.session_state.explanation = None

if explain_btn and code_input.strip():
    llm = get_llm(api_key, 0.3)
    with st.spinner("Generating explanation..."):
        st.session_state.explanation = llm.invoke(EXPLAIN_PROMPT.format(code=code_input)).content
        st.session_state.review = None
        st.session_state.tests = None

# ── Results ───────────────────────────────────────────────────
if st.session_state.review:
    review = st.session_state.review
    score = parse_score(review)
    bugs = parse_section(review, "BUGS:")
    security = parse_section(review, "SECURITY:")
    perf = parse_section(review, "PERFORMANCE:")
    style = parse_section(review, "STYLE:")
    strengths = parse_section(review, "STRENGTHS:")
    improved = parse_improved_code(review)

    with col2:
        score_class = "score-high" if score >= 8 else "score-med" if score >= 6 else "score-low"
        st.markdown(f'<div class="score-card {score_class}"><div class="score-num">{score}/10</div><div class="score-lbl">Code Quality Score</div></div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{"#ef4444" if bugs else "#22c55e"}">{len(bugs)}</div><div class="stat-lbl">Bugs</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{"#8b5cf6" if security else "#22c55e"}">{len(security)}</div><div class="stat-lbl">Security</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{"#f59e0b" if perf else "#22c55e"}">{len(perf)}</div><div class="stat-lbl">Perf</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#22c55e">{len(strengths)}</div><div class="stat-lbl">Good</div></div>', unsafe_allow_html=True)

    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs(["🐛 Issues", "💪 Strengths", "✨ Improved Code", "📄 Full Review"])

    with tab1:
        if bugs:
            st.markdown("### 🐛 Bugs")
            for b in bugs:
                parts = b.split("|")
                desc = parts[0].strip()
                fix = parts[1].replace("FIX:", "").strip() if len(parts) > 1 else ""
                st.markdown(f'<div class="issue-card issue-bug"><div class="issue-title">🔴 {desc}</div>{"<div class=issue-fix>✅ Fix: " + fix + "</div>" if fix else ""}</div>', unsafe_allow_html=True)

        if security:
            st.markdown("### 🔒 Security Issues")
            for s in security:
                parts = s.split("|")
                desc = parts[0].strip()
                fix = parts[1].replace("FIX:", "").strip() if len(parts) > 1 else ""
                st.markdown(f'<div class="issue-card issue-security"><div class="issue-title">🟣 {desc}</div>{"<div class=issue-fix>✅ Fix: " + fix + "</div>" if fix else ""}</div>', unsafe_allow_html=True)

        if perf:
            st.markdown("### ⚡ Performance Issues")
            for p in perf:
                parts = p.split("|")
                desc = parts[0].strip()
                fix = parts[1].replace("FIX:", "").strip() if len(parts) > 1 else ""
                st.markdown(f'<div class="issue-card issue-perf"><div class="issue-title">🟡 {desc}</div>{"<div class=issue-fix>✅ Fix: " + fix + "</div>" if fix else ""}</div>', unsafe_allow_html=True)

        if not bugs and not security and not perf:
            st.markdown('<div class="issue-card issue-ok"><div class="issue-title">✅ No critical issues found — well-written code!</div></div>', unsafe_allow_html=True)

    with tab2:
        for s in strengths:
            st.markdown(f'<div class="strength-card">✅ {s}</div>', unsafe_allow_html=True)

    with tab3:
        if improved:
            st.code(improved, language="python")
            st.download_button("💾 Download Improved Code", improved, file_name="improved_code.py", mime="text/plain")
        else:
            st.info("Improved code not extracted — view the Full Review tab.")

    with tab4:
        st.text(review)

if st.session_state.tests:
    st.subheader("🧪 Generated Unit Tests")
    st.caption("Auto-generated pytest tests — run with `pytest test_generated.py`")
    st.markdown('<div class="test-header">📄 test_generated.py</div>', unsafe_allow_html=True)
    st.code(st.session_state.tests, language="python")
    st.download_button("💾 Download Tests", st.session_state.tests, file_name="test_generated.py", mime="text/plain")

if st.session_state.explanation:
    st.subheader("💡 Code Explanation")
    st.markdown(st.session_state.explanation)
