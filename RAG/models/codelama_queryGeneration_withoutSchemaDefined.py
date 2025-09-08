import os
import re
from groq import Groq

# Set your Groq API key (make sure to replace with your actual key)
api_key = "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"  # Or use os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)

# Function to generate MongoDB queries based on user question
def generate_mongo_query(question):
    # Use Groq model to generate a response based on the user question
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Generate a MongoDB query for the following task: {question}",
            }
        ],
        model="llama3-8b-8192",  # Choose a valid model available in your access
    )

    response = chat_completion.choices[0].message.content
    print("Groq Model Response:", response)

    # Post-process the model's response to create a Mongo query
    mongo_query = post_process_response_to_mongo_query(response)
    return mongo_query

# Example of a post-processing function that converts the model's response to a MongoDB query
def post_process_response_to_mongo_query(response):
    # Use regex to extract numbers from the response
    if "greater than" in response and "age" in response:
        age = extract_number_from_response(response, "greater than")
        return f"db.users.find({{ age: {{ $gt: {age} }} }})"
    elif "less than" in response and "salary" in response:
        salary = extract_number_from_response(response, "less than")
        return f"db.employees.find({{ salary: {{ $lt: {salary} }} }})"
    else:
        return "Invalid query format"

# Helper function to extract numbers from the response using regex
def extract_number_from_response(response, condition):
    # Regex to match numbers after "greater than" or "less than"
    match = re.search(rf"{condition}\s+(\d+)", response)
    if match:
        return int(match.group(1))
    else:
        raise ValueError("Number not found in the response")

# Example usage
question = "Find all users who are older than 30"
mongo_query = generate_mongo_query(question)
print("Generated Mongo Query:", mongo_query)

question_2 = "List all employees with a salary less than 50000"
mongo_query_2 = generate_mongo_query(question_2)
print("Generated Mongo Query:", mongo_query_2)
