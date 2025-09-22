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

      In streaming conversations, you should remember facts mentioned by the user
    within the current conversation, such as names, preferences, or other details,
    and use them in later responses. Do NOT store anything in the database
    for these remembered facts.
    """,
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    tools=[
        add_student_tool, get_student_tool, update_student_tool, delete_student_tool, list_students_tool,
        get_total_students_tool, get_students_by_department_tool, get_recent_onboarded_students_tool,
        get_active_students_last_7_days_tool, add_event_tool, update_event_tool, delete_event_tool, list_events_tool,
        send_email_tool
    ],
)

# ----------------- Conversation Memory -----------------
conversation_memory = {}

# ----------------- Normal chat - no memory -----------------
async def run_agent(message: str):
    runner = Runner()
    result = await runner.run(agent, message)
    return result.final_output.strip()

# ----------------- Streaming chat - with memory per user -----------------
async def stream_agent(message: str, user_id: str, thread_id: str):
    # Initialize memory for user if not exists
    if user_id not in conversation_memory:
        conversation_memory[user_id] = {}

    # Initialize memory for thread if not exists
    if thread_id not in conversation_memory[user_id]:
        conversation_memory[user_id][thread_id] = []

    # Append user message to memory
    conversation_memory[user_id][thread_id].append({"role": "user", "content": message})

    # Build conversation text
    context_messages = conversation_memory[user_id][thread_id]
    conversation_text = "\n".join([f"{m['role']}: {m['content']}" for m in context_messages])

    # Run agent
    runner = Runner()
    result = await runner.run(agent, conversation_text)

    # Save assistant reply
    conversation_memory[user_id][thread_id].append({"role": "assistant", "content": result.final_output})

    yield result.final_output
