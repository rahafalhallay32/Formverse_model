from app.models.form_generator import analyze_researcher_input, format_to_json

# Example input for the researcher
researcher_input = {
    "goal": "Gather information about using AI in daily life",
    "hypothesis": "Check how many people trust AI",
    "target_group": "Adults aged 25-40",
    "time_taken": 5
}

# Call the analyze_researcher_input function
response = analyze_researcher_input(
    goal=researcher_input["goal"],
    hypothesis=researcher_input["hypothesis"],
    target_group=researcher_input["target_group"],
    time_taken=researcher_input["time_taken"]
)

# Format the response to JSON
if response:
    formatted_response = format_to_json(response)
    if formatted_response:
        print("Generated Research Form:")
        print(formatted_response)
    else:
        print("Failed to format the response into JSON.")
else:
    print("Failed to generate the research form.")
