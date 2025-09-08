import os
import re
from groq import Groq


# Set your Groq API key (make sure to replace with your actual key)
api_key = "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"  # Or use os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)

# Define MongoDB schema for `users`
mongo_schema = """
The MongoDB collection 'users' has the following fields:
- _id (ObjectId)
- first_name (string)
- last_name (string)
- email (string)
- password (hashed_string)
- role (string) [faculty, student, admin, etc.]
- status (string) [active, inactive]
- created_at (datetime)
- updated_at (datetime)

Ensure that queries use correct field names and data types.
"""

# Function to generate MongoDB queries based on user question and schema
def generate_mongo_query_with_schema(question):
    # Provide schema details in the prompt
    prompt = f"{mongo_schema}\nGenerate a MongoDB query for: {question}"

    # Use Groq model to generate a response
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )

    response = chat_completion.choices[0].message.content
    print("\nGroq Model Response:\n", response)

    # Extract the valid MongoDB query
    mongo_query = extract_mongo_query(response)
    return mongo_query

# Extracts MongoDB query from response using regex
def extract_mongo_query(response):
    match = re.search(r"db\.users\.find\((.*?)\)", response, re.DOTALL)
    return f"db.users.find({match.group(1)})" if match else "Error: Could not extract MongoDB query."

# Example usage
questions = [
    "Find all active users",
    "List all faculty members",
    "Find users whose first name contains 'Joe'",
    "Find users whose first or last name contains 'Joe' or 'Mat'",
]

for question in questions:
    print("\nUser Question:", question)
    mongo_query = generate_mongo_query_with_schema(question)
    print("Generated Mongo Query:", mongo_query)
