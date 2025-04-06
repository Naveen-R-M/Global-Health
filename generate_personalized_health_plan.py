from imports import *

# Load environment variables from .env file
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the .env file
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")

# Define the correct Gemini API endpoint and model
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"  # Correct Gemini API endpoint
GEMINI_MODEL = "gemini-2.0-flash" # Model name

# Load data from JSON files
def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

generic_health_plan = load_json("generic_health_plan.json")
risk_data = load_json("risk_data.json")
user_profile = load_json("user_profile.json")

# Combine data into a single payload
combined_data = {
    "user_profile": user_profile,
    "risk_data": risk_data,
    "generic_health_plan": generic_health_plan
}

def get_payloads(choice, data):
    if choice == 1:
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Generate a personalized health plan based on the following data: {json.dumps(data)}. Give only the contents, and not extra wordings. Please don't include the user profile in the result. And how is it different from the generic health plan? Give the content concise, as I'm going to display it in the home page for the user's app."
                }]
            }]
        }
    else:
        payload = {
        "contents": [{
            "parts": [{
                "text": f"Give the data {data} in a proper JSON format (python dictionary)"
            }]
        }]
    }
    return payload

# Function to generate a personalized health plan using the Gemini API
def generate_personalized_health_plan(payload):
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=payload, params=params)

    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"Gemini API error: {response.status_code} - {response.text}")

# Generate and save the personalized health plan
try:
    personalized_plan = generate_personalized_health_plan(get_payloads(1, combined_data))
    print(personalized_plan)
    personalized_plan = generate_personalized_health_plan(get_payloads(2, personalized_plan))

    # Save the personalized plan to a JSON file
    with open("personalized_health_plan.json", "w") as file:
        json.dump({"personalized_plan": personalized_plan}, file, indent=4)
    print("Personalized health plan saved to personalized_health_plan.json")
except Exception as e:
    print(f"An error occurred: {e}")