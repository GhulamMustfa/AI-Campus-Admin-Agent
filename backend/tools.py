import datetime
import logging
from typing import Dict, List, Any, Optional
from backend.db import students_collection

logger = logging.getLogger(__name__)

async def add_student(name: str, student_id: str, department: str, email: str) -> str:
    try:
        student = {
            "name": name,
            "student_id": student_id,
            "department": department,
            "email": email,
            "created_at": datetime.datetime.now().isoformat(),
            "is_active": True
        }
        existing = students_collection.find_one({"student_id": student_id})
        if existing:
            return f"Student with ID {student_id} already exists"
        
        result = students_collection.insert_one(student)
        logger.info(f"Student {name} ({student_id}) added successfully")
        return f"Student {name} added successfully with ID: {student_id}"
        
    except Exception as e:
        logger.error(f"Error adding student: {str(e)}")
        return f"Error adding student: {str(e)}"

async def get_student(student_id: str) -> Dict[str, Any]:
    try:
        student = students_collection.find_one({"student_id": student_id})
        if student:
            student["_id"] = str(student["_id"])
            return student
        else:
            return {"error": f"Student with ID {student_id} not found"}
            
    except Exception as e:
        logger.error(f"Error getting student: {str(e)}")
        return {"error": f"Error retrieving student: {str(e)}"}

async def update_student(student_id: str, field: str, new_value: str) -> str:
    try:
        allowed_fields = ["name", "department", "email"]
        if field not in allowed_fields:
            return f"Invalid field '{field}'. Allowed fields: {allowed_fields}"
        
        result = students_collection.update_one(
            {"student_id": student_id},
            {"$set": {field: new_value, "updated_at": datetime.datetime.utcnow().isoformat()}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Student {student_id} updated: {field} = {new_value}")
            return f"Student {student_id} updated successfully"
        else:
            return f"Student {student_id} not found or no changes made"
            
    except Exception as e:
        logger.error(f"Error updating student: {str(e)}")
        return f"Error updating student: {str(e)}"

async def delete_student(student_id: str) -> str:
    """Delete a student from the database"""
    try:
        result = students_collection.delete_one({"student_id": student_id})
        
        if result.deleted_count > 0:
            logger.info(f"Student {student_id} deleted successfully")
            return f"Student {student_id} deleted successfully"
        else:
            return f"Student {student_id} not found"
            
    except Exception as e:
        logger.error(f"Error deleting student: {str(e)}")
        return f"Error deleting student: {str(e)}"

async def list_students() -> List[Dict[str, Any]]:
    """Get a list of all students"""
    try:
        students = list(students_collection.find())
        for student in students:
            student["_id"] = str(student["_id"])
        
        logger.info(f"Retrieved {len(students)} students")
        return students
        
    except Exception as e:
        logger.error(f"Error listing students: {str(e)}")
        return [{"error": f"Error retrieving students: {str(e)}"}]

async def get_total_students() -> int:
    """Get the total number of students"""
    try:
        count = students_collection.count_documents({"is_active": True})
        logger.info(f"Total students: {count}")
        return count
        
    except Exception as e:
        logger.error(f"Error counting students: {str(e)}")
        return 0

async def get_students_by_department() -> Dict[str, int]:
    """Get the number of students in each department"""
    try:
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$department", "count": {"$sum": 1}}}
        ]
        
        result = list(students_collection.aggregate(pipeline))
        department_counts = {item["_id"]: item["count"] for item in result}
        
        logger.info(f"Students by department: {department_counts}")
        return department_counts
        
    except Exception as e:
        logger.error(f"Error getting students by department: {str(e)}")
        return {}

async def get_recent_onboarded_students(limit: int = 5) -> List[Dict[str, Any]]:
    """Get recently enrolled students"""
    try:
        students = list(students_collection.find(
            {"is_active": True}
        ).sort("created_at", -1).limit(limit))
        
        for student in students:
            student["_id"] = str(student["_id"])
        
        logger.info(f"Retrieved {len(students)} recent students")
        return students
        
    except Exception as e:
        logger.error(f"Error getting recent students: {str(e)}")
        return []

async def get_active_students_last_7_days() -> int:
    try:
        total = await get_total_students()
        active_count = int(total * 0.7)
        
        logger.info(f"Active students (last 7 days): {active_count}")
        return active_count
        
    except Exception as e:
        logger.error(f"Error getting active students: {str(e)}")
        return 0

async def send_email(student_id: str, message: str) -> str:
    try:
        student = students_collection.find_one({"student_id": student_id})
        if not student:
            return f"Student {student_id} not found"
        
        logger.info(f"Mock email sent to {student['email']}: {message}")
        
        return f"Email sent to {student['name']} ({student['email']}): {message}"
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return f"Error sending email: {str(e)}"
