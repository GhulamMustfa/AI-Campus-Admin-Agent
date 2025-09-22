from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from backend.models import Student, UpdateStudent
from backend.tools import add_student, get_student, update_student, delete_student, list_students

router = APIRouter(tags=["Students"])


@router.post("/students")
def create_student(student: Student):
    try:
        result = add_student(student.name, student.student_id, student.department, student.email)
        return {"message": "Student created successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}")
def get_student_by_id(student_id: str):
    try:
        result = get_student(student_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/students/{student_id}")
def update_student_by_id(student_id: str, update: UpdateStudent):
    try:
        result = update_student(student_id, update.field, update.new_value)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/students/{student_id}")
def delete_student_by_id(student_id: str):
    try:
        result = delete_student(student_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students")
def list_all_students():
    try:
        students = list_students()
        return {"students": students, "count": len(students)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
