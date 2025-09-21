from pydantic import BaseModel, EmailStr
from typing import Optional

class Student(BaseModel):
    name: str
    student_id: str
    department: str
    email: EmailStr

class UpdateStudent(BaseModel):
    field: str
    new_value: str
