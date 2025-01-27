import openai
from dotenv import load_dotenv
import os
from models.dto import SummarizeInput, SurveyResponse  # Importing the DTOs

# Load OpenAI API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_survey_responses(goal: str, hypothesis: str, target_group: str, time_taken: int, user_responses: list):
    """
    Generates a research summary, including individual user responses and a general summary based on researcher input and survey responses.

    Args:
        goal (str): The research goal.
        hypothesis (str): The research hypothesis.
        target_group (str): The target group for the research.
        time_taken (int): The estimated time to complete the research (in minutes).
        user_responses (list): List of survey responses to summarize.

    Returns:
        dict: A dictionary containing individual summaries and the general summary, or None if an error occurs.
    """

    # Create the prompt for summarizing each user response
    individual_summaries = []
    for response in user_responses:
        prompt = f"""
        You are an AI assistant that analyzes and summarizes survey responses. Below is a survey response from a user:

        Survey Response:
        {response}

        Based on this response, please provide a brief summary or key insights.
        """

        try:
            # Using openai.Chat.completions.create for the new API to summarize each user's response
            response_summary = openai.chat.completions.create(
                model="gpt-4",  # Using GPT-4 model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )

            # Collect the individual response summaries
            individual_summary = response_summary.choices[0].message.content.strip()
            individual_summaries.append(individual_summary)

        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            individual_summaries.append(f"Failed to summarize response: {response}")

    # Now summarize the general trends across all responses
    general_prompt = f"""
    You are an AI assistant that analyzes and summarizes survey responses. Below are the research details and the responses from multiple users.

    Researcher Inputs:
        - Goal: {goal}
        - Hypothesis: {hypothesis}
        - Target Group: {target_group}
        - Time Taken (in minutes): {time_taken}

    Survey Responses:
    {', '.join(user_responses)}

    Based on the provided survey responses and the research inputs, please summarize the main trends, common themes, or insights. 
    If applicable, also highlight any significant differences between users.
    """

    try:
        # Using openai.Chat.completions.create for the general summary
        general_summary_response = openai.chat.completions.create(
            model="gpt-4",  # Using GPT-4 model
            messages=[{"role": "user", "content": general_prompt}],
            max_tokens=700,
            temperature=0.7
        )

        # Get the general summary
        general_summary = general_summary_response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        general_summary = "Failed to generate general summary."

    return {
        "individual_summaries": individual_summaries,
        "general_summary": general_summary
    }
