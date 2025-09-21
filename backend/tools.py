import os
import datetime
import pymongo
from typing import Dict, Any, List
from agents import function_tool
from backend.db import students_collection, admins_collection, get_db

# ----------------- Student Functions -----------------
def add_student(name: str, student_id: int, department: str, email: str) -> Dict[str, Any]:
    email = email.lower().strip()
    if students_collection.find_one({"email": email}):
        return {"error": f"Student with email {email} already exists"}
    student = {
        "name": name,
        "student_id": student_id,
        "department": department,
        "email": email,
        "created_at": datetime.datetime.utcnow()
    }
    result = students_collection.insert_one(student)
    student["_id"] = str(result.inserted_id)
    return {"message": "Student added successfully", "student": student}

def get_student(identifier: str) -> Dict[str, Any]:
    identifier = identifier.strip()
    student = students_collection.find_one({"email": identifier.lower()}) \
              or students_collection.find_one({"student_id": identifier})
    if student:
        student["_id"] = str(student["_id"])
        return student
    try:
        sid = int(identifier)
        student = students_collection.find_one({"student_id": sid})
        if student:
            student["_id"] = str(student["_id"])
            return student
    except Exception:
        pass
    return {"error": "Student not found"}

def update_student(identifier: str, field: str, new_value: str) -> Dict[str, Any]:
    identifier = identifier.strip()
    if field not in ["name", "department", "email", "student_id"]:
        return {"error": "Invalid field"}
    query = {"email": identifier.lower()} if field != "student_id" else {"student_id": identifier}
    if field == "email":
        new_value = new_value.lower().strip()
    result = students_collection.update_one(query, {"$set": {field: new_value}})
    if result.matched_count:
        updated_student = students_collection.find_one(query)
        updated_student["_id"] = str(updated_student["_id"])
        return {"message": "Student updated successfully", "student": updated_student}
    return {"error": "Student not found"}

def delete_student(identifier: str) -> Dict[str, Any]:
    identifier = identifier.strip()
    query = {"email": identifier.lower()} if "@" in identifier else {"student_id": identifier}
    result = students_collection.delete_one(query)
    if result.deleted_count:
        return {"message": "Student deleted successfully"}
    try:
        sid = int(identifier)
        result = students_collection.delete_one({"student_id": sid})
        if result.deleted_count:
            return {"message": "Student deleted successfully"}
    except Exception:
        pass
    return {"error": "Student not found"}

def list_students() -> Dict[str, Any]:
    result = list(students_collection.find().sort("created_at", -1))
    for s in result:
        s["_id"] = str(s["_id"])
    return {"students": result}

# ----------------- Analytics Functions -----------------
def get_total_students() -> Dict[str, Any]:
    return {"total_students": students_collection.count_documents({})}

def get_students_by_department() -> Dict[str, Any]:
    pipeline = [{"$group": {"_id": "$department", "count": {"$sum": 1}}}]
    return {"students_by_department": list(students_collection.aggregate(pipeline))}

def get_recent_onboarded_students(limit: int = 5) -> Dict[str, Any]:
    limit = int(limit)
    cursor = students_collection.find().sort("created_at", -1).limit(limit)
    out = []
    for s in cursor:
        s["_id"] = str(s["_id"])
        out.append(s)
    return {"recent_students": out}

def get_active_students_last_7_days() -> Dict[str, Any]:
    cursor = students_collection.find().limit(3)
    out = []
    for s in cursor:
        s["_id"] = str(s["_id"])
        out.append(s)
    return {"active_last_7_days": out}

# ----------------- Event Functions -----------------
def add_event(name: str, date: str, location: str):
    event = {"name": name, "date": date, "location": location}
    result = get_db.insert_one(event)
    event["_id"] = str(result.inserted_id)
    return {"message": "Event added", "event": event}

def update_event(event_id: str, name: str = None, date: str = None, location: str = None):
    update_fields = {k: v for k, v in (("name", name), ("date", date), ("location", location)) if v}
    result = get_db.update_one({"_id": pymongo.ObjectId(event_id)}, {"$set": update_fields})
    if result.matched_count:
        updated_event = get_db.find_one({"_id": pymongo.ObjectId(event_id)})
        updated_event["_id"] = str(updated_event["_id"])
        return {"message": "Event updated", "event": updated_event}
    return {"error": "Event not found"}

def delete_event(event_id: str):
    result = get_db.delete_one({"_id": pymongo.ObjectId(event_id)})
    if result.deleted_count:
        return {"message": "Event deleted", "event_id": event_id}
    return {"error": "Event not found"}

def list_events():
    events = list(get_db.find())
    for event in events:
        event["_id"] = str(event["_id"])
    return {"events": events}

# ----------------- Email -----------------
def send_email(student_identifier: str, message: str) -> Dict[str, Any]:
    student_identifier = student_identifier.strip()
    student = students_collection.find_one({"email": student_identifier.lower()})
    if not student:
        try:
            sid = int(student_identifier)
            student = students_collection.find_one({"student_id": sid})
        except Exception:
            pass
    if not student:
        return {"error": "Student not found"}
    print(f"[EMAIL MOCK] to={student['email']} message={message}")
    return {"message": f"Email mock sent to {student['email']}"}

# ----------------- Wrap with function_tool -----------------
add_student_tool = function_tool(add_student)
get_student_tool = function_tool(get_student)
update_student_tool = function_tool(update_student)
delete_student_tool = function_tool(delete_student)
list_students_tool = function_tool(list_students)

get_total_students_tool = function_tool(get_total_students)
get_students_by_department_tool = function_tool(get_students_by_department)
get_recent_onboarded_students_tool = function_tool(get_recent_onboarded_students)
get_active_students_last_7_days_tool = function_tool(get_active_students_last_7_days)

add_event_tool = function_tool(add_event)
update_event_tool = function_tool(update_event)
delete_event_tool = function_tool(delete_event)
list_events_tool = function_tool(list_events)

send_email_tool = function_tool(send_email)
