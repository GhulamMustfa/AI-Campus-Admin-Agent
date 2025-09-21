from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models import Student, UpdateStudent
from db import db, fix_id
from agent import ask_model, stream_chat

router = APIRouter()

# ---- Chat Endpoints ----
@router.post("/chat")
async def chat(payload: dict):
    """
    Normal chat endpoint
    Payload: {"message": "Hello"}
    """
    msg = payload.get("message", "")
    if not msg:
        raise HTTPException(status_code=400, detail="Message is required")
    reply = await ask_model([{"role": "user", "content": msg}])
    return {"response": reply}

@router.post("/chat/stream")
async def chat_stream(payload: dict):
    """
    Streaming chat endpoint (SSE)
    Payload: {"message": "Hello"}
    """
    msg = payload.get("message", "")
    if not msg:
        raise HTTPException(status_code=400, detail="Message is required")

    def event_stream():
        for token in stream_chat([{"role": "user", "content": msg}]):
            yield token

    return StreamingResponse(event_stream(), media_type="text/event-stream")

# ---- Student CRUD ----
@router.post("/students")
async def create_student(s: Student):
    await db.students.insert_one(s.model_dump())
    return {"message": "Student created"}

@router.get("/students/{sid}")
async def read_student(sid: str):
    s = await db.students.find_one({"student_id": sid})
    if not s: raise HTTPException(404, "Not found")
    return fix_id(s)

@router.patch("/students/{sid}")
async def update_student_route(sid: str, upd: UpdateStudent):
    await db.students.update_one({"student_id": sid},
                                 {"$set": {upd.field: upd.new_value}})
    return {"message": "Updated"}

@router.delete("/students/{sid}")
async def delete_student_route(sid: str):
    await db.students.delete_one({"student_id": sid})
    return {"message": "Deleted"}

@router.get("/students")
async def list_students_route():
    cur = db.students.find()
    return [fix_id(s) async for s in cur]

# ---- Analytics ----
@router.get("/analytics")
async def analytics():
    total = await db.students.count_documents({})
    by_dept = await db.students.aggregate([
        {"$group": {"_id": "$department", "count": {"$sum": 1}}}
    ]).to_list(None)
    return {"total_students": total,
            "by_department": {d["_id"]: d["count"] for d in by_dept}}
