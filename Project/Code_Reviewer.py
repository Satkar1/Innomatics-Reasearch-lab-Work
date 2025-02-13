import streamlit as st
import google.generativeai as ai
import time
import base64
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from streamlit.components.v1 import html

# Configure API Key (Replace with your actual key)
ai.configure(api_key="AIzaSyCi5NabZBjwVyHld_knc4WhhjoNFCbzfPI")

# AI System Prompt
sys_prompt = """You are an AI Code Reviewer.
Your job is to analyze the provided Python code, detect bugs, and suggest optimized solutions.
You should return:
1. A detailed bug report explaining issues in the code.
2. A fixed and optimized version of the code.
Ensure responses are clear, well-structured, and maintain best coding practices."""

# Load Gemini-2 Flash Model
gemini_model = ai.GenerativeModel(model_name="gemini-2.0-flash-exp", system_instruction=sys_prompt)

# Custom CSS for Styling & Animations
st.markdown("""
    <style>
        body { background-color: #0e1117; color: white; font-family: 'Arial', sans-serif; }
        .stTextArea textarea { background-color: rgba(30, 30, 30, 0.8); color: #00d4ff; font-size: 16px; border-radius: 10px; box-shadow: 0 0 10px #00d4ff; }
        .stButton > button { border-radius: 10px; background: linear-gradient(90deg, #ff8c00, #ff2d55); color: white; font-weight: bold; box-shadow: 0 4px 15px rgba(255, 140, 0, 0.6); transition: 0.3s; }
        .stButton > button:hover { transform: scale(1.05); box-shadow: 0 6px 20px rgba(255, 45, 85, 0.8); }
        .glow-text { font-size: 28px; color: #ffdd57; text-shadow: 0 0 10px #ffdd57, 0 0 20px #ffdd57; font-weight: bold; text-align: center; }
        .fade-in { animation: fadeIn 1.5s ease-in-out; }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .ai-avatar {
            position: absolute;
            right: 20px;
            top: 10px;
            width: 80px;
            height: 80px;
            background: url('https://i.imgur.com/EOjZ3Y2.png');
            background-size: cover;
            border-radius: 50%;
            box-shadow: 0 0 10px #ff2d55;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='glow-text'>🤖 AI Code Reviewer ⚒️</h1>", unsafe_allow_html=True)
st.markdown("**🔍 This AI Code Reviewer analyzes your code, detects bugs, suggests fixes, and applies modifications dynamically.**")
st.markdown("<div class='ai-avatar'></div>", unsafe_allow_html=True)

# User input fields
code_input = st.text_area("📜 Enter your Python code:", placeholder="Paste your Python code here...", height=200)
query_input = st.text_area("🔧 Enter your query (if any):", placeholder="E.g., Optimize for performance or fix security issues...", height=100)

# Function to apply syntax highlighting
def format_code(code):
    return highlight(code, PythonLexer(), HtmlFormatter(style="monokai", full=True))

# Function to download fixed code
def get_download_link(text, filename="fixed_code.py"):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download Fixed Code</a>'

# Analyze button
if st.button("🚀 Analyze Code"):
    if code_input.strip():
        with st.spinner("Analyzing your code... Please wait."):
            time.sleep(2)  # Simulate processing time
            prompt = f"Code:\n```{code_input}```\n\nQuery: {query_input if query_input.strip() else 'Review and optimize the code.'}"
            response = gemini_model.generate_content(prompt)
            
            if hasattr(response, "text"):
                st.subheader("📝 Bug Report & Fixes:")
                st.write(response.text)
                
                # Extract fixed code from AI response
                fixed_code = response.text.split("```python\n")[-1].split("```", 1)[0]
                
                if fixed_code:
                    st.subheader("✅ Optimized Code:")
                    formatted_code = format_code(fixed_code)
                    html(f'<div class="fade-in" style="border-radius:10px; padding:10px; background:#282c34">{formatted_code}</div>', height=300)
                    st.markdown(get_download_link(fixed_code), unsafe_allow_html=True)
            else:
                st.error("❌ Error: No response received. Please try again.")
    else:
        st.warning("⚠️ Please enter code before clicking the button.")
