from fastapi import FastAPI, Body
from pydantic import BaseModel
from models.form_generator import analyze_researcher_input, ResearcherInput
import uvicorn
import json

app = FastAPI()

@app.post("/generate_research_form")
async def generate_research_form(researcher_input: ResearcherInput):
  """
  API endpoint to generate a research form based on researcher input.
  """
  goal = researcher_input.goal
  hypothesis = researcher_input.hypothesis
  target_group = researcher_input.target_group
  time_taken = researcher_input.time_taken

  research_form = analyze_researcher_input(goal, hypothesis, target_group, time_taken)

  if research_form:
    try:
      # Parse the research form string into a JSON object
      research_form_json = json.loads(research_form)
      return {"research_form": research_form_json} 
    except json.JSONDecodeError:
      return {"error": "Failed to parse research form into JSON."}
  else:
    return {"error": "Failed to generate research form."}

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)