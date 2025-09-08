from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.codelama import (
    generate_response,
    generate_natural_lang_response,
    classify_question,
    generate_mongo_query_with_schema,
    is_generic_question,
)
from app.databaseClient import MongoDBClient
import re
from app.logging_config import configure_logger  # Import the logging configuration

# Get the logger from the logging configuration module
logger = configure_logger()


def __init__(self):
    """Initialize AppService with MongoDBClient."""
    self.db_client = MongoDBClient()


def is_read_only_query(query: str) -> bool:
    """
    Checks if the generated MongoDB query is read-only.
    Args: query (str): The MongoDB query string.
    Returns: bool: True if the query is read-only, False otherwise.
    """
    if not isinstance(query, str):
        return False  # Ensure query is a valid string before processing

    # Strict regex patterns to detect write operations
    write_operation_patterns = [
        r"\b(?:insert|update|delete|drop|create|rename|replace|modify|insertMany|updateMany|bulkWrite)\b",
        r"\$set\b",  # For detecting $set, which is part of update operations
        r"\$push\b",  # For detecting $push (array modification)
        r"\$addToSet\b",  # For detecting $addToSet (array modification)
        r"\$pull\b",  # For detecting $pull (array modification)
    ]

    for pattern in write_operation_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False  # Detected a write operation
    return True


async def responseGeneration(db_client: MongoDBClient, question: str):
    try:
        # Check if it's a general or MongoDB-specific question
        if is_generic_question(question):
            logger.info("Processing as a natural language response")
            # This is taken out as per request from Advisor
            # response = generate_natural_lang_response(question, request.result)
            response = "Sorry, currently I can only answer questions specific to Finance records. Ask me a specific question."
            return {"response": response}

        logger.info("Processing as a MongoDB query request")
        mongo_query = generate_mongo_query_with_schema(question)

        # Validate the generated query
        if not mongo_query or "Error:" in mongo_query:
            raise HTTPException(
                status_code=400, detail="Failed to generate a valid query"
            )

        if not is_read_only_query(mongo_query):
            raise HTTPException(
                status_code=400, detail="Generated query is not a read-only operation"
            )

        logger.info(f"Going to execute db query: {str(mongo_query)}")
        query_result = await db_client.execute_query(mongo_query)
        nlp_output = await generate_natural_lang_response(question, query_result)

        return nlp_output

    except Exception as e:
        logger.error(f"Error generating MongoDB query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
