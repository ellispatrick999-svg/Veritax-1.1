from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from uuid import uuid4
from datetime import datetime

# -----------------------------------
# App Initialization
# -----------------------------------

app = FastAPI(
    title="User Profile API",
    version="1.0.0",
    description="User profiles for tax and filing systems"
)

# -----------------------------------
# In-Memory Store (replace with DB)
# -----------------------------------

USER_STORE: Dict[str, dict] = {}

# -----------------------------------
# Models
# -----------------------------------

class UserCreateRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    country: str = "US"
    tax_residency: str = "US"

class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    tax_residency: Optional[str] = None
    preferences: Optional[Dict[str, str]] = None

class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    first_name: str
    last_name: str
    country: str
    tax_residency: str
    preferences: Dict[str, str]
    created_at: datetime
    updated_at: datetime

# -----------------------------------
# Helpers
# -----------------------------------

def get_user_or_404(user_id: str) -> dict:
    user = USER_STORE.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user

# -----------------------------------
# Endpoints
# -----------------------------------

@app.post("/users", response_model=UserProfile)
def create_user(payload: UserCreateRequest):
    user_id = str(uuid4())
    now = datetime.utcnow()

    user = {
        "user_id": user_id,
        "email": payload.email,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "country": payload.country,
        "tax_residency": payload.tax_residency,
        "preferences": {},
        "created_at": now,
        "updated_at": now,
    }

    USER_STORE[user_id] = user
    return user

@app.get("/users/{user_id}", response_model=UserProfile)
def get_user(user_id: str):
    return get_user_or_404(user_id)

@app.put("/users/{user_id}", response_model=UserProfile)
def update_user(user_id: str, payload: UserUpdateRequest):
    user = get_user_or_404(user_id)

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "preferences" and value:
            user["preferences"].update(value)
        else:
            user[field] = value

    user["updated_at"] = datetime.utcnow()
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    get_user_or_404(user_id)
    del USER_STORE[user_id]
    return {"status": "deleted"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
