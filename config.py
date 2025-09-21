import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI')  # Fetch MONGO_URI from .env
    SECRET_KEY = os.getenv('SECRET_KEY')  # Fetch SECRET_KEY from .env
