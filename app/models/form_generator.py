import openai
from dotenv import load_dotenv
import os
import json

# Load OpenAI API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_researcher_input(goal: str, target_group: str, number_of_questions: int, hypothesis: str, time_taken: int):
    """
    Function to generate a research form using OpenAI's GPT-4 model based on researcher input.
    """

    # Create a structured prompt based on the input data
    prompt = f"""
    You are a professional research assistant. Based on the following inputs, generate a research form:
    Questions should either be **multiple choice** or **two options like yes or no** or **open-ended** depending on the format preference.

    Researcher Inputs:
    - Goal: {goal}
    - Hypothesis: {hypothesis}
    - Target Group: {target_group}
    - Time Taken (in minutes): {time_taken}

    Based on this information, generate a research form with:
    - Questions related to {goal} for {target_group}.
    - Ensure that the questions are clear and related to {hypothesis}.

    Return the research form in the following format:
    - Goal
    - Target Group
    - List of Questions (in JSON format with "question", "type" and "options" for MC questions)
    """

    # Send the prompt to OpenAI GPT-4 to generate the research form
    response = openai.Completion.create(
        engine="gpt-4",  # Using the latest GPT-4 model
        prompt=prompt,
        max_tokens=700,  # Increased max_tokens for more detailed responses
        temperature=0.7,
        n=1
    )

    # Parse the response from OpenAI (assuming the model returns a structured format)
    research_form = response.choices[0].text.strip()

    return research_form


def format_to_json(response):
    """
    Tries to format the generated research form response into a JSON format.
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("Error formatting response into JSON.")
        return {}

