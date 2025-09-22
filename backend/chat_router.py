from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import StreamingResponse
from backend.models import ThreadCreate, ChatRequest
from backend.agent import run_agent, stream_agent, conversation_memory
from backend.db import db
from datetime import datetime

router = APIRouter(tags=["Chat"])

# Normal chat - no memory
@router.post("/chat")
async def chat(msg: ChatRequest):
    if not msg.message:
        raise HTTPException(status_code=400, detail="message is required")
    try:
        response = await run_agent(msg.message)
        return {"response": response}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}


@router.post("/chat/stream/{thread_id}")
async def chat_stream(msg: ChatRequest, thread_id: str):
    # Check if thread exists in DB
    existing = db.threads.find_one({"user_id": msg.user_id, "thread_id": thread_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Thread not found")

    async def event_generator():
        try:
            async for chunk in stream_agent(msg.message, user_id=msg.user_id, thread_id=thread_id):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [STREAM ERROR] {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/threads/create")
def create_thread(thread: ThreadCreate):
    # Check if thread already exists
    existing = db.threads.find_one({"user_id": thread.user_id, "thread_id": thread.thread_id})
    if existing:
        raise HTTPException(status_code=400, detail="Thread already exists")

    # Insert thread into MongoDB
    db.threads.insert_one({
        "user_id": thread.user_id,
        "thread_id": thread.thread_id,
        "created_at": datetime.utcnow()
    })

    # Initialize in-memory conversation
    if thread.user_id not in conversation_memory:
        conversation_memory[thread.user_id] = {}
    conversation_memory[thread.user_id][thread.thread_id] = []

    return {"message": f"Thread {thread.thread_id} created for user {thread.user_id}"}


@router.delete("/threads/delete")
def delete_thread(user_id: str, thread_id: str):
    result = db.threads.delete_one({"user_id": user_id, "thread_id": thread_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Also remove in-memory conversation
    if user_id in conversation_memory and thread_id in conversation_memory[user_id]:
        del conversation_memory[user_id][thread_id]

    return {"message": f"Thread {thread_id} deleted for user {user_id}"}
