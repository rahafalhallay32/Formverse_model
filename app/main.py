from fastapi import FastAPI
from app.models.form_generator import generate_form
#from app.models.form_summarization import summarize_responses
from pydantic import BaseModel

app = FastAPI()

class FormInput(BaseModel):
    goal: str
    group_type: str

class ResponseInput(BaseModel):
    responses: list[str]

@app.post("/generate_form/")
async def generate_form_endpoint(input: FormInput):
    form = generate_form(input.goal, input.group_type)
    return {"form_questions": form}

'''
@app.post("/summarize_responses/")
async def summarize_responses_endpoint(input: ResponseInput):
    summary = summarize_responses(input.responses)
    return {"summary": summary}'''
