from pydantic import BaseModel, EmailStr, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from app.models import UserRole

# ✅ Faculty Status Enum
class FacultyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# ✅ Login Schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # Accepts "faculty" or "finance"

class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]

# ✅ Faculty Registration Schema
class RegisterFacultyRequest(BaseModel):
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r"^\d{10,15}$")  # ✅ Fixed `regex` → `pattern`
    password: str = Field(..., min_length=8, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    role: Optional[UserRole] = UserRole.FACULTY  # Defaults to faculty if not provided
    status: Optional[FacultyStatus] = FacultyStatus.ACTIVE  # ✅ Default to active

    @validator("email")
    def validate_allowed_emails(cls, value):
        allowed_domains = ["@loyalistcollege.com", "@tbcollege.com"]  # ✅ Allowed domains
        if not any(value.endswith(domain) for domain in allowed_domains):
            raise ValueError(f"Only emails ending with {', '.join(allowed_domains)} are allowed.")
        return value

    @validator("password")
    def validate_password(cls, value):
        import re
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[\W_])[A-Za-z\d\W_]{8,50}$"
        if not re.match(pattern, value):
            raise ValueError("Password must contain at least one letter, one number, and one special character (@$!%*?&).")
        return value

# ✅ Faculty Response Schema (with login details & status)
class FacultyResponse(BaseModel):
    id: str  # Convert MongoDB ObjectId to string
    email: EmailStr
    phone_number: str  # ✅ Added phone number
    first_name: str
    last_name: str
    role: UserRole
    status: FacultyStatus  # ✅ Faculty status
    is_logged_in: bool  # ✅ Track login status
    last_login: Optional[datetime] = None  # ✅ Track last login
    login_history: Optional[List[Dict[str, Any]]] = []  # ✅ Store login attempts
    created_at: datetime

# ✅ Faculty Registration Response Schema
class RegisterFacultyResponse(BaseModel):
    message: str  # ✅ Success message
    user: FacultyResponse  # ✅ Nested user object

# ✅ Faculty Update Schema (For Faculty Self-Update)
class UpdateFacultyRequest(BaseModel):
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15, pattern=r"^\d{10,15}$")  # ✅ Fixed regex issue
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    old_password: Optional[str] = None  # Required for password update
    password: Optional[str] = Field(None, min_length=8, max_length=50)

    @validator("password")
    def validate_password(cls, value):
        import re
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[\W_])[A-Za-z\d\W_]{8,50}$"
        if value and not re.match(pattern, value):
            raise ValueError("Password must contain at least one letter, one number, and one special character.")
        return value

# ✅ Finance Update Faculty Schema (Supports Role & Status)
class UpdateFacultyByFinanceRequest(BaseModel):
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15, pattern=r"^\d{10,15}$")  # ✅ Fixed regex issue
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=50)
    role: Optional[UserRole] = None  # ✅ Finance can update role
    status: Optional[FacultyStatus] = None  # ✅ Finance can update status

    @validator("role")
    def validate_role(cls, value):
        if value and value not in [UserRole.FACULTY, UserRole.FINANCE]:
            raise ValueError("Invalid role. Allowed values: 'faculty' or 'finance'.")
        return value

    @validator("status")
    def validate_status(cls, value):
        if value and value not in [FacultyStatus.ACTIVE, FacultyStatus.INACTIVE]:
            raise ValueError("Invalid status. Allowed values: 'active' or 'inactive'.")
        return value

    @validator("password")
    def validate_password(cls, value):
        import re
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[\W_])[A-Za-z\d\W_]{8,50}$"
        if value and not re.match(pattern, value):
            raise ValueError("Password must contain at least one letter, one number, and one special character.")
        return value
