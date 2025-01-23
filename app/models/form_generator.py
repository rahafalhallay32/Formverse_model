import openai
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_form(goal: str, group_type: str):
    prompt = f"Create a research form with questions for the goal: '{goal}' and target group: '{group_type}'."
    
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].text.strip().split("\n")
    except Exception as e:
        return {"error": str(e)}
