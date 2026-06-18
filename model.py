from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginUser(BaseModel):
    email: EmailStr
    password: str

class RegisterUser(BaseModel):
    email: EmailStr
    password: str
    name:str

class CategoryCreate(BaseModel):
    name: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None