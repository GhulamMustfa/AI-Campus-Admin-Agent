# backend/agent.py
import os
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner
from .tools import *

# ----------------- OpenAI Client -----------------
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# ----------------- Agent Setup -----------------
agent = Agent(
    name="Campus Admin Agent",
    instructions="""
    You are the Campus Admin assistant. When asked about students, events, or any data, 
    ALWAYS use the appropriate tools to get the actual data from the database.
    For example:
    - When asked to "list students" or "show students", use list_students_tool
    - When asked about student count, use get_total_students_tool
    - When asked about a specific student, use get_student_tool
    Always provide the actual data, not just acknowledgments.
    """,
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    tools=[
        add_student_tool, get_student_tool, update_student_tool, delete_student_tool, list_students_tool,
        get_total_students_tool, get_students_by_department_tool, get_recent_onboarded_students_tool,
        get_active_students_last_7_days_tool, add_event_tool, update_event_tool, delete_event_tool, list_events_tool,
        send_email_tool
    ],
)

# ----------------- Run / Stream Functions -----------------
async def run_agent(message: str, context=None) -> str:
    """Run agent with optional context/memory"""
    runner = Runner()
    result = await runner.run(agent, message)
    return result.final_output.strip()

async def stream_agent(message: str, context=None):
    """Stream agent output as tokens"""
    runner = Runner()
    result = await runner.run(agent, message)
    yield result.final_output