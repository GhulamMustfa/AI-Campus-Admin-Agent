import os
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner
from .tools import *
from backend.rag_agent import get_thread_context

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

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

conversation_memory = {}

async def run_agent(message: str):
    runner = Runner()
    result = await runner.run(agent, message)
    return result.final_output.strip()


async def stream_agent(message: str, user_id: str, thread_id: str, pdf_content: str | None = None, save_permanently: bool = False):
    if user_id not in conversation_memory:
        conversation_memory[user_id] = {}
    if thread_id not in conversation_memory[user_id]:
        conversation_memory[user_id][thread_id] = {"messages": [], "pdf_context": ""}

    thread_memory = conversation_memory[user_id][thread_id]
    thread_memory["messages"].append({"role": "user", "content": message})

    if pdf_content:
        thread_memory["pdf_context"] = pdf_content

    context = get_thread_context(conversation_memory, user_id, thread_id)
    runner = Runner()

    final_prompt = f"""
    Use the following context to answer the question. If the question requires a tool,
    use the context to extract any necessary information for the tool's parameters.

    Context:
    {context}

    Question:
    {message}
    """

    result = await runner.run(agent, final_prompt)
    answer = result.final_output.strip()

    thread_memory["messages"].append({"role": "assistant", "content": answer})
    
    if save_permanently:
        from backend.db import db
        db.user_threads.update_one(
            {"user_id": user_id, "thread_id": thread_id},
            {"$set": {
                "messages": thread_memory["messages"],
                "pdf_context": thread_memory["pdf_context"]
            }},
            upsert=True
        )

    yield answer