from pydantic import BaseModel, EmailStr
from typing import Optional

class AuthRequest(BaseModel):
    email: str
    password: str
    name: str = None 

class Student(BaseModel):
    name: str
    student_id: str
    department: str
    email: EmailStr

class UpdateStudent(BaseModel):
    field: str
    new_value: str



class ChatMessage(BaseModel):
    message: str
    user_id: str

class ThreadCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ThreadUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
