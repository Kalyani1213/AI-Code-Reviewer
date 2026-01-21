import streamlit as st
from code_parser import parse_code
from style_checker import show_style_corrected
from error_detector import detect_errors
from ai_suggester import get_ai_suggestions
import re

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="😇",
    layout="wide",
)

# =========================
# Helpers
# =========================
def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def format_ai_output(text):
    """Format AI output with colored headers for display"""
    def style_header(match, emoji, color):
        header = match.group(1)
        return f'<b style="color:{color};">{emoji} {header}:</b>'
    
    text = re.sub(r'(Code Readability)\s*:', lambda m: style_header(m, '🟢', '#16a34a'), text)
    text = re.sub(r'(Performance)\s*:', lambda m: style_header(m, '🟡', '#ca8a04'), text)
    text = re.sub(r'(Best Practices)\s*:', lambda m: style_header(m, '🔵', '#2563eb'), text)
    return text.replace("\n", "<br>")

# =========================
# CSS
# =========================
st.markdown("""
<style>
.stApp {background: linear-gradient(to right, #f0fdf4, #ecfeff);}
[data-baseweb="button"] {background-color: #16a34a !important; color: white !important; border-radius: 12px !important; font-weight: bold !important; padding: 10px 16px !important; transition: all 0.2s ease-in-out;}
[data-baseweb="button"]:hover {background-color: #15803d !important; transform: scale(1.03);}
.code-box {background:#0f172a; color:#e5e7eb; padding:16px; border-radius:12px; font-family: monospace; font-size:15px; font-weight:bold; overflow-x:auto;}
.answer-box {background:#f0fdf4; padding:18px; border-radius:16px; border-left:6px solid #22c55e; font-size:16px;}
</style>
""", unsafe_allow_html=True)

# =========================
# Session State
# =========================
for key, default in {
    "analyzed_code": "",
    "ai_call_count": 0,
    "chat_history": [],
    "ai_suggestions": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown("## 🧠 AI Code Reviewer")
    st.markdown("#### Smart Python Analysis Tool")
    st.divider()
    st.markdown("""
    <div style="background-color:#dcfce7; padding:14px; border-radius:14px; border:1px solid #22c55e;">
        <b>✔ Features</b>
        <ul>
            <li>Syntax Validation</li>
            <li>Error Detection</li>
            <li>PEP8 Formatting</li>
            <li>AI Review + Improvement</li>
           
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.button("🔄 Reset Application", use_container_width=True, on_click=reset_app)

# =========================
# Header
# =========================
col1, col2 = st.columns([6, 2])
with col1:
    st.image("logo.png", width=250)
    st.title("AI Code Reviewer")
    st.caption("Analyze • Improve • Learn")
with col2:
    st.metric("AI Reviews Generated", st.session_state.ai_call_count)
st.divider()

# =========================
# Code Input Area
# =========================
code = st.text_area(
    "Paste Python code here",
    height=300,
    value=st.session_state.analyzed_code,
    placeholder="def hello():\n    print('Hello World')"
)

# =========================
# Buttons
# =========================
col_analysis, col_ai_sugg, col_improved = st.columns([2,2,2])

# ----- Analyze Code -----
with col_analysis:
    if st.button("🧪 Analyze Code", use_container_width=True):
        if not code.strip():
            st.warning("Enter code first!")
            st.stop()
        st.session_state.analyzed_code = code
        st.session_state.chat_history = []
        st.session_state.ai_suggestions = []
        st.session_state.ai_call_count = 0

        # Parse
        result = parse_code(code)
        if not result["success"]:
            st.error(result["error"]["message"])
            st.stop()
        st.success("✅ Code parsed successfully")

        # Errors
        err = detect_errors(code)
        if err["error_count"] > 0:
            for e in err["errors"]:
                st.error(e["message"])
        else:
            st.success("No static errors found")

        # Formatting
        try:
            style = show_style_corrected(code)
            if style["success"]:
                with st.expander("Formatted Code"):
                    st.code(style["corrected_code"], language="python")
        except:
            pass

# ----- AI Suggestions -----
with col_ai_sugg:
    if st.button("🤖 AI Suggestions", use_container_width=True):
        if not st.session_state.analyzed_code:
            st.info("Analyze code first.")
        else:
            with st.spinner("Generating suggestion..."):
                prompt = f"""
You are an expert Python developer.

Task: Provide a concise review of this code, ONLY 2–3 lines per section.

Include:
- Code Readability
- Performance
- Best Practices
- Time Complexity
- Space Complexity

Do NOT provide improved code.

Code:
{st.session_state.analyzed_code}
"""
                s = get_ai_suggestions(prompt, st.session_state.ai_call_count)
                s["message"] = format_ai_output(s["message"])
                st.session_state.ai_suggestions.append(s)
                st.session_state.ai_call_count += 1

# Display AI suggestions
st.divider()
for i, s in enumerate(st.session_state.ai_suggestions, 1):
    with st.expander(f"AI Review #{i}"):
        st.markdown(f"<div class='answer-box'>{s['message']}</div>", unsafe_allow_html=True)

# ----- Improved Code -----
with col_improved:
    if st.button("✨ Improved Code", use_container_width=True):
        if not st.session_state.analyzed_code:
            st.info("Analyze code first.")
        else:
            with st.spinner("Generating improved code..."):
                prompt = f"""
You are an expert Python developer.

Task: Return ONLY the improved working code. No explanations, no text.

Original Code:
{st.session_state.analyzed_code}
"""
                code_res = get_ai_suggestions(prompt, st.session_state.ai_call_count)
                st.session_state.ai_call_count += 1
                st.markdown(f"<div class='code-box'>{code_res['message']}</div>", unsafe_allow_html=True)

# =========================
# AI Chat Section
# =========================
st.divider()
st.markdown("### 💬 AI Chat")
question = st.text_input("Type your question here")

if st.button("Ask AI"):
    if not st.session_state.analyzed_code:
        st.warning("Analyze code first!")
        st.stop()

    q = question.lower()
    if "time" in q or "space" in q or "complexity" in q:
        prompt = f"""
You are an expert Python developer.

Code:
{st.session_state.analyzed_code}

User Question:
{question}

Rules:
1. Return ONLY Time Complexity and Space Complexity.
2. No explanations, no code, no extra sections.
"""
    elif "explain" in q or "why" in q:
        prompt = f"""
You are an expert Python assistant.

Code:
{st.session_state.analyzed_code}

User Question:
{question}

Rules:
Explain clearly and fully. No extra sections.
"""
    elif "code" in q or "implement" in q or "write" in q:
        prompt = f"""
You are an expert Python developer.

Code:
{st.session_state.analyzed_code}

User Question:
{question}

Rules:
Return ONLY the requested code. No explanations, no extra text.
"""
    else:
        prompt = f"""
You are an expert Python assistant.

Code:
{st.session_state.analyzed_code}

User Question:
{question}

Rules:
Answer exactly what the user asks. No extra text, no Code Readability/Performance/Best Practices unless asked.
"""

    with st.spinner("AI thinking..."):
        r = get_ai_suggestions(prompt, st.session_state.ai_call_count)
        r["message"] = format_ai_output(r["message"])
        st.session_state.chat_history.append({"question": question, "answer": r["message"]})
        st.session_state.ai_call_count += 1

# Display last AI answer
if st.session_state.chat_history:
    ans = st.session_state.chat_history[-1]["answer"]
    if "```" in ans or "def " in ans:
        st.markdown(f"<div class='code-box'>{ans}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='answer-box'>{ans}</div>", unsafe_allow_html=True)
