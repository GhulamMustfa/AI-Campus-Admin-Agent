# routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.agent import run_agent, stream_agent

router = APIRouter(tags=["Chat"])

# Request model
class ChatRequest(BaseModel):
    user_id: str = None  # optional for /chat
    message: str

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

# Streaming chat - with memory
@router.post("/chat/stream")
async def chat_stream(msg: ChatRequest):
    async def event_generator():
        try:
            async for chunk in stream_agent(msg.message, user_id=msg.user_id):
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
