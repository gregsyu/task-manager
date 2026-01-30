from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr]
    password: str = Field(..., min_length=8, max_length=72)
    full_name: Optional[str]

class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr]
    full_name: Optional[str]
    # is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# class UserPasswordChange(BaseModel):
#     current_password: str
#     new_password: str = Field(..., min_length=8)
