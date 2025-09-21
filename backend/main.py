from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import asyncio
import re

from backend.agent import run_agent_with_tools
from backend.student_router import router
from backend.analytics_router import routers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Campus Admin Agent", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default_user"

@app.get("/")
def root():
    return {"message": "AI Campus Admin Agent Server", "status": "running"}

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        response, tools_used = await run_agent_with_tools(msg.message, msg.user_id)
        return {"response": response, "tools_used": tools_used}
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(msg: ChatMessage):
    async def event_stream():
        try:
            response, _ = await run_agent_with_tools(msg.message, msg.user_id)
            yield f"data: {response}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

app.include_router(router)
app.include_router(routers)
