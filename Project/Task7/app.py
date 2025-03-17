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
st.title("🧠 AI Data Science Conversational Tutor")
st.markdown("Ask any Data Science-related question! I'll remember everything until you end the chat. Type `exit` or press **End Chat** button to stop.")

# -------------------- Session State for Chat --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------- Helper Function: Standardize User Query --------------------
def standardize_query(query):
    return f"""
    You are an advanced AI Data Science Tutor with deep expertise in modern AI, Machine Learning, Data Science, and related technologies.
    Answer questions specifically focused on:
    - Core Data Science: Machine Learning, AI, Python, Statistics, Visualization, Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch.
    - Emerging tools & frameworks: LangChain, LLMOps, Vector Databases (e.g., Pinecone, ChromaDB), Prompt Engineering, RAG (Retrieval-Augmented Generation), Generative AI tools that assist Data Science workflows.
    
    You should avoid completely unrelated topics (like politics, sports, entertainment).

    Here is the user's question: '{query}'
    """


# -------------------- Chat Form (User Input) --------------------
with st.form("chat_form", clear_on_submit=True):
    user_query = st.text_input("You: ", placeholder="Ask your Data Science question here...", key="input")
    submitted = st.form_submit_button("Send")

# -------------------- Handling User Query --------------------
if submitted and user_query.strip() != "":
    if user_query.lower() in ["exit", "end", "quit", "bye"]:
        st.success("✅ Chat Ended. Thanks for using the AI Tutor!")
        # Clear memory and chat
        st.session_state.chat_history = []
        memory.clear()
    else:
        # STEP 2: Standard Template Formatting
        formatted_query = standardize_query(user_query)

        # STEP 3: Add user query to memory
        memory.chat_memory.add_user_message(formatted_query)

        # STEP 4: AI Response (with memory context)
        response = llm.invoke([
            *memory.chat_memory.messages,
            HumanMessage(content=formatted_query)
        ])

        # STEP 5: Add AI response to memory and chat history
        memory.chat_memory.add_ai_message(response.content)
        st.session_state.chat_history.append(("You", user_query))
        st.session_state.chat_history.append(("AI", response.content.strip()))

# -------------------- Display Chat History --------------------
st.markdown("---")
st.subheader("💬 Conversation History")

for sender, message in st.session_state.chat_history:
    with st.chat_message(sender):
        st.markdown(message)

# -------------------- End Chat Button --------------------
if st.button("🚪 End Chat"):
    st.success("✅ Chat Ended. Thanks for using the AI Tutor!")
    # Clear memory and chat
    st.session_state.chat_history = []
    memory.clear()
  
