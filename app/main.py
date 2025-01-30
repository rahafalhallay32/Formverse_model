from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from models.dto import ResearcherInput  # Importing DTOs from dto.py
from models.form_generator import analyze_researcher_input  # Importing form generation 
from models.survey_report import run_analysis  # Importing the survey report
from models.form_bot import interact_with_survey  # Importing the chatbot interaction function
import uvicorn
import json
import os

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

# Endpoint survey report
@app.post("/generate_survey_report")
async def generate_survey_report(file: UploadFile = File(...)):
    try:
        if file is None:
            raise HTTPException(status_code=400, detail="File not provided.")
        
        json_data = await file.read()
        output_path = "../data"  # Temporary path for saving the report
        
        # Ensure the output directory exists
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        report_filename = run_analysis(json_data.decode(), output_path)
        
        # Return the generated file as response
        return FileResponse(report_filename, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename="survey_analysis_report.docx")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating survey report: {str(e)}")


# Endpoint for Chatbot Interaction
# Endpoint for Chatbot Interaction
@app.post("/ask_survey_question")
async def ask_survey_question(file: UploadFile = File(...), query: str = ""):
    """
    API endpoint to ask a question to the chatbot based on the survey data.
    It processes the uploaded JSON file and returns a response based on the query.
    """
    try:
        if file is None:
            raise HTTPException(status_code=400, detail="File not provided.")
        if not query:
            raise HTTPException(status_code=400, detail="Query not provided.")

        # Save the uploaded file to a temporary directory
        output_path = "./data"  # Temporary path for saving the file

        # Ensure the output directory exists
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Generate a unique filename for the uploaded file
        file_location = os.path.join(output_path, file.filename)

        # Write the uploaded file to the directory
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())

        # Now pass the file path to the `interact_with_survey` function
        response = interact_with_survey(file_location, query)  # Pass the file path to the function

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interacting with chatbot: {str(e)}")


# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
