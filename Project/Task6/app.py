import streamlit as st
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import json
from geopy.geocoders import Nominatim
from gtts import gTTS
import base64
import tempfile
from langchain.schema.runnable import RunnablePassthrough

# Load environment variables
load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Initialize AI model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

# Define travel booking URLs
BOOKING_URLS = {
    "Air India": "https://www.airindia.com/",
    "Delta": "https://www.delta.com/",
    "Emirates": "https://www.emirates.com/",
    "Uber": "https://www.uber.com/global/en/price-estimate/",
    "RedBus": "https://www.redbus.in/",
    "IRCTC": "https://www.irctc.co.in/",
}

# Get booking URL or fallback to Google search
def get_booking_url(provider):
    return BOOKING_URLS.get(provider, f"https://www.google.com/search?q={provider}+booking")

# Define travel AI prompt template
prompt_template = PromptTemplate(
    input_variables=["source", "destination", "preference"],
    template="""
    You are an AI travel assistant. A user wants to travel from {source} to {destination} 
    with a preference for {preference}. Provide travel options for cab, train, bus, and flight. 
    Return the response strictly in **valid JSON format**, without any extra text or explanations.
    """
)

# Define travel AI chain
chain = {
    "source": RunnablePassthrough(),
    "destination": RunnablePassthrough(),
    "preference": RunnablePassthrough()
} | prompt_template | llm

# Streamlit UI setup
st.set_page_config(page_title="PathPlanner-AI", layout="wide", page_icon="🧭")

# Apply custom styling
st.markdown("""
    <style>
        body {
            background-color: #121212;
            color: white;
        }
        .stApp {
            background-color: #1e1e1e;
        }
        .stTextInput, .stSelectbox {
            background-color: #333 !important;
            color: white !important;
            border-radius: 8px;
        }
        .stButton > button {
            background-color: #ff4c4c !important;
            color: white !important;
            border-radius: 10px;
            font-weight: bold;
            padding: 10px 20px;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background-color: #e63946 !important;
        }
        .travel-card {
            background: #222;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 2px 2px 10px rgba(255, 255, 255, 0.1);
            transition: 0.3s;
        }
        .travel-card:hover {
            transform: scale(1.03);
        }
        .book-btn {
            background-color: #1db954;
            padding: 8px 15px;
            color: white;
            font-weight: bold;
            text-decoration: none;
            border-radius: 8px;
            display: inline-block;
        }
        .book-btn:hover {
            background-color: #1aa34a;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for filters
with st.sidebar:
    st.markdown("## 🌍 Travel Preferences")
    preference = st.selectbox("Choose Preference", ["Cheapest", "Fastest", "Comfortable", "Eco-friendly"])
    sort_by = st.selectbox("Sort By", ["Default", "Lowest Price", "Shortest Duration"])

# Main UI
st.markdown("<h1 style='text-align: center; color: #ff4c4c;'>PathPlanner-AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Find the best travel options with AI!</h3>", unsafe_allow_html=True)

# Input section
col1, col2 = st.columns(2)
with col1:
    source = st.text_input("Source Location", placeholder="Enter starting point")
with col2:
    destination = st.text_input("Destination", placeholder="Enter destination")

# Search button
if st.button("🔍 Find Travel Options"):
    if source and destination:
        st.markdown(f"<h2 style='color: #1db954;'>🛫 Travel Options from {source} to {destination}</h2>", unsafe_allow_html=True)
        with st.spinner("Finding the best travel options..."):
            response = chain.invoke({"source": source, "destination": destination, "preference": preference})
            response_content = response.content
            try:
                travel_data = json.loads(response_content.strip("```json").strip("```"))
                st.session_state.response = travel_data
            except json.JSONDecodeError:
                st.error("AI response format error.")

# Display travel options
if "response" in st.session_state:
    travel_data = st.session_state.response

    def display_travel_options(title, key, icon):
        st.markdown(f"<h3 style='color: #1db954;'>{icon} {title}</h3>", unsafe_allow_html=True)
        for item in travel_data.get(key, []):
            provider = item["provider"]
            price = item["price"]
            duration = item["duration"]
            notes = item["notes"]
            description = item.get("description", "No description available.")
            booking_url = item.get("booking_url", "")

            card_html = f"""
                <div class="travel-card">
                    <h4>{provider}</h4>
                    <p>💰 <strong>Price:</strong> {price}</p>
                    <p>⏳ <strong>Duration:</strong> {duration}</p>
                    <p>📌 <strong>Notes:</strong> {notes}</p>
                    <p>ℹ️ <strong>Description:</strong> {description}</p>
                    <a href="{booking_url}" target="_blank" class="book-btn">Book Now</a>
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    display_travel_options("Flights", "flights", "✈️")
    display_travel_options("Trains", "trains", "🚆")
    display_travel_options("Buses", "buses", "🚌")
    display_travel_options("Cabs", "cabs", "🚖")
