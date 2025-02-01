import openai
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv  # For loading the API key from environment variables
import os
from app.models.dto import SurveyData

# Load OpenAI API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Step 1: Load Data from JSON File
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
    # New chain using RunnableSequence (pipe operator)
    return prompt | llm


def process_survey_data(survey_data: SurveyData):
    responses_str = "\n".join(
        [f"Q: {q.question}\nA: {', '.join(a[0] for a in q.answers)}" 
         for q in survey_data.questions]
    )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return text_splitter.split_text(responses_str)