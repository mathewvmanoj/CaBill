from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class DatabaseConnection:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        try:
            cls.client = AsyncIOMotorClient(settings.MONGO_URI)
            cls.db = cls.client[settings.MONGO_DB_NAME]
            print("Connected to MongoDB successfully!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed.")

# Database connection function
async def get_database():
    return DatabaseConnection.db

# uvicorn app.main:app --reload