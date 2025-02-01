from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.models.dto import ResearcherInput, FormData, Question  # Importing DTOs from dto.py
from app.models.form_generator import analyze_researcher_input  # Importing form generation 
from app.models.survey_report import run_analysis  # Importing the survey report
from app.models.form_bot import interact_with_survey  # Importing the chatbot interaction function
import uvicorn
import json
import os
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins. Replace "*" with specific origins if needed.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
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
        logger.debug("Received survey data: %s", survey_data.json())
        if not survey_data.isGenerated:
            if not survey_data.goal or not survey_data.hypothesis or not survey_data.targetGroup or not survey_data.timeTaken:
                raise HTTPException(
                    status_code=400,
                    detail="Required fields (goal, hypothesis, targetGroup, timeTaken) are missing for non-AI-generated form."
                )
        
        logger.debug("Received survey data: %s", survey_data.json())
        
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
        logger.error("Error generating survey report: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating survey report: {str(e)}")

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import os
import logging
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

class Question(BaseModel):
    question: str
    questionType: str
    options: List[str]
    isRequired: bool
    _id: str
    answers: List[List[str]]

class SurveyData(BaseModel):
    _id: str
    title: str
    questions: List[Question]
    summary: Optional[str] = None
    user: str
    isPublished: bool
    isActive: bool
    isGenerated: bool
    isResultsShared: bool
    goal: Optional[str] = None
    hypothesis: Optional[str] = None
    targetGroup: Optional[str] = None
    timeTaken: Optional[str] = None

class SurveyQueryRequest(BaseModel):
    survey_data: SurveyData
    query: str

# Chatbot Functions
def initialize_llm_chain():
    llm = ChatOpenAI(temperature=0.7, model="gpt-4")
    prompt_template = """
    You are an intelligent assistant helping analyze survey data. Use this data:
    {data}
    
    Question: {query}
    
    Guidelines:
    1. Answer based only on the provided data
    2. Be concise and specific
    3. If data is missing, state that clearly
    """
    prompt = PromptTemplate(input_variables=["data", "query"], template=prompt_template)
    return LLMChain(prompt=prompt, llm=llm)

def process_survey_data(survey_data: SurveyData):
    responses_str = "\n".join(
        [f"Q: {q.question}\nA: {', '.join(a[0] for a in q.answers)}" 
         for q in survey_data.questions]
    )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return text_splitter.split_text(responses_str)

@app.post("/ask_survey_question")
async def ask_survey_question(request: SurveyQueryRequest):
    try:
        chunks = process_survey_data(request.survey_data)
        llm_chain = initialize_llm_chain()
        response = llm_chain.run({
            "data": "\n".join(chunks),
            "query": request.query
        })
        return JSONResponse(content={"response": response})
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
