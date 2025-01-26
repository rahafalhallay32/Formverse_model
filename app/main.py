from fastapi import FastAPI
from pydantic import BaseModel
from models.dto import ResearcherInput, SummarizeInput  # Importing DTOs from dto.py
from models.form_generator import analyze_researcher_input  # Importing form generation logic
from models.form_summarization import summarize_survey_responses  # Importing summarization logic
import uvicorn
import json

app = FastAPI()

# Endpoint for generating a research form based on researcher input
@app.post("/generate_research_form")
async def generate_research_form(researcher_input: ResearcherInput):
    """
    API endpoint to generate a research form based on researcher input.
    """
    # Extracting values from the validated ResearcherInput
    goal = researcher_input.goal
    hypothesis = researcher_input.hypothesis
    target_group = researcher_input.target_group
    time_taken = researcher_input.time_taken

    # Generate the research form using the provided researcher input
    research_form = analyze_researcher_input(goal, hypothesis, target_group, time_taken)

    if research_form:
        try:
            # Parse the research form string into a JSON object
            research_form_json = json.loads(research_form)
            return {"research_form": research_form_json} 
        except Exception as e:  # Catch any exception that occurs
            print(f"An error occurred: {e}")
            return {"error": f"An error occurred: {e}"}
    else:
        return {"error": "Failed to generate research form."}

# Endpoint for summarizing survey responses based on researcher input and responses
@app.post("/summarize_survey_responses")
async def summarize_survey_responses_endpoint(summarize_input: SummarizeInput):
    """
    API endpoint to summarize survey responses based on researcher input and responses.
    """
    goal = summarize_input.goal
    hypothesis = summarize_input.hypothesis
    target_group = summarize_input.target_group
    time_taken = summarize_input.time_taken
    user_responses = summarize_input.user_responses

    # Generate the survey response summary
    summary_result = summarize_survey_responses(goal, hypothesis, target_group, time_taken, user_responses)

    if summary_result:
        return {
            "individual_summaries": summary_result["individual_summaries"],
            "general_summary": summary_result["general_summary"]
        }
    else:
        return {"error": "Failed to summarize survey responses."}

# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
