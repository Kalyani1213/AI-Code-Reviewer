import streamlit as st
import time
from code_parser import parse_code
from style_checker import show_style_corrected
from error_detector import detect_errors
from ai_suggester import get_ai_suggestions

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="😇",
    layout="wide",
)

# =========================
# Session State
# =========================
if "ai_suggestions" not in st.session_state:
    st.session_state.ai_suggestions = []

if "analyzed_code" not in st.session_state:
    st.session_state.analyzed_code = ""

if "ai_call_count" not in st.session_state:
    st.session_state.ai_call_count = 0

# =========================
# Helpers
# =========================
def refresh_app():
    st.session_state.analyzed_code = ""
    st.session_state.ai_suggestions = []
    st.session_state.ai_call_count = 0
    st.rerun()  # updated from experimental_rerun

# =========================
# Sidebar Styling
# =========================
sidebar_css = """
<style>
[data-testid="stSidebar"] {
    background-color: #f0f4f8;
    border-right: 2px solid #3b82f6;
}
[data-testid="stSidebar"] h2 {
    color: #1e40af;
    font-weight: bold;
}
[data-baseweb="button"] {
    background-color: #3b82f6 !important;
    color: white !important;
    border-radius: 12px;
    padding: 8px 16px;
    font-weight: bold;
}
[data-baseweb="button"]:hover {
    background-color: #2563eb !important;
}
</style>
"""
st.markdown(sidebar_css, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧠 AI Code Reviewer", unsafe_allow_html=True)
    st.markdown("##### Smart Python Code Analysis", unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    <div style='
        background-color: #e0f2fe;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #3b82f6;
    '>
        <h4 style='color:#1e40af;'>Features:</h4>
        <ul style='margin-left: 20px;'>
            <li>Syntax validation</li>
            <li>Error detection</li>
            <li>PEP8 formatting</li>
            <li>AI review</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.button("🔄 Reset Application", use_container_width=True, on_click=refresh_app)

# =========================
# Header
# =========================
header_left, header_right = st.columns([6, 2])

with header_left:
    st.image("logo.png", width=140)
    st.title("AI Code Reviewer")
    st.caption("Analyze • Improve • Learn")

with header_right:
    st.metric("AI Reviews", st.session_state.ai_call_count)
    st.button("🧹 Clear All", use_container_width=True, on_click=refresh_app)

st.divider()

# =========================
# Tabs
# =========================
tab1, tab2 = st.tabs(["🧪 Code Analysis", "🤖 AI Suggestions"])

# =========================
# TAB 1 — ANALYSIS
# =========================
with tab1:
    st.markdown("### 🧪 Code Input")

    code = st.text_area(
        label="Paste your Python code",
        height=280,
        value=st.session_state.analyzed_code,
        placeholder="def hello():\n    print('Hello World')",
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        analyze_clicked = st.button(
            "🚀 Analyze Code",
            type="primary",
            use_container_width=True
        )

    with col2:
        st.button("🧹 Clear", use_container_width=True, on_click=refresh_app)

    if analyze_clicked:
        if not code.strip():
            st.warning("Please enter some code.")
            st.stop()

        st.session_state.analyzed_code = code
        st.session_state.ai_suggestions = []
        st.session_state.ai_call_count = 0

        # -------- Parse --------
        parse_result = parse_code(code)
        if not parse_result["success"]:
            st.error("❌ Syntax Error")
            st.code(parse_result["error"]["message"])
            st.stop()
        st.success("✅ Code parsed successfully")

        # -------- Error Detection --------
        st.markdown("### 🐞 Error Detection")
        error_result = detect_errors(code)
        if error_result["error_count"] == 0:
            st.success("No static errors found 🎉")
        else:
            for error in error_result["errors"]:
                with st.expander(f"⚠️ {error['type']}", expanded=True):
                    st.write(error["message"])
                    st.info(error["suggestion"])

        # -------- Style Correction --------
        st.markdown("### 🎨 PEP8 Formatting")
        try:
            style_result = show_style_corrected(code)
            if style_result["success"]:
                with st.expander("View formatted code"):
                    st.code(style_result["corrected_code"], language="python")
        except Exception:
            st.info("Style checker not available")

        # -------- AI Suggestions --------
        with st.spinner("🤖 Generating AI suggestions..."):
            suggestion = get_ai_suggestions(
                code,
                variation=st.session_state.ai_call_count,
            )
            st.session_state.ai_suggestions.append(suggestion)
            st.session_state.ai_call_count += 1

# =========================
# TAB 2 — AI SUGGESTIONS
# =========================
with tab2:
    st.markdown("### 🤖 AI Code Review")

    if not st.session_state.ai_suggestions:
        st.info("Run **Analyze Code** to receive AI feedback.")
    else:
        for idx, suggestion in enumerate(st.session_state.ai_suggestions, start=1):
            if isinstance(suggestion, dict) and suggestion.get("type") == "AISuggestion":
                message_html = suggestion["message"].replace("\n", "<br>")
                st.markdown(f"""
                <div style='
                    background-color: #fef9c3;
                    padding: 12px;
                    border-radius: 12px;
                    border: 1px solid #facc15;
                    margin-bottom: 12px;
                '>
                    <strong>Suggestion #{idx}:</strong><br>
                    {message_html}
                </div>
                """, unsafe_allow_html=True)
            elif isinstance(suggestion, dict) and suggestion.get("type") == "Error":
                st.error(suggestion.get("message", "Unknown AI error"))
            else:
                st.error("Invalid AI response format")

        st.divider()

        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption("Request additional independent AI reviews")

        with col2:
            if st.button("➕ More Suggestions", use_container_width=True):
                if st.session_state.analyzed_code.strip():
                    with st.spinner("🤖 Thinking..."):
                        new_suggestion = get_ai_suggestions(
                            st.session_state.analyzed_code,
                            variation=st.session_state.ai_call_count
                        )
                        st.session_state.ai_suggestions.append(new_suggestion)
                        st.session_state.ai_call_count += 1
                        st.rerun()  # ✅ corrected
