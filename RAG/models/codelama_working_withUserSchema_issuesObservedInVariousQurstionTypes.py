import os
import re
from groq import Groq

# Set your Groq API key (make sure to replace with your actual key)
api_key = "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"  # Or use os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)

# Function to generate MongoDB queries based on user question and schema
def generate_mongo_query_with_schema(question, schema):
    # Provide schema details in the prompt
    schema_info = f"The schema for your MongoDB database is as follows: {schema}"

    # Use Groq model to generate a response based on the user question
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{schema_info} Generate a MongoDB query for the following task: {question}",
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
    # Check if the response contains the necessary query structure
    if "active" in response and "status" in response:
        return f"db.users.find({{ status: 'active' }})"
    elif "faculty" in response and "role" in response:
        return f"db.users.find({{ role: 'faculty' }})"
    elif "name" in response:
        name = extract_name_from_response(response)
        return f"db.users.find({{ first_name: '{name}' }})"
    else:
        return "Invalid query format"

# Helper function to extract names from the response using regex
def extract_name_from_response(response):
    match = re.search(r"(\w+)", response)  # Matches the first name
    if match:
        return match.group(1)
    else:
        raise ValueError("Name not found in the response")

# Define your MongoDB schema for `users`
schema = {
    "users": {
        "fields": {
            "_id": "ObjectId",
            "first_name": "string",
            "last_name": "string",
            "email": "string",
            "password": "hashed_string",
            "role": "string",
            "status": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        },
        "description": "A collection of users with their personal and account details"
    }
}

# Example usage
question = "Find all active users"
mongo_query = generate_mongo_query_with_schema(question, schema)
print("Generated Mongo Query:", mongo_query)

question_2 = "List all faculty members"
mongo_query_2 = generate_mongo_query_with_schema(question_2, schema)
print("Generated Mongo Query:", mongo_query_2)

question_3 = "All faculty with name containing 'JOE'"
mongo_query_3 = generate_mongo_query_with_schema(question_3, schema)
print("Generated Mongo Query:", mongo_query_3)

question_4 = "All users with name containing 'JOE'"
mongo_query_4 = generate_mongo_query_with_schema(question_4, schema)
print("Generated Mongo Query:", mongo_query_4)

question_5 = "All usernames with name containing 'JOE' or 'MAT'"
mongo_query_5 = generate_mongo_query_with_schema(question_5, schema)
print("Generated Mongo Query:", mongo_query_5)