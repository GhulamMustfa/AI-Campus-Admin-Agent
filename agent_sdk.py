# agent_sdk.py

import os
import openai
from openai import Tool, Agent
from openai import HumanMessage, AIMessage, SystemMessage
from db import conversations
from tools import (
    add_student, get_student, update_student, delete_student, list_students,
    get_total_students, get_students_by_department, get_recent_onboarded_students,
    get_active_students_last_7_days, get_cafeteria_timings, get_library_hours,
    get_event_schedule, send_email
)
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Define tools in OpenAI Agent SDK style
tools = [
    Tool(
        name="add_student",
        func=add_student,
        description="Add a new student to the system",
        args_schema={"name": str, "student_id": str, "department": str, "email": str}
    ),
    Tool(
        name="get_student",
        func=get_student,
        description="Get student by ID",
        args_schema={"student_id": str}
    ),
    Tool(
        name="update_student",
        func=update_student,
        description="Update student's field",
        args_schema={"student_id": str, "field": str, "new_value": str}
    ),
    Tool(
        name="delete_student",
        func=delete_student,
        description="Delete a student",
        args_schema={"student_id": str}
    ),
    Tool(
        name="list_students",
        func=lambda: list_students(),
        description="List all students",
        args_schema={}
    ),
    Tool(
        name="get_total_students",
        func=lambda: get_total_students(),
        description="Get total number of students",
        args_schema={}
    ),
    Tool(
        name="get_students_by_department",
        func=lambda: get_students_by_department(),
        description="Get breakdown of students by department",
        args_schema={}
    ),
    Tool(
        name="get_recent_onboarded_students",
        func=get_recent_onboarded_students,
        description="Get recent onboarded students",
        args_schema={"limit": int}
    ),
    Tool(
        name="get_active_students_last_7_days",
        func=lambda: get_active_students_last_7_days(),
        description="Get students active in last 7 days",
        args_schema={}
    ),
    Tool(
        name="get_cafeteria_timings",
        func=lambda: get_cafeteria_timings(),
        description="Get cafeteria timings",
        args_schema={}
    ),
    Tool(
        name="get_library_hours",
        func=lambda: get_library_hours(),
        description="Get library hours",
        args_schema={}
    ),
    Tool(
        name="get_event_schedule",
        func=lambda: get_event_schedule(),
        description="Get event schedule",
        args_schema={}
    ),
    Tool(
        name="send_email",
        func=send_email,
        description="Send mock email to a student",
        args_schema={"student_id": str, "message": str}
    )
]

def save_message(conversation_id, role, content):
    conversations.update_one(
        {"conversation_id": conversation_id},
        {"$push": {"messages": {"role": role, "content": content, "ts": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}}},
        upsert=True
    )

def get_conversation_messages(conversation_id):
    doc = conversations.find_one({"conversation_id": conversation_id})
    if not doc:
        return []
    return doc.get("messages", [])

async def run_agent(conversation_id: str, user_message: str, stream: bool = False):
    # Load memory
    history = get_conversation_messages(conversation_id)
    messages = []
    if history:
        for m in history:
            messages.append({"role": m["role"], "content": m["content"]})
    # Append latest user message
    messages.append({"role": "user", "content": user_message})
    # Save user message
    save_message(conversation_id, "user", user_message)

    agent = Agent.from_tools(tools=tools, llm=lambda *args, **kwargs: openai.ChatCompletion.create(model=MODEL, **kwargs))

    if stream:
        # stream token-level responses
        resp = await agent.arun(messages=messages, stream=True)
        # resp will be an async generator of tokens
        async for chunk in resp:
            # each chunk is e.g. {"choices":[{"delta": {"role": "assistant"/"content": ..., "content": ...}}]}
            yield chunk
        # after streaming, store assistant final message
        # build up final content
        # Note: depending on the agent SDK version, agent.arun may produce content chunks
        # We reconstruct final assistant message
        # For simplicity, after streaming completes, you might get the full message via agent.run (non-stream)
        # But since we have streamed, better to capture content as we go (below when using in main)
    else:
        result = agent.run(messages=messages)
        # agent.run returns assistant message (and may have included tool responses)
        assistant_message = result
        save_message(conversation_id, "assistant", assistant_message)
        return assistant_message
