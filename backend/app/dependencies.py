from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.config import settings
from app.database import get_database
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_database)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception

        user = await db.users.find_one({"email": email})
        if user is None:
            raise credentials_exception

        # ✅ Ensure "id" is a string, not ObjectId
        return {
            "id": str(user["_id"]),  # 🔥 Convert ObjectId to string
            "email": user["email"],
            "role": user["role"],
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
        }

    except JWTError:
        raise credentials_exception
