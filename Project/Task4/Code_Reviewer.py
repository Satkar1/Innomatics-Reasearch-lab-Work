import streamlit as st
import google.generativeai as ai
import base64
from streamlit.components.v1 import html
f = open("keys/.gemini.txt")

key = f.read()

ai.configure(api_key=key)
# System Prompt

sys_prompt = """You are an AI Code Reviewer.
Your job is to analyze the provided Python code, detect bugs, and suggest optimized solutions.
You should return:
1. A detailed bug report explaining issues in the code.
2. A fixed and optimized version of the code.
Ensure responses are clear, well-structured, and maintain best coding practices."""

gemini_model = ai.GenerativeModel(model_name="gemini-2.0-flash-exp", system_instruction=sys_prompt)


# User input fields
code_input = st.text_area("📜 Enter your Python code:", placeholder="Paste your Python code here...", height=200)
query_input = st.text_area("🔧 Enter your query (if any):", placeholder="E.g., Optimize for performance or fix security issues...", height=100)

def format_code(code):
    return highlight(code, PythonLexer(), HtmlFormatter(style="monokai", full=True))

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
