from fastapi import APIRouter, HTTPException, status, Depends
from app.models import get_user_by_email
from app.security import verify_password, create_access_token, create_refresh_token, get_password_hash
from app.schemas import (
    LoginRequest, LoginResponse, RegisterFacultyRequest, RegisterFacultyResponse,
    FacultyResponse, UpdateFacultyRequest, UpdateFacultyByFinanceRequest
)
from typing import List
from datetime import timedelta, datetime
from jose import jwt, JWTError
from bson import ObjectId
from app.config import settings
from app.dependencies import get_current_user
from app.database import get_database

router = APIRouter()

### **1️⃣ API: Faculty & Finance Login**
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db=Depends(get_database)):
    """ Authenticate user, validate role, update login data, and return JWT tokens. """
    
    user = await get_user_by_email(request.email)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if user["role"] != request.role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Incorrect role")
    
    if user["status"] != "active":
        raise HTTPException(status_code=403, detail="Account is inactive. Contact support.")

    # ✅ Update login info
    login_time = datetime.utcnow()
    login_entry = {"timestamp": login_time, "ip": "127.0.0.1"}  # Store IP if available

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "last_login": login_time,
            "current_session_start": login_time,
            "is_logged_in": True,
            "last_active": login_time
        },
        "$push": {"login_history": login_entry}}
    )

    # Generate Tokens
    access_token = create_access_token(data={"sub": user["email"], "role": user["role"]}, expires_delta=timedelta(minutes=60))
    refresh_token = create_refresh_token(data={"sub": user["email"], "role": user["role"]}, expires_delta=timedelta(days=7))

    return {
        "success": True,
        "message": "Authentication successful",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "role": user["role"],
                "status": user["status"], 
                "phone_number": user.get("phone_number", ""),
                "last_login": user.get("last_login"),
                "created_at": user["created_at"].isoformat()
            }
        }
    }

### **2️⃣ API: Faculty Registration by Finance**
@router.post("/register", response_model=RegisterFacultyResponse)
async def register_faculty(request: RegisterFacultyRequest, current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    """ Allows only finance users to register faculty. """

    if current_user["role"] != "finance":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only finance can register faculty users")

    # ✅ Convert email to lowercase before checking & saving
    normalized_email = request.email.lower()

    # ✅ Case-insensitive email check
    existing_user = await db.users.find_one({"email": {"$regex": f"^{normalized_email}$", "$options": "i"}})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = get_password_hash(request.password)
    new_user = {
        "_id": ObjectId(),
        "email": normalized_email,  # ✅ Always store emails in lowercase
        "hashed_password": hashed_password,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "role": request.role if request.role else "faculty",
        "status": request.status if request.status else "active",
        "phone_number": request.phone_number,
        "created_at": datetime.utcnow(),
        "login_history": [],
        "is_logged_in": False,
        "last_login": None,
        "current_session_start": None,
        "last_active": None
    }

    await db.users.insert_one(new_user)

    return RegisterFacultyResponse(
        message="Faculty registration successful!",
        user=FacultyResponse(
            id=str(new_user["_id"]),
            email=new_user["email"],
            phone_number=new_user["phone_number"],
            first_name=new_user["first_name"],
            last_name=new_user["last_name"],
            role=new_user["role"],
            status=new_user["status"],
            is_logged_in=new_user["is_logged_in"],
            created_at=new_user["created_at"]
        )
    )


### **3️⃣ API: Faculty Updates Their Profile (Self)**
@router.put("/update/faculty-self")
async def update_faculty_self(request: UpdateFacultyRequest, current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    """ Allows Faculty to update their own profile. """
    
    if current_user["role"] != "faculty":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only faculty can update their profile")

    faculty = await db.users.find_one({"_id": ObjectId(current_user["id"])})
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    update_data = {}

    if request.first_name:
        update_data["first_name"] = request.first_name
    if request.last_name:
        update_data["last_name"] = request.last_name
    if request.phone_number:
        update_data["phone_number"] = request.phone_number

    if request.password and request.old_password:
        if not verify_password(request.old_password, faculty["hashed_password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect old password")

        update_data["hashed_password"] = get_password_hash(request.password)

    update_data["updated_at"] = datetime.utcnow()
    await db.users.update_one({"_id": ObjectId(current_user["id"])}, {"$set": update_data})

    return {"message": "Profile updated successfully", "updated_fields": list(update_data.keys())}

### **4️⃣ API: Finance Updates Faculty (Including Role & Status)**
@router.put("/update/faculty-finance")
async def update_faculty_by_finance(
    faculty_id: str, 
    request: UpdateFacultyByFinanceRequest, 
    current_user: dict = Depends(get_current_user), 
    db = Depends(get_database)
):
    """ Allows only Finance to update Faculty's details. """
    
    if current_user["role"] != "finance":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only finance can update faculty details")

    faculty = await db.users.find_one({"_id": ObjectId(faculty_id)})
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    update_data = {}

    if request.first_name:
        update_data["first_name"] = request.first_name
    if request.last_name:
        update_data["last_name"] = request.last_name
    if request.phone_number:
        update_data["phone_number"] = request.phone_number
    if request.email:
        update_data["email"] = request.email
    if request.password:
        update_data["hashed_password"] = get_password_hash(request.password)

    if request.role:
        update_data["role"] = request.role
    if request.status:
        update_data["status"] = request.status

    update_data["updated_at"] = datetime.utcnow()
    await db.users.update_one({"_id": ObjectId(faculty_id)}, {"$set": update_data})

    return {"message": "Faculty details updated successfully", "updated_fields": list(update_data.keys())}

@router.get("/facultyCollection", response_model=List[FacultyResponse])
async def get_faculty_collection(current_user: dict = Depends(get_current_user), db=Depends(get_database)):
    """ Retrieve Complete faculty Collection. Only finance can access this. """
      
    if current_user["role"] != "finance":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only finance can view faculty details")
    
    faculty_collection = await db.users.find({"role":"faculty"}).to_list(None)  # Convert cursor to list

    if not faculty_collection:
        raise HTTPException(status_code=404, detail="No records found.")

    return [
        FacultyResponse(
            id=str(faculty["_id"]),
            email=faculty["email"],
            first_name=faculty["first_name"],
            last_name=faculty["last_name"],
            role=faculty["role"],
            status=faculty["status"],
            phone_number=faculty.get("phone_number", ""),
            is_logged_in=faculty.get("is_logged_in", False),
            created_at=faculty["created_at"]
        )
        for faculty in faculty_collection
    ]