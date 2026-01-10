from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Dict
from uuid import uuid4

from passlib.context import CryptContext
import jwt

# -----------------------------------
# App Initialization
# -----------------------------------

app = FastAPI(
    title="Authentication API",
    version="1.0.0",
    description="Secure authentication for tax platform"
)

# -----------------------------------
# Security Configuration
# -----------------------------------

SECRET_KEY = "CHANGE_THIS_TO_A_SECURE_RANDOM_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# -----------------------------------
# In-Memory User Credential Store
# (Replace with database)
# -----------------------------------

AUTH_USERS: Dict[str, dict] = {}

# -----------------------------------
# Models
# -----------------------------------

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class AuthUser(BaseModel):
    user_id: str
    email: EmailStr
    created_at: datetime

# -----------------------------------
# Password Utilities
# -----------------------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# -----------------------------------
# JWT Utilities
# -----------------------------------

def create_access_token(user_id: str, email: str) -> dict:
    expires_at = datetime.utcnow() + time_
