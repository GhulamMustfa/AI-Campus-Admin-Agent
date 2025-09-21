from fastapi import APIRouter, HTTPException
from backend.tools import (
    get_total_students, get_students_by_department, 
    get_recent_onboarded_students, get_active_students_last_7_days
)

routers = APIRouter(tags=["Analytics"])


@routers.get("/analytics")
async def get_analytics():
    try:
        total_students = await get_total_students()
        students_by_dept = await get_students_by_department()
        recent_students = await get_recent_onboarded_students(limit=5)
        active_students = await get_active_students_last_7_days()

        return {
            "total_students": total_students,
            "students_by_department": students_by_dept,
            "recent_students": recent_students,
            "active_students_7_days": active_students
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@routers.get("/analytics/summary")
async def get_analytics_summary():
    try:
        total_students = await get_total_students()
        students_by_dept = await get_students_by_department()
        
        return {
            "total_students": total_students,
            "departments": len(students_by_dept),
            "top_department": max(students_by_dept.items(), key=lambda x: x[1])[0] if students_by_dept else "None"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
