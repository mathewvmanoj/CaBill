from bson import ObjectId
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.database import DatabaseConnection
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    FACULTY = "faculty"
    FINANCE = "finance"

class User(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    role: str  # "faculty" or "finance"
    created_at: datetime

async def get_user_by_email(email: str):
    """ Fetch user details by email """
    user = await DatabaseConnection.db.users.find_one({"email": email})
    return user if user else None
