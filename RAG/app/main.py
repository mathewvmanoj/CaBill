from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models.codelama import (
    generate_response,
    generate_natural_lang_response,
    classify_question,
    generate_mongo_query_with_schema,
    is_generic_question,
)
from app.databaseClient import MongoDBClient
from app.responseEngine import responseGeneration
import re
from app.logging_config import configure_logger  # Import the logging configuration

# Get the logger from the logging configuration module
logger = configure_logger()
db_client = MongoDBClient()

# Initialize FastAPI app
app = FastAPI(
    title="MongoDB Query Generator API",
    description="Generate MongoDB queries based on user questions",
    version="1.0",
)

# Allow all origins (for development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QueryRequest(BaseModel):
    """Request model for query generation."""

    question: str
    result: str


@app.post("/generate_query", summary="Generate MongoDB Query")
async def generate_query(request: QueryRequest):
    """
    API endpoint to generate a MongoDB query based on the user's question.
    Args: request (QueryRequest): User's question and expected result format.
    Returns: dict: Generated query if valid, otherwise an error response.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    return await responseGeneration(db_client, request.question)


@app.post("/generate_response", summary="Generate Natural Language Response")
async def generate_responses(request: QueryRequest):
    """
    API endpoint to generate a natural language response.
    Args: request (QueryRequest): User's question and expected result format.
    Returns: dict: Generated natural language response.
    """
    try:
        response = await generate_natural_lang_response(
            request.question, request.result
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server on port 5001")
    uvicorn.run(app, host="0.0.0.0", port=5001)
