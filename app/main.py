from fastapi import FastAPI
from pydantic import BaseModel
import json
from app.form_generator import analyze_researcher_input, format_to_json


# Initialize the FastAPI app
app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Define the input data model using Pydantic
class FormInput(BaseModel):
    goal: str
    target_group: str
    hypothesis: str
    time_taken: int  # Time in minutes

# Endpoint to generate the research form
@app.post("/generate_form/")
async def generate_form_endpoint(input: FormInput):
    # Call the function to generate the form based on the inputs
    form_response = analyze_researcher_input(input.goal, input.target_group,
                                             input.hypothesis, input.time_taken)
    
    # Try to format the response into JSON
    form_json = format_to_json(form_response)

    # Return the JSON formatted research form
    if form_json:
        return {"form_questions": form_json}
    else:
        return {"error": "Failed to generate valid JSON from the response."}
