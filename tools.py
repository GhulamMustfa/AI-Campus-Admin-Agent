import datetime
from db import db, fix_id

async def add_student(name, student_id, department, email):
    doc = {"name": name, "student_id": student_id,
           "department": department, "email": email,
           "created_at": datetime.datetime.utcnow()}
    await db.students.insert_one(doc)
    return "Student added."

async def get_student(student_id):
    s = await db.students.find_one({"student_id": student_id})
    return fix_id(s) if s else "Not found."

async def update_student(student_id, field, new_value):
    await db.students.update_one({"student_id": student_id},
                                 {"$set": {field: new_value}})
    return "Updated."

async def delete_student(student_id):
    await db.students.delete_one({"student_id": student_id})
    return "Deleted."

async def list_students():
    cur = db.students.find()
    return [fix_id(s) async for s in cur]

async def get_total_students():
    return await db.students.count_documents({})

async def get_students_by_department():
    pipeline = [{"$group": {"_id": "$department", "count": {"$sum": 1}}}]
    data = await db.students.aggregate(pipeline).to_list(None)
    return {d["_id"]: d["count"] for d in data}

async def get_recent_onboarded_students(limit=5):
    cur = db.students.find().sort("created_at", -1).limit(limit)
    return [fix_id(s) async for s in cur]

async def get_active_students_last_7_days():
    return 7  # mock activity

async def send_email(student_id, message):
    return f"Email to {student_id}: {message}"
