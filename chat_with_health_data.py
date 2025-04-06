from imports import *

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")

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

# Fallback emotional responses
fallback_emotion_responses = {
    "tired": "Tiredness can result from lack of sleep, stress, or even low hydration. Try a short rest, hydration, or a light walk if you can.",
    "stressed": "Stress is common. Deep breathing or a few minutes of mindfulness can make a big difference.",
    "happy": "That's great! Staying positive is good for overall health. Keep doing what works for you!",
    "anxious": "You're not alone. Talking to someone or a brief mindfulness break can help manage anxiety."
}

# Call Gemini API
def ask_gemini(question, context):
    headers = { "Content-Type": "application/json" }
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
    params = { "key": GEMINI_API_KEY }

    response = requests.post(GEMINI_API_URL, headers=headers, json=payload, params=params)
    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, json.JSONDecodeError):
            return None
    else:
        raise Exception(f"Gemini API error: {response.status_code} - {response.text}")

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

    try:
        ai_response = ask_gemini(prompt, context)
        if ai_response and "not sure" not in ai_response.lower():
            return ai_response
        else:
            return fallback_emotion_responses.get(feeling, "Thanks for sharing. Let's keep track of how you're feeling.")
    except Exception as e:
        return fallback_emotion_responses.get(feeling, f"Couldn't process right now. Here's something to try: deep breathing or light stretching.")

# Main chat function
def chat_with_health_assistant():
    print("Welcome to your Health Assistant Chat!\nType 'exit' anytime to leave.\n")

    # Initial feeling check-in
    try:
        feeling_input = input("Health Assistant: How are you feeling today? (e.g., tired, stressed, happy, etc.)\nYou: ")
        if feeling_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            return

        response = analyze_feeling(feeling_input)
        print(f"Health Assistant: {response}\n")
    except Exception as e:
        print(f"An error occurred during emotional check-in: {e}")

    # General health Q&A loop
    while True:
        user_question = input("You: ")
        if user_question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        try:
            response = ask_gemini(user_question, general_context)
            print(f"Health Assistant: {response}")
        except Exception as e:
            print(f"An error occurred: {e}")

# Entry point
if __name__ == "__main__":
    chat_with_health_assistant()
