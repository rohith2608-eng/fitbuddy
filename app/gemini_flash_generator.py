from google import genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODELS = ["gemini-3.6-flash", "gemini-3.6-flash-lite"]
MAX_RETRIES = 3

def generate_nutrition_tip_with_flash(goal: str) -> str:
    """
    Generate a nutrition or recovery tip using Gemini Flash based on the user's fitness goal.
    
    Args:
        goal (str): User's fitness goal - "weight loss", "muscle gain", or "general fitness".
        
    Returns:
        str: Generated tip.
    """
    prompt = (
        f"Give one clear, helpful nutrition or recovery tip for someone focused on '{goal}'. "
        "The tip should be practical, friendly, and easy to understand."
    )
    
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
                    return f"Error generating tip: {str(e)}"
    return "Error: All models are currently unavailable. Please try again later."
