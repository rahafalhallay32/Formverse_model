from pydantic import BaseModel
import openai
from dotenv import load_dotenv
import os
from models.dto import ResearcherInput

# Load OpenAI API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


"""class ResearcherInput(BaseModel):
    goal: str
    hypothesis: str
    target_group: str
    time_taken: int"""


def analyze_researcher_input(goal: str, hypothesis: str, target_group: str, time_taken: int):
    """
    Generates a research form in JSON format using OpenAI's GPT-4 model based on researcher input.

    Args:
        goal (str): The research goal.
        hypothesis (str): The research hypothesis.
        target_group (str): The target group for the research.
        time_taken (int): The estimated time to complete the research (in minutes).

    Returns:
        str (or None): The generated research form in JSON format, or None if an error occurs.
    """

    prompt = f"""
    You are a professional research assistant. Based on the following researcher inputs, generate a research form in JSON format:

    **Researcher Inputs:**
    - Goal: {goal}
    - Hypothesis: {hypothesis}
    - Target Group: {target_group}
    - Time Taken (in minutes): {time_taken}

    **Research Form Requirements:**
    - Questions should be clear, concise, and relevant to the research goal and hypothesis.
    - Use a mix of question formats (multiple choice, open ended, yes/no) depending on the information being gathered.
    - The target audience is {target_group}.

    **Output Format:**
    The research form should be a JSON list of questions with the following structure for each question:
        - question (string): The text of the question.
        - type (string): The type of question (e.g., "Multiple Choice", "Open-Ended", "Yes/No").
        - options (list of strings, optional): Only applicable for multiple choice questions, containing the available options.

    **Example:**
    [
        {{
            "question": "What do you think is the most significant benefit of using AI in daily life?",
            "type": "Open-Ended"
        }},
        {{
            "question": "How do you think AI will impact your daily routine in the next 5 years?",
            "type": "Open-Ended"
        }},
        {{
            "question": "Do you think AI-powered virtual assistants will improve your daily productivity?",
            "type": "Multiple Choice",
            "options": ["Strongly Agree", "Agree", "Neutral", "Disagree"]
        }},
        {{
            "question": "What are the primary concerns you have about using AI in daily life?",
            "type": "Open-Ended"
        }},
        {{
            "question": "Would you prefer using AI-powered tools for tasks like data analysis and report generation?",
            "type": "Multiple Choice",
            "options": ["Yes", "No"]
        }}
    ]
    """

    try:
        # Using openai.Chat.completions.create for the new API
        response = openai.chat.completions.create(
            model="gpt-4",  # Using GPT-4 model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.7
        )

        # Get the research form content (JSON) and strip whitespace
        research_form = response.choices[0].message.content.strip()

        return research_form

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None