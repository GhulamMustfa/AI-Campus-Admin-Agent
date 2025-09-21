from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from backend.tools import (
    get_total_students, get_students_by_department, 
    get_recent_onboarded_students, get_active_students_last_7_days
)

logger = logging.getLogger(__name__)
analytics_router = APIRouter()

@analytics_router.get("/analytics")
async def get_analytics():
    """
    Get comprehensive campus analytics
    Returns: JSON with statistics and charts data
    """
    try:
        logger.info("Fetching campus analytics")
        
        # Get all analytics data
        total_students = await get_total_students()
        students_by_dept = await get_students_by_department()
        recent_students = await get_recent_onboarded_students(limit=5)
        active_students = await get_active_students_last_7_days()
        
        # Format department data for charts
        department_chart_data = [
            {"department": dept, "count": count} 
            for dept, count in students_by_dept.items()
        ]
        
        # Format recent students data
        recent_students_data = []
        for student in recent_students:
            if isinstance(student, dict):
                recent_students_data.append({
                    "name": student.get("name", "Unknown"),
                    "student_id": student.get("student_id", "Unknown"),
                    "department": student.get("department", "Unknown"),
                    "created_at": student.get("created_at", "Unknown")
                })
        
        analytics_data = {
            "overview": {
                "total_students": total_students,
                "active_students_7_days": active_students,
                "departments_count": len(students_by_dept)
            },
            "students_by_department": {
                "data": department_chart_data,
                "total": sum(students_by_dept.values()) if students_by_dept else 0
            },
            "recent_enrollments": {
                "students": recent_students_data,
                "count": len(recent_students_data)
            },
            "department_breakdown": students_by_dept
        }
        
        logger.info(f"Analytics generated: {total_students} total students")
        return analytics_data
        
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")

@analytics_router.get("/analytics/summary")
async def get_analytics_summary():
    """
    Get a quick summary of campus statistics
    """
    try:
        total_students = await get_total_students()
        students_by_dept = await get_students_by_department()
        
        return {
            "total_students": total_students,
            "departments": len(students_by_dept),
            "top_department": max(students_by_dept.items(), key=lambda x: x[1])[0] if students_by_dept else "None"
        }
        
    except Exception as e:
        logger.error(f"Analytics summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@analytics_router.get("/analytics/departments")
async def get_department_analytics():
    """
    Get detailed department analytics
    """
    try:
        students_by_dept = await get_students_by_department()
        
        # Calculate percentages
        total = sum(students_by_dept.values()) if students_by_dept else 0
        
        department_data = []
        for dept, count in students_by_dept.items():
            percentage = (count / total * 100) if total > 0 else 0
            department_data.append({
                "department": dept,
                "count": count,
                "percentage": round(percentage, 2)
            })
        
        # Sort by count descending
        department_data.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "departments": department_data,
            "total_students": total,
            "department_count": len(department_data)
        }
        
    except Exception as e:
        logger.error(f"Department analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate department analytics: {str(e)}")

@analytics_router.get("/analytics/recent")
async def get_recent_analytics(limit: int = 10):
    """
    Get recent student enrollments
    """
    try:
        if limit > 50:  # Prevent excessive data requests
            limit = 50
            
        recent_students = await get_recent_onboarded_students(limit=limit)
        
        return {
            "recent_students": recent_students,
            "count": len(recent_students),
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Recent analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recent analytics: {str(e)}")
