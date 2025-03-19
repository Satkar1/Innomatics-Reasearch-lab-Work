import os
import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# -------------------- Load API Key --------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# -------------------- Initialize Gemini Model --------------------
llm = ChatGoogleGenerativeAI(
    google_api_key=api_key,
    model="gemini-2.0-flash-exp",
    temperature=0.2
)

# -------------------- Memory Setup --------------------
memory = ConversationBufferMemory(return_messages=True)

# -------------------- Streamlit Page Config --------------------
st.set_page_config(page_title="Data Science AI Tutor", page_icon="🤖", layout="centered")

# Custom CSS for styling
def apply_custom_css():
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(to right, #1e3c72, #2a5298);
            color: white;
            font-family: 'Arial', sans-serif;
        }
        .stTextInput > div > div > input {
            border-radius: 20px;
            padding: 10px;
            border: 1px solid #ccc;
        }
        .stButton > button {
            background: linear-gradient(to right, #ff512f, #dd2476);
            color: white;
            border-radius: 20px;
            padding: 10px 20px;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background: linear-gradient(to right, #dd2476, #ff512f);
            box-shadow: 0px 0px 10px rgba(255, 81, 47, 0.6);
        }
        .chat-container {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 5px 0;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
        }
        .user-message {
            background-color: rgba(255, 255, 255, 0.3);
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        .ai-message {
            background-color: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_css()

st.title("🧠 AI Data Science Conversational Tutor")
st.markdown("Ask any Data Science-related question! Type `exit` or press **End Chat** button to stop.")

# -------------------- Session State for Chat --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------- Helper Function: Standardize User Query --------------------
def standardize_query(query):
    return f"""
    You are an advanced AI Data Science Tutor with deep expertise in AI, ML, and Data Science.
    Answer concisely and clearly while avoiding unrelated topics.
    User's Question: '{query}'
    """

# -------------------- Chat Form (User Input) --------------------
with st.container():
    chat_box = st.container()

    with st.form("chat_form", clear_on_submit=True):
        user_query = st.text_input("You: ", placeholder="Ask your Data Science question here...", key="input")
        submitted = st.form_submit_button("Send")

# -------------------- Handling User Query --------------------
if submitted and user_query.strip() != "":
    if user_query.lower() in ["exit", "end", "quit", "bye"]:
        st.success("✅ Chat Ended. Thanks for using the AI Tutor!")
        st.session_state.chat_history = []
        memory.clear()
    else:
        formatted_query = standardize_query(user_query)
        memory.chat_memory.add_user_message(formatted_query)
        response = llm.invoke([
            *memory.chat_memory.messages,
            HumanMessage(content=formatted_query)
        ])
        memory.chat_memory.add_ai_message(response.content)
        st.session_state.chat_history.append(("You", user_query))
        st.session_state.chat_history.append(("AI", response.content.strip()))

# -------------------- Display Chat History with Auto Scroll --------------------
with chat_box:
    st.markdown("### 💬 Conversation History")
    chat_container = st.container()
    with chat_container:
        for sender, message in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f'<div class="user-message">{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-message">{message}</div>', unsafe_allow_html=True)
    st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

# -------------------- End Chat Button --------------------
if st.button("🚪 End Chat"):
    st.success("✅ Chat Ended. Thanks for using the AI Tutor!")
    st.session_state.chat_history = []
    memory.clear()
