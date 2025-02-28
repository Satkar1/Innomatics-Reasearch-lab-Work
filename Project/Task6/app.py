import streamlit as st
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ API Key is missing! Please check your .env file.")

# Initialize LangChain model with API key
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=API_KEY)

# Travel booking URLs
BOOKING_URLS = {
    "Air India": "https://www.airindia.com/",
    "Delta": "https://www.delta.com/",
    "Emirates": "https://www.emirates.com/",
    "Uber": "https://www.uber.com/global/en/price-estimate/",
    "RedBus": "https://www.redbus.in/",
    "IRCTC": "https://www.irctc.co.in/",
}

# Function to get booking URL (fallback to Google search)
def get_booking_url(provider):
    return BOOKING_URLS.get(provider, f"https://www.google.com/search?q={provider}+booking")

# Streamlit page setup
st.set_page_config(page_title="PathPlanner-AI", layout="wide", page_icon="🌍")

# Custom styles for better UI
st.markdown("""
    <style>
        body { background-color: #121212; color: white; }
        .stApp { background-color: #1e1e1e; }
        .stButton > button { background-color: #ff4c4c !important; color: white !important; 
            border-radius: 10px; font-weight: bold; padding: 10px 20px; transition: 0.3s; }
        .stButton > button:hover { background-color: #e63946 !important; }
        .travel-card { background: #222; padding: 15px; border-radius: 10px; 
            margin-bottom: 15px; box-shadow: 2px 2px 10px rgba(255, 255, 255, 0.1); transition: 0.3s; }
        .travel-card:hover { transform: scale(1.03); }
        .book-btn { background-color: #1db954; padding: 8px 15px; color: white; 
            font-weight: bold; text-decoration: none; border-radius: 8px; display: inline-block; }
        .book-btn:hover { background-color: #1aa34a; }
    </style>
""", unsafe_allow_html=True)

# Sidebar for preferences
with st.sidebar:
    st.markdown("## 🌍 Travel Preferences")
    preference = st.selectbox("Choose Preference", ["Cheapest", "Fastest", "Comfortable", "Eco-friendly"])
    sort_by = st.selectbox("Sort By", ["Default", "Lowest Price", "Shortest Duration"])

# App header
st.markdown("<h1 style='text-align: center; color: #ff4c4c;'>PathPlanner-AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Find the best travel options with AI!</h3>", unsafe_allow_html=True)

# Input section
col1, col2 = st.columns(2)
with col1:
    source = st.text_input("Source Location", placeholder="Enter starting point")
with col2:
    destination = st.text_input("Destination", placeholder="Enter destination")

# Button to fetch travel options
if st.button("🔍 Find Travel Options"):
    if source and destination:
        st.markdown(f"<h2 style='color: #1db954;'>🛫 Travel Options from {source} to {destination}</h2>", unsafe_allow_html=True)
        with st.spinner("Finding the best travel options..."):
            # Call Gemini API
            response = llm.invoke(f"Suggest travel options from {source} to {destination}, preference: {preference}. Return in JSON format.")
            response_content = response.content
            try:
                travel_data = json.loads(response_content.strip("```json").strip("```"))
                st.session_state.response = travel_data
            except json.JSONDecodeError:
                st.error("⚠️ AI response format error. Please try again.")

# Display travel options dynamically
if "response" in st.session_state:
    travel_data = st.session_state.response

    def show_travel_options(title, key, icon):
        st.markdown(f"<h3 style='color: #1db954;'>{icon} {title}</h3>", unsafe_allow_html=True)
        for item in travel_data.get(key, []):
            provider = item["provider"]
            price = item["price"]
            duration = item["duration"]
            notes = item["notes"]
            description = item.get("description", "No description available.")
            booking_url = item.get("booking_url", "")

            travel_card = f"""
                <div class="travel-card">
                    <h4>{provider}</h4>
                    <p>💰 <strong>Price:</strong> {price}</p>
                    <p>⏳ <strong>Duration:</strong> {duration}</p>
                    <p>📌 <strong>Notes:</strong> {notes}</p>
                    <p>ℹ️ <strong>Description:</strong> {description}</p>
                    <a href="{booking_url}" target="_blank" class="book-btn">Book Now</a>
                </div>
            """
            st.markdown(travel_card, unsafe_allow_html=True)

    show_travel_options("Flights", "flights", "✈️")
    show_travel_options("Trains", "trains", "🚆")
    show_travel_options("Buses", "buses", "🚌")
    show_travel_options("Cabs", "cabs", "🚖")
