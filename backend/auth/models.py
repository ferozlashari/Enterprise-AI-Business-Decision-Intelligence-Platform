from pydantic import BaseModel, EmailStr
from typing import Optional


# ==========================
# User Registration Schema
# ==========================

class UserCreate(BaseModel):

    username: str

    email: EmailStr

    password: str

    role: Optional[str] = "Analyst"



# ==========================
# Login Schema
# ==========================

class UserLogin(BaseModel):

    username: str

    password: str



# ==========================
# Token Response
# ==========================

class TokenResponse(BaseModel):

    access_token: str

    token_type: str



# ==========================
# User Response
# ==========================

class UserResponse(BaseModel):

    username: str

    email: EmailStr

    role: str


    class Config:

        from_attributes = True