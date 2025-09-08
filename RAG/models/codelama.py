import os
import re
import logging
from groq import Groq
from requests.exceptions import RequestException
from requests.exceptions import RequestException
import requests
from app.logging_config import configure_logger
from app.config import api_key


# Get the logger from the logging configuration module
logger = configure_logger()

# Set your Groq API key (use os.getenv for security in production)
if not api_key:
    logger.error("API key is missing!")
    raise EnvironmentError("GROQ_API_KEY environment variable not set")

client = Groq(api_key=api_key)

# Define MongoDB collection schemas
mongo_schemas = {
    "users": """
    Collection: users
    Fields:
    - _id (ObjectId)
    - first_name (string)
    - last_name (string)
    - email (string)
    - role (string) [faculty, student, admin, etc.]
    - status (string) [active, inactive]
    - created_at (datetime)
    - updated_at (datetime)
    """,
    "invoices": """
    Collection: invoices
    Fields:
    - _id (ObjectId)
    - faculty_id (ObjectId) -> References users._id
    - total_hours_worked (int)
    - status (string) [pending, approved, rejected]
    - submitted_at (datetime)
    - comments (array) -> Nested comments with sender_email, message, timestamps
    """,
    "schedule": """
    Collection: schedule
    Fields:
    - _id (ObjectId)
    - course_code (string)
    - instructor (string)
    - room (string)
    - start_time (string)
    - end_time (string)
    - created_at (datetime)
    - updated_at (datetime)
    """
}

# Function to detect the relevant schema based on user question
def detect_relevant_schema(question):
    try:
        question_lower = question.lower()
        for collection, schema in mongo_schemas.items():
            if any(keyword in question_lower for keyword in schema.lower().split("\n")):
                return schema
        return None
    except Exception as e:
        logger.error(f"Error detecting relevant schema: {e}")
        return None

# Function to predict whether a question is generic or a query
def classify_question(question, mongo_schemas):
    """Classifies the question as 'general' or 'specific' based on the schema."""
    try:
        prompt = (
            f"Question: {question}\n"
            f"Schema: {mongo_schemas}\n"
            f"Classify the question as either 'general' or 'specific'."
        )

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )

        response = chat_completion.choices[0].message.content.strip().lower()

        # Normalize response
        if "specific" in response:
            return "specific"
        elif "general" in response:
            return "general"
        else:
            logger.warning(f"Unexpected classification response: {response}")
            return "general"  # Default fallback

    except Exception as e:
        logger.error(f"Error classifying question: {e}")
        return "general"

# def classify_question(question):
#     """Classifies the question into categories such as 'user query', 'invoice query', or 'schedule query'."""
#     try:
#         # url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
#         # headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', 'your_huggingface_api_key')}"}
#         # payload = {"inputs": question, "parameters": {"candidate_labels": ["users", "invoices", "schedule", "general"]}}
#         # response = requests.post(url, headers=headers, json=payload)
#         # response.raise_for_status()
#         # result = response.json()
#         # return result["labels"][0] if "labels" in result else "general"

#         prompt = f"Question: {question}\nIs this question related to the schema definition or a general question? Schema: {mongo_schemas}. Return 'general' & 'specific' as response."

#         chat_completion = client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="llama3-8b-8192",
#         )
        
#         response = chat_completion.choices[0].message.content
#         return response
#     except Exception as e:
#         logger.error(f"Error classifying question: {e}")
#         return "general"

# Extract specific keywords from schema to be dynamic in identifying generics questions
def extract_keywords_from_schema(mongo_schemas):
    """Extracts relevant keywords from the schema definitions for classification."""
    schema_keywords = set()

    for collection, schema_text in mongo_schemas.items():
        schema_keywords.add(collection.lower())  # Collection name
        for line in schema_text.split("\n"):
            line = line.strip()
            if line.startswith("- "):  # Extract field names
                field_name = line.split(" ")[1].strip("()")
                schema_keywords.add(field_name.lower())

    return list(schema_keywords)  # Return as a list

# Function to check if a question is generic or specific to a query
def is_generic_question(question):
    # List of keywords or patterns indicating it's a database query
    query_keywords = ["retrieve", "find", "get", "count", "list", "where", "invoices", "users", "schedules"]
    
    # Add schema-specific keywords
    query_keywords.extend(extract_keywords_from_schema(mongo_schemas))

    question_lower = question.lower()
    return not any(keyword in question_lower for keyword in query_keywords)

# Function to generate natural language response based on whether the question is generic or specific
async def generate_response(question):
    prompt = f"Question: {question}\nGenerate a general response to this question."

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    
    response = chat_completion.choices[0].message.content
    return response

# Function to generate MongoDB query with dynamic schema selection
def generate_mongo_query_with_schema(question):
    logger.info(f"Processing generate_mongo_query_with_schema with question: {question}")
    try:
        schema = detect_relevant_schema(question)
        if not schema:
            logger.error(f"No matching schema found for the question: {question}")
            return "Error: No matching schema found for the question."
        
        prompt = f"{schema}\nGenerate a MongoDB query for: {question}"
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            response = chat_completion.choices[0].message.content
        except RequestException as e:
            logger.error(f"API request failed: {e}")
            return "Error: API request failed."
        
        return extract_mongo_query(response)
    except Exception as e:
        logger.error(f"Error generating MongoDB query: {e}")
        return "Error: Unexpected error occurred."

# Improved regex function to extract MongoDB queries
def extract_mongo_query(response):
    try:
        match = re.search(r"(db\.\w+\.(?:find|aggregate|countDocuments)\(.*?\))", response, re.DOTALL)
        if match:
            return match.group(1)
        else:
            logger.warning("Could not extract MongoDB query from response.")
            return "Error: Could not extract MongoDB query."
    except Exception as e:
        logger.error(f"Error extracting MongoDB query: {e}")
        return "Error: Could not extract MongoDB query."

# Function to generate natural language response
async def generate_natural_lang_response(question, result):
    try:
        prompt = f"Question: {question}\nResult: {result}\nGenerate a natural language response based on the result.  Also remove any sensitive information from the resultset & any information related to ADMIN users(Do not mention about these santizations in the result)."
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            response = chat_completion.choices[0].message.content
            return response
        except RequestException as e:
            logger.error(f"API request failed while generating natural language response: {e}")
            return "Error: API request failed."
    except Exception as e:
        logger.error(f"Error generating natural language response: {e}")
        return "Error: Unexpected error occurred."

# List of test queries
error_questions = [
    "Retrieve details of a user with email 'john.doe@example.com'",
    "Retrieve users who were created after '2024-01-01'",
    "Retrieve users who were updated within the last 30 days",
    "Retrieve invoices where status is 'approved'",
    "Get schedules where the duration is more than 3 hours",
    "Get all schedules where the instructor is also a faculty member",
    "Retrieve invoices for users whose email contains '@loyalistcollege.com'",
    "Retrieve all users who have at least one submitted invoice",
    "Get invoices that have comments with more than one reply",
    "Retrieve all schedules that have the course code starting with 'CS'",
    "Find invoices where the total hours worked match the instructor’s schedule",
    "Count the number of active users",
    "Get the total number of invoices",
    "Retrieve the number of schedules available for 'CS101'",
    "Find the total worked hours across all invoices",
    "Get the total number of invoices with pending status",
    "Find the number of users with the role 'student'",
    "Count the number of invoices per faculty member",
    "Get the number of schedules per instructor",
    "Retrieve the number of invoices submitted each month",
    "Count the number of schedules per room"
]

# List of test queries for verification
questions = [
    "Find all active users",
    "List all inactive users",
    "Retrieve details of a user with email 'john.doe@example.com'",
    "Get all users with role 'student'",
    "Find all users who are faculty members",
    "List users whose first name is 'David'",
    "Find users with last name 'Smith'",
    "Retrieve users who were created after '2024-01-01'",
    "Get users sorted by creation date (descending)",
    "Find users whose email ends with '@loyalistcollege.com'",
    "List all admin users",
    "Get all users with the role 'staff'",
    "Retrieve users who were updated within the last 30 days",
    "Find users with email containing 'john'",
    "Get all users whose status is either 'active' or 'pending'",
    "Find users who have not logged in since '2023-12-01'",
    "Get users sorted by last updated date (ascending)",
    "Retrieve users where the last name starts with 'J'",
    "Find users whose first name contains 'Michael' (case-insensitive)",
    "List all users who were created before '2024-02-01'",

    "Get all invoices that are pending",
    "Find invoices with total_hours_worked greater than 40",
    "Retrieve all invoices for faculty ID '65c026f8a1b2f3c4d56789ab'",
    "Get all invoices submitted after '2024-01-15'",
    "Find invoices that contain a comment from 'finance@loyalistcollege.com'",
    "Get all invoices sorted by submission date (newest first)",
    "Retrieve invoices where status is 'approved'",
    "Find invoices submitted before '2024-01-10'",
    "Get all invoices that contain a worked day entry for 'CS101'",
    "Find invoices with at least 10 worked days",
    "Retrieve invoices with total hours worked less than 20",
    "Get all invoices where the status is either 'pending' or 'under review'",
    "Find invoices that were submitted in February 2024",
    "Get invoices that have comments with more than one reply",
    "Retrieve invoices sorted by total hours worked (descending)",
    "Find invoices that have at least one comment",
    "Get invoices where a comment message contains 'verify total hours'",
    "Find invoices where the first comment was sent by 'finance@loyalistcollege.com'",
    "Retrieve invoices where worked days include the course 'CS103'",
    "Get invoices with a total hours worked between 30 and 50",

    "Retrieve all schedule details for instructor 'Femi Johnson'",
    "Find all schedules in Room 108",
    "Get all schedules where the course code is 'SUST1002'",
    "Find schedules for group 'M02M(GBM)-Sem2-G1'",
    "Retrieve all schedules that start on '2024-09-06'",
    "Get schedules with an end date after '2024-12-01'",
    "Find all schedules where start time is '08:00 AM'",
    "Retrieve schedules for courses that start in September 2024",
    "Find all schedules that are in Room 202",
    "Get schedules sorted by start date (ascending)",
    "Retrieve schedules where the instructor name starts with 'F'",
    "Find schedules that were created on '2024-02-06'",
    "Get all schedules updated after '2024-02-10'",
    "Retrieve schedules that have an end time of '11:00 AM'",
    "Find schedules that have an instructor name starting with 'Sarah'",
    "Get all schedules for 'CS101' for the fall semester",
    "Find schedules with a start time earlier than '09:00 AM'",
    "Get schedules for course 'CS201' where the room is 'Room 105'",
    "Retrieve schedules where the course code starts with 'CS'"
]

# ## Verification of code
# for question in questions:
#     logger.info(f"User Question: {question}")
#     mongo_query = generate_mongo_query_with_schema(question)
#     logger.info(f"Generated Mongo Query: {mongo_query}")
