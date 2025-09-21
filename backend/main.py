from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import time
import asyncio
from typing import Dict, Any

# Import our modules
from backend.agent import run_agent_with_tools
from backend.student_router import router
from backend.analytics_router import analytics_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Campus Admin Agent",
    description="AI-powered campus administration with streaming responses",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    tools_used: list = []

@app.get("/")
def root():
    return {
        "message": "AI Campus Admin Agent Server",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/chat", response_model=ChatResponse)
async def chat(msg: ChatMessage):
    try:
        logger.info(f"Chat request from user {msg.user_id}: {msg.message[:50]}...")
        response, tools_used = await run_agent_with_tools(msg.message, msg.user_id)
        return ChatResponse(response=response, tools_used=tools_used)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(msg: ChatMessage):
    async def event_stream():
        try:
            logger.info(f"Streaming chat request from user {msg.user_id}")
            
            response, _ = await run_agent_with_tools(msg.message, msg.user_id)
            
            for char in response:
                yield f"data: {char}\n\n"
                await asyncio.sleep(0.01)
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

app.include_router(router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return {"error": "Internal server error", "detail": str(exc)}
