from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from backend.tools import add_student, get_student, update_student, delete_student, list_students

router = APIRouter(tags=["Students"])

class Student(BaseModel):
    name: str
    student_id: str
    department: str
    email: EmailStr

class UpdateStudent(BaseModel):
    field: str
    new_value: str


@router.post("/students")
async def create_student(student: Student):
    try:
        result = await add_student(student.name, student.student_id, student.department, student.email)
        return {"message": "Student created successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}")
async def get_student_by_id(student_id: str):
    try:
        result = await get_student(student_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/students/{student_id}")
async def update_student_by_id(student_id: str, update: UpdateStudent):
    try:
        result = await update_student(student_id, update.field, update.new_value)
        if "not found" in result.lower():
            raise HTTPException(status_code=404, detail=result)
        return {"message": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/students/{student_id}")
async def delete_student_by_id(student_id: str):
    try:
        result = await delete_student(student_id)
        if "not found" in result.lower():
            raise HTTPException(status_code=404, detail=result)
        return {"message": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students")
async def list_all_students():
    try:
        students = await list_students()
        return {"students": students, "count": len(students)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
