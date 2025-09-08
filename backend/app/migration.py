import asyncio
from app.database import DatabaseConnection
from datetime import datetime
from bson import ObjectId
from passlib.hash import bcrypt

# Admin user details
ADMIN_EMAIL = "admin@loyalistcollege.com"
ADMIN_PHONE = "9999999999"
ADMIN_PASSWORD = "admin123"  # Change this later for security
ADMIN_ROLE = "finance"

async def run_migration():
    db = DatabaseConnection.db

    # Check if the 'users' collection exists
    collections = await db.list_collection_names()
    if "users" not in collections:
        # Create 'users' collection if not exists
        await db.create_collection("users")
        print("Created 'users' collection.")

    # Check if the admin user already exists
    existing_admin = await db.users.find_one({"email": ADMIN_EMAIL})
    
    if not existing_admin:
        # Hash the admin password
        hashed_password = bcrypt.hash(ADMIN_PASSWORD)
        
        # Create admin user document
        admin_user = {
            "_id": ObjectId(),
            "email": ADMIN_EMAIL,
            "phone_number": ADMIN_PHONE,
            "role": ADMIN_ROLE,
            "hashed_password": hashed_password,
            "status": "active",
            "created_at": datetime.utcnow(),
            "last_login": None,
            "current_session_start": None,
            "is_logged_in": False,
            "last_active": None,
            "login_history": [],
            "login_info": {"last_logout": None},
            "logout_info": {},
            "first_name": "Admin",
            "last_name": "User"
        }

        # Insert the admin user into the collection
        await db.users.insert_one(admin_user)
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")