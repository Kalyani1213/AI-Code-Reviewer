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
    """
    Clear all session state variables and rerun the app
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def format_ai_output(text):
    """
    Format AI output:
    - Only headers (Code Readability, Performance, Best Practices) are bold and colored.
    - Content under the headers remains normal font.
    """

    import re

    # Pattern to match header (with colon) but only style the header, leave content
    def style_header(match, emoji, color):
        header = match.group(1)  # The header text
        return f'<b style="color:{color};">{emoji} {header}:</b>'

    # Replace headers individually
    text = re.sub(r'(Code Readability)\s*:', lambda m: style_header(m, '🟢', '#16a34a'), text)
    text = re.sub(r'(Performance)\s*:', lambda m: style_header(m, '🟡', '#ca8a04'), text)
    text = re.sub(r'(Best Practices)\s*:', lambda m: style_header(m, '🔵', '#2563eb'), text)

    # Replace newlines with <br> for HTML rendering
    text = text.replace("\n", "<br>")

    return text


# =========================
# CSS Styling for buttons, tabs, code
# =========================
st.markdown("""
<style>
/* App background */
.stApp {
    background: linear-gradient(to right, #f0fdf4, #ecfeff);
}

/* Buttons everywhere */
[data-baseweb="button"] {
    background-color: #16a34a !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    padding: 10px 16px !important;
    transition: all 0.2s ease-in-out;
}
[data-baseweb="button"]:hover {
    background-color: #15803d !important;
    transform: scale(1.03);
}

/* Custom code box */
.code-box {
    background:#0f172a;
    color:#e5e7eb;
    padding:16px;
    border-radius:12px;
    font-family: monospace;
    font-size:15px;
    font-weight:bold;
    overflow-x:auto;
}

/* AI answer box */
.answer-box {
    background:#f0fdf4;
    padding:18px;
    border-radius:16px;
    border-left:6px solid #22c55e;
    font-size:16px;
}

/* Custom tab buttons */
.tab-button {
    background-color: #bbf7d0;
    color: #065f46;
    padding: 10px 20px;
    border-radius: 12px;
    font-weight: bold;
    border: none;
    cursor: pointer;
    margin-right: 4px;
    transition: all 0.2s;
}
.tab-button:hover {
    background-color: #86efac;
}
.tab-button.active {
    background-color: #22c55e;
    color: white;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# =========================
# Session State
# =========================
for key, default in {
    "analyzed_code": "",
    "ai_call_count": 0,
    "chat_history": [],
    "active_chat": None,
    "ai_suggestions": [],
    "active_tab": "Code Analysis"
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
    <div style="
        background-color:#dcfce7;
        padding:14px;
        border-radius:14px;
        border:1px solid #22c55e;
    ">
        <b>✔ Features</b>
        <ul>
            <li>Syntax Validation</li>
            <li>Error Detection</li>
            <li>PEP8 Formatting</li>
            <li>AI Review</li>
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
    st.image("logo.png", width=120)
    st.title("AI Code Reviewer")
    st.caption("Analyze • Improve • Learn")

with col2:
    st.metric("AI Reviews Generated", st.session_state.ai_call_count)

st.divider()

# =========================
# Custom Tab Buttons
# =========================
tab_cols = st.columns([1,1])
with tab_cols[0]:
    if st.button("🧪 Code Analysis", key="tab1"):
        st.session_state.active_tab = "Code Analysis"
with tab_cols[1]:
    if st.button("🤖 AI Chat & Suggestions", key="tab2"):
        st.session_state.active_tab = "AI Chat & Suggestions"

st.divider()

# =========================
# TAB LOGIC
# =========================
if st.session_state.active_tab == "Code Analysis":
    # -------- Code Input --------
    code = st.text_area(
        "Paste Python code",
        height=300,
        value=st.session_state.analyzed_code,
        placeholder="def hello():\n    print('Hello World')"
    )

    if st.button("🚀 Analyze Code", use_container_width=True, key="analyze_code"):
        if not code.strip():
            st.warning("Please enter code before analyzing!")
            st.stop()

        st.session_state.analyzed_code = code
        st.session_state.chat_history = []
        st.session_state.ai_call_count = 0

        # Parse code
        result = parse_code(code)
        if not result["success"]:
            st.error(result["error"]["message"])
            st.stop()
        st.success("✅ Code parsed successfully")

        # Detect errors
        err = detect_errors(code)
        if err["error_count"] > 0:
            for e in err["errors"]:
                st.error(e["message"])
        else:
            st.success("No static errors found")

        # PEP8 / formatting
        try:
            style = show_style_corrected(code)
            if style["success"]:
                with st.expander("Formatted Code"):
                    st.code(style["corrected_code"], language="python")
        except:
            pass

        # AI suggestion only after code is analyzed
        with st.spinner("Generating AI suggestion..."):
            s = get_ai_suggestions(code, st.session_state.ai_call_count)
            s["message"] = format_ai_output(s["message"])
            st.session_state.ai_suggestions.append(s)
            st.session_state.ai_call_count += 1

elif st.session_state.active_tab == "AI Chat & Suggestions":
    # -------- AI Chat --------
    if not st.session_state.analyzed_code:
        st.info("Please analyze code first in 🧪 Code Analysis tab to get AI suggestions.")
    else:
        left, right = st.columns([2,5])
        # LEFT: History
        with left:
            st.markdown("### 💬 Questions")
            for i, chat in enumerate(st.session_state.chat_history):
                if st.button(chat["question"], key=f"q{i}", use_container_width=True):
                    st.session_state.active_chat = i
            st.divider()
            if st.button("➕ More Suggestions", use_container_width=True):
                with st.spinner("AI thinking..."):
                    prompt = f"Review the Python code and provide feedback:\n{st.session_state.analyzed_code}"
                    r = get_ai_suggestions(prompt, st.session_state.ai_call_count)
                    r["message"] = format_ai_output(r["message"])
                    st.session_state.chat_history.append({
                        "question": "General Code Review",
                        "answer": r["message"]
                    })
                    st.session_state.ai_call_count += 1
                    st.session_state.active_chat = len(st.session_state.chat_history) -1
                    st.rerun()
        # RIGHT: Chat Answer
        with right:
            st.markdown("### 🤖 AI Response")
            question = st.text_input("Ask anything about your code")
            if st.button("Ask AI", key="ask_ai"):
                if not st.session_state.analyzed_code:
                    st.warning("Please analyze code first!")
                    st.stop()
                with st.spinner("Thinking..."):
                    prompt = f"""
You are an expert Python assistant.

RULES:
1. If user asks for CODE → return ONLY code.
2. If user asks to EXPLAIN → explain clearly (line by line if needed).
3. If user asks to REVIEW / IMPROVE → use:
   Code Readability, Performance, Best Practices.
4. Do not add unnecessary sections.

Code Context:
{st.session_state.analyzed_code}

User Question:
{question}
"""
                    r = get_ai_suggestions(prompt, st.session_state.ai_call_count)
                    r["message"] = format_ai_output(r["message"])
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": r["message"]
                    })
                    st.session_state.ai_call_count += 1
                    st.session_state.active_chat = len(st.session_state.chat_history)-1
                    st.rerun()

            # Display selected answer safely
            if (st.session_state.active_chat is not None and
                st.session_state.chat_history and
                st.session_state.active_chat < len(st.session_state.chat_history)):

                ans = st.session_state.chat_history[st.session_state.active_chat]["answer"]
                if "```" in ans or "def " in ans:
                    st.markdown(f"<div class='code-box'>{ans}</div>", unsafe_allow_html=True)
                else:
                    formatted = format_ai_output(ans)
                    st.markdown(f"<div class='answer-box'>{formatted}</div>", unsafe_allow_html=True)
            else:
                st.info("No AI answer yet. Ask a question or generate suggestions.")
