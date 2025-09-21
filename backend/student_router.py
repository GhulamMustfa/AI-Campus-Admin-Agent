from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Dict, Any
import logging
from backend.db import students_collection
from backend.tools import add_student, get_student, update_student, delete_student, list_students
from pydantic import BaseModel, EmailStr, validator

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class Student(BaseModel):
    name: str
    student_id: str
    department: str
    email: EmailStr
    
    @validator('student_id')
    def validate_student_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Student ID cannot be empty')
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v.strip()

class UpdateStudent(BaseModel):
    field: str
    new_value: str
    
    @validator('field')
    def validate_field(cls, v):
        allowed_fields = ['name', 'department', 'email']
        if v not in allowed_fields:
            raise ValueError(f'Field must be one of: {allowed_fields}')
        return v

# Create student
@router.post("/students")
async def create_student(student: Student):
    """Create a new student"""
    try:
        logger.info(f"Creating student: {student.name} ({student.student_id})")
        
        # Check if student already exists
        existing = students_collection.find_one({"student_id": student.student_id})
        if existing:
            raise HTTPException(status_code=400, detail=f"Student ID {student.student_id} already exists")

        # Use the tool function
        result = await add_student(student.name, student.student_id, student.department, student.email)
        
        return {
            "message": "Student created successfully",
            "student_id": student.student_id,
            "name": student.name,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating student: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create student: {str(e)}")

# Read student
@router.get("/students/{student_id}")
async def get_student_by_id(student_id: str):
    """Get student by ID"""
    try:
        logger.info(f"Getting student: {student_id}")
        
        result = await get_student(student_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get student: {str(e)}")

# Update student
@router.patch("/students/{student_id}")
async def update_student_by_id(student_id: str, update: UpdateStudent):
    """Update student information"""
    try:
        logger.info(f"Updating student {student_id}: {update.field} = {update.new_value}")
        
        result = await update_student(student_id, update.field, update.new_value)
        
        if "not found" in result.lower():
            raise HTTPException(status_code=404, detail=result)
        
        return {"message": result}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating student: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update student: {str(e)}")

# Delete student
@router.delete("/students/{student_id}")
async def delete_student_by_id(student_id: str):
    """Delete a student"""
    try:
        logger.info(f"Deleting student: {student_id}")
        
        result = await delete_student(student_id)
        
        if "not found" in result.lower():
            raise HTTPException(status_code=404, detail=result)
        
        return {"message": result}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting student: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete student: {str(e)}")

# List all students
@router.get("/students")
async def list_all_students():
    """Get all students"""
    try:
        logger.info("Listing all students")
        
        students = await list_students()
        
        return {
            "students": students,
            "count": len(students)
        }
        
    except Exception as e:
        logger.error(f"Error listing students: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list students: {str(e)}")
