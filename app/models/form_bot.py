import openai
import json
import re
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv  # For loading the API key from environment variables
import os
from pathlib import Path


# Load OpenAI API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Step 1: Load Data from JSON File
def load_json_data(file_path):
    """Load JSON data from a file, with error handling."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file at {file_path} does not exist.")
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


# Step 2: Clean and Preprocess Responses
def clean_text(text):
    """Clean the text by removing unwanted characters and standardizing."""
    if isinstance(text, list):  # If the text is a list, join it into a string
        text = ' '.join(text)
    
    # Basic text cleaning: remove unwanted characters, extra spaces
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    text = text.strip()  # Remove leading/trailing spaces
    return text


# Step 3: Normalize and Flatten Data
def normalize_data(responses_data):
    """Normalize and flatten survey data into a consistent format."""
    cleaned_responses = {}
    
    # Loop through each user's responses
    for user, responses in responses_data.items():
        user_responses = {}
        
        # If responses are a list of questions
        if isinstance(responses, list):
            for item in responses:
                question = item.get("question")
                answer = item.get("answer")
                if question and answer:
                    user_responses[question] = clean_text(answer)
        
        # If responses are a dictionary
        elif isinstance(responses, dict):
            for question, answer in responses.items():
                user_responses[question] = clean_text(answer)

        # Store the user's responses in the cleaned_responses dictionary
        cleaned_responses[user] = user_responses

    return cleaned_responses


# Step 4: Split the Data into Chunks using Langchain Text Splitter
def split_data(responses_data):
    """Process and split data into chunks."""
    # Normalize the responses into a standard format
    cleaned_responses = normalize_data(responses_data)

    # Convert cleaned responses into a string format for each user
    responses_str = "\n".join([f"{user}: {', '.join(responses.values())}" for user, responses in cleaned_responses.items()])

    # Initialize the text splitter (Langchain RecursiveCharacterTextSplitter)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

    # Split the data into manageable chunks
    chunks = text_splitter.split_text(responses_str)
    
    return chunks


# Step 5: Create Chatbot Using Langchain and OpenAI LLM
def initialize_llm_chain():
    """Initialize the language model chain."""
    llm = ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai.api_key)

    prompt_template = """
    You are an intelligent assistant helping a researcher interact with user responses from a survey. Your task is to answer the following question based only on the survey responses provided in the JSON file below.

    ### Survey Data:
    {data}

    ### Question:
    {query}

    ### Important Guidelines:
    1. **Only use the data provided in the JSON file** to answer the question.
    2. Ensure that your response is **directly relevant to the question** and based on the survey responses.
    3. If the question cannot be answered with the provided data, **inform the researcher** that the necessary data is not available, and suggest possible next steps to gather more information.
    4. Keep your response **concise**, **clear**, and **focused** on the question at hand.
    """
    
    prompt = PromptTemplate(input_variables=["data", "query"], template=prompt_template)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    
    return llm_chain


# Step 6: Set Up the Chatbot
def chatbot_interaction(query, chunks, llm_chain):
    """Interact with the chatbot and return a response."""
    # Loop over all chunks and process them with the LLM chain
    answers = []
    for chunk in chunks:
        # Get the response from the LLM based on the chunk and user query
        answer = llm_chain.run({"data": chunk, "query": query})
        answers.append(answer)

    # Combine all answers to form a final response
    final_answer = "\n".join(answers)
    return final_answer


def interact_with_survey(file_path, query):
    """Main function to load JSON, process it, and answer queries."""
    try:
        # Load JSON data from the saved file
        responses_data = load_json_data(file_path)
        
        # Split the data and initialize the LLM chain
        chunks = split_data(responses_data)
        llm_chain = initialize_llm_chain()
        
        # Get the response from the chatbot interaction
        response = chatbot_interaction(query, chunks, llm_chain)
        return response

    except Exception as e:
        raise Exception(f"Error processing survey data: {str(e)}")


"""
# Example usage
if __name__ == "__main__":
    # Assume the user uploads a JSON file
    file_path = Path(__file__).parent / "test.json"
    question = "What are the most common barriers to physical activity?"
    
    answer = interact_with_survey(file_path, question)
    print(f"Bot: {answer}")
"""