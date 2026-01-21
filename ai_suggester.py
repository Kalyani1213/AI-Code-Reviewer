# ai_suggester.py
import streamlit as st  # <-- use Streamlit secrets
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage

# -------------------------
# Read HuggingFace API token from Streamlit secrets
# -------------------------
HF_TOKEN = st.secrets["HUGGINGFACEHUB_API_TOKEN"]

# -------------------------
# Setup HuggingFace LLM
# -------------------------
llm = HuggingFaceEndpoint(
    repo_id='HuggingFaceH4/zephyr-7b-beta',
    huggingfacehub_api_token=HF_TOKEN,  # use the secret
    temperature=0.3,
    max_new_tokens=800  # allow more tokens for AI Suggestions
)

model = ChatHuggingFace(llm=llm)

# -------------------------
# Function to get AI suggestions or answers
# -------------------------
def get_ai_suggestions(prompt_text, variation=0):
    """
    Returns AI response for a given prompt_text.
    Can be used for:
    - AI Suggestions
    - Improved Code
    - AI Chat
    """
    try:
        response = model.invoke([HumanMessage(content=prompt_text)])
        ai_message = response.content.strip()
        return {
            "type": "AIResponse",
            "message": ai_message,
            "severity": "Info"
        }
    except Exception as e:
        return {
            "type": "Error",
            "message": f"❌ AI error: {str(e)}",
            "severity": "Error"
        }
