import json
import os
import openai
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from docx import Document
from docx.shared import Inches
from dotenv import load_dotenv  # For loading the API key from environment variables
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi import UploadFile, File

# Load OpenAI API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to load survey data from JSON
def load_survey_data(json_data):
    try:
        survey_data = json.loads(json_data)
        return survey_data
    except json.JSONDecodeError as e:
        print("Error loading JSON:", e)
        return None

# Function to dynamically identify closed-ended questions and analyze responses
def analyze_closed_end_questions(survey_data, doc):
    closed_end_questions = {}
    
    for user in survey_data['survey_responses']:
        for response in user['responses']:
            question = response['question']
            answer = response['answer'].lower()
            
            if answer in ['yes', 'no']:
                if question not in closed_end_questions:
                    closed_end_questions[question] = {'Yes': 0, 'No': 0}
                if answer == 'yes':
                    closed_end_questions[question]['Yes'] += 1
                elif answer == 'no':
                    closed_end_questions[question]['No'] += 1

    for i, (question, counts) in enumerate(closed_end_questions.items()):
        labels = ['Yes', 'No']
        sizes = [counts['Yes'], counts['No']]
        
        chart_filename = f"chart_{i}.png"
        plt.figure(figsize=(6,6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
        plt.title(f"Response Distribution - {question}")
        plt.savefig(chart_filename)
        plt.close()

        doc.add_paragraph(f"Question: {question}")
        doc.add_picture(chart_filename, width=Inches(4.0))
        doc.add_paragraph("\n")
        
        os.remove(chart_filename)

def generate_wordcloud_for_open_end(survey_data, doc):
    open_end_answers = []

    for user in survey_data['survey_responses']:
        for response in user["responses"]:
            if response['answer'].lower() not in ['yes', 'no']:
                open_end_answers.append(response["answer"])
    
    word_counts = Counter(" ".join(open_end_answers).split())
    most_common_words = dict(word_counts.most_common(10))
    
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(most_common_words)
    wordcloud_filename = "wordcloud.png"
    wordcloud.to_file(wordcloud_filename)

    doc.add_paragraph("Top 10 Most Common Words in Open-Ended Questions")
    doc.add_picture(wordcloud_filename, width=Inches(4.0))
    doc.add_paragraph("\n")

    os.remove(wordcloud_filename)

def generate_analysis_with_gpt(survey_data):
    goal = survey_data['goal']
    hypothesis = survey_data['hypothesis']
    target_group = survey_data['target_group']
    time_taken = survey_data['time_taken']
    
    formatted_responses = []
    for user in survey_data['survey_responses']:
        formatted_responses.append(f"User {user['user']} responses:")
        for item in user['responses']:
            formatted_responses.append(f"- {item['question']}: {item['answer']}")

    analyze_prompt = f"""
    You are a skilled data analyst tasked with analyzing survey responses containing both closed and open-ended questions. Your main goal is to deliver a structured and data-driven analysis with proper charts and thematic analysis.

    ### Research Details:
    - *Goal:* {goal}
    - *Hypothesis:* {hypothesis}
    - *Target Group:* {target_group}
    - *Time Taken (in minutes):* {time_taken}
    - *Survey Responses:* {', '.join(formatted_responses)}

    ### Expected Output:
    1. Provide a summary of the survey results.
    2. For closed-ended questions, analyze response distribution.
    3. Perform thematic analysis for open-ended questions.
    4. Evaluate the hypothesis based on the data determine if the hypothesis is: *Supported* or *Partially Supported* or *Not Supported*
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": analyze_prompt}],
        max_tokens=700,
        temperature=0.5
    )
    
    return response.choices[0].message.content

def create_word_document(survey_data, gpt_analysis, output_path):
    # Ensure the output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    doc = Document()
    
    doc.add_heading('Survey Analysis Report', 0)
    doc.add_paragraph(f"Goal: {survey_data['goal']}")
    doc.add_paragraph(f"Hypothesis: {survey_data['hypothesis']}")
    doc.add_paragraph(f"Target Group: {survey_data['target_group']}")
    doc.add_paragraph(f"Time Taken (in minutes): {survey_data['time_taken']}")
    
    doc.add_heading('Analysis:', level=1)
    doc.add_paragraph(gpt_analysis)
    
    analyze_closed_end_questions(survey_data, doc)
    generate_wordcloud_for_open_end(survey_data, doc)
    
    output_filename = os.path.join(output_path, "survey_analysis_report.docx")
    doc.save(output_filename)
    print(f"Analysis saved to {output_filename}")
    
    return output_filename

def run_analysis(json_data, output_path):
    survey_data = load_survey_data(json_data)
    if survey_data:
        gpt_analysis = generate_analysis_with_gpt(survey_data)
        return create_word_document(survey_data, gpt_analysis, output_path)


"""
if __name__ == "__main__":
    with open('../data/survey_data.json', 'r') as file:  # Adjust the path to the data file
        json_data = file.read()
    
    output_path = '../data'  # Specify the output directory
    run_analysis(json_data, output_path)"""