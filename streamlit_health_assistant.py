import streamlit as st
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is not set in the .env file.")
    st.stop()

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Load JSON data
def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

personalized_health_plan = load_json("personalized_health_plan.json")
risk_data = load_json("risk_data.json")
user_profile = load_json("user_profile.json")

# Combine general health context
general_context = {
    "personalized_health_plan": personalized_health_plan,
    "risk_data": risk_data,
    "user_profile": user_profile
}

# Call Gemini API
def ask_gemini(question, context):
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"You are a supportive health assistant. Based on the following data: "
                    f"{json.dumps(context)}\n\n"
                    f"Respond concisely and gently.\n"
                    f"Question: {question}"
                )
            }]
        }]
    }
    params = {"key": GEMINI_API_KEY}

    response = requests.post(GEMINI_API_URL, headers=headers, json=payload, params=params)
    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, json.JSONDecodeError):
            return "Sorry, I couldn't process the response."
    else:
        return f"Gemini API error: {response.status_code} - {response.text}"

# Emotion-specific analysis
def analyze_feeling(feeling):
    feeling = feeling.strip().lower()
    context = {
        "user_profile": user_profile,
        "recent_sleep_hours": user_profile.get("sleep_hours", 6),
        "recent_steps": user_profile.get("daily_steps", 5000)
    }

    prompt = (
        f"The user said they feel '{feeling}'. Using the health and lifestyle data provided, suggest one helpful reason or insight, "
        f"and provide a supportive action. Be kind, empathetic, and concise."
    )

    return ask_gemini(prompt, context)

# Streamlit UI
st.title("Health Assistant Chat")
st.write("Welcome to your personalized health assistant. You can ask questions about your health plan, risk data, or share how you're feeling.")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display introductory message if chat history is empty
if not st.session_state.chat_history:
    st.session_state.chat_history.append({"role": "assistant", "message": "How are you feeling today?"})

# Display chat history in a chatbot-like format
st.subheader("Chat")
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        with st.chat_message("user"):
            st.write(chat["message"])
    elif chat["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(chat["message"])

# Single text input for both initial check-in and general Q&A
if user_input := st.chat_input("Type your message here..."):
    if len(st.session_state.chat_history) == 1:  # Initial feeling check-in
        response = analyze_feeling(user_input)
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        st.session_state.chat_history.append({"role": "assistant", "message": response})
    else:  # General Q&A
        response = ask_gemini(user_input, general_context)
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        st.session_state.chat_history.append({"role": "assistant", "message": response})
    st.experimental_rerun()