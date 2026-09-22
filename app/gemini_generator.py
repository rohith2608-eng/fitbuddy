from google import genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODELS = ["gemini-3.6-flash", "gemini-3.6-flash-lite"]
MAX_RETRIES = 3

def generate_workout_gemini(user_input: dict):
    prompt = f"""
    You are a professional fitness trainer.

    Create a personalized, structured 7-day workout plan for someone with the goal of **{user_input['goal']}**, and prefers **{user_input['intensity']}** intensity workouts.

    Each day must include:
    - A warm-up (5-10 mins)
    - Main workout (targeted exercises, sets & reps)
    - Cooldown or recovery tip

    Format:
    Day 1:
    Warm-up: ...
    Main Workout: ...
    Cooldown: ...
    (Repeat for Day 2-7)
    """
    for model in MODELS:
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                if "503" in str(e) and attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** (attempt + 1))  # Wait 2s, 4s, 8s
                    continue
                elif "503" in str(e):
                    print(f"Model {model} unavailable, trying fallback...")
                    break  # Try next model
                else:
                    return f"Error: {e}"
    return "Error: All models are currently unavailable. Please try again later."
