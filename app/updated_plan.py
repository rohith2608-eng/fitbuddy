from google import genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODELS = ["gemini-3.6-flash", "gemini-3.6-flash-lite"]
MAX_RETRIES = 3

def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    """
    Use Gemini to update the workout plan based on user feedback.
    """
    prompt = f"""
    You are a professional fitness trainer assistant.
    
    Here's the original 7-day workout plan:
    {original_plan}
    
    User Feedback:
    "{user_feedback}"
    
    Based on the feedback, revise the relevant parts of the workout plan. Keep the format and rest of the plan unchanged if not needed.
    """
    
    for model in MODELS:
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text.strip()
            except Exception as e:
                if "503" in str(e) and attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** (attempt + 1))  # Wait 2s, 4s, 8s
                    continue
                elif "503" in str(e):
                    print(f"Model {model} unavailable, trying fallback...")
                    break  # Try next model
                else:
                    return f"Error updating plan: {e}"
    return "Error: All models are currently unavailable. Please try again later."
