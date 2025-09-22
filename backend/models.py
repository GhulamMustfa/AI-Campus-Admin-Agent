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



class ChatRequest(BaseModel):
    user_id: str = None
    message: str

class ThreadCreate(BaseModel):
    user_id: str
    thread_id: str
