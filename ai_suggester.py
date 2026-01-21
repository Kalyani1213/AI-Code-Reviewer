# ai_suggester.py
import os
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage

load_dotenv()

# -------------------------
# Setup HuggingFace LLM
# -------------------------
llm = HuggingFaceEndpoint(
    repo_id='HuggingFaceH4/zephyr-7b-beta',
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    temperature=0.3,
    max_new_tokens=500  # enough to get all 3 sections
)

model = ChatHuggingFace(llm=llm)

# -------------------------
# Function to get AI suggestions
# -------------------------
def get_ai_suggestions(code_string, variation=0):
    """
    Returns actionable AI suggestions for Python code with headings:
    Code Readability, Performance, Best Practices
    """
    prompt = f"""
Please review the following Python code and provide actionable suggestions under these three categories:

1. Code Readability:
   - Provide 2-3 concise and specific suggestions.
   - Include short examples if possible.

2. Performance:
   - Provide 2-3 concise and specific suggestions.
   - Include short examples if possible.

3. Best Practices:
   - Provide 2-3 concise and specific suggestions.
   - Include short examples if possible.

Important:
- Do not skip any category.
- Use clear headings for each category exactly as above.
- Use bullet points or numbers for suggestions.

Python code:
{code_string}
"""

    try:
        response = model.invoke([HumanMessage(content=prompt)])
        ai_message = response.content.strip()
        return {
            "type": "AISuggestion",
            "message": ai_message,
            "severity": "Info"
        }
    except Exception as e:
        return {
            "type": "Error",
            "message": f"❌ AI error: {str(e)}",
            "severity": "Error"
        }
