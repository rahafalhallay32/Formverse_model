from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from app.models.dto import ResearcherInput, FormData, SurveyQueryRequest, SurveyData # Importing DTOs from dto.py
from app.models.form_generator import analyze_researcher_input  # Importing form generation 
from app.models.survey_report import run_analysis  # Importing the survey report
import uvicorn
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from app.models.form_bot import initialize_llm_chain, process_survey_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def generate_survey_report(survey_data: FormData):
    try:
        # Check if the form is not AI-generated and validate required fields
        if not survey_data.isGenerated:
            if not survey_data.goal or not survey_data.hypothesis or not survey_data.targetGroup or not survey_data.timeTaken:
                raise HTTPException(
                    status_code=400,
                    detail="Required fields (goal, hypothesis, targetGroup, timeTaken) are missing for non-AI-generated form."
                )
        
        output_path = "./output"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        json_data = survey_data.json()
        report_filename = run_analysis(json_data, output_path)
        
        return FileResponse(
            report_filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename="survey_analysis_report.docx"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating survey report: {str(e)}")

@app.post("/ask_survey_question")
async def ask_survey_question(request: SurveyQueryRequest):
    try:
        chunks = process_survey_data(request.survey_data)
        llm_chain = initialize_llm_chain()
        response = llm_chain.invoke({
            "data": "\n".join(chunks),
            "query": request.query
        })
        return JSONResponse(content={"response": response.content })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
