import os
import json
import logging
import requests
from typing import List, Dict, Any, Tuple
import asyncio

from backend.tools import (
    add_student, get_student, update_student, delete_student, list_students,
    get_total_students, get_students_by_department, get_recent_onboarded_students,
    get_active_students_last_7_days, send_email
)

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

conversation_memory: Dict[str, List[Dict[str, str]]] = {}

TOOL_FUNCTIONS = {
    "add_student": add_student,
    "get_student": get_student,
    "update_student": update_student,
    "delete_student": delete_student,
    "list_students": list_students,
    "get_total_students": get_total_students,
    "get_students_by_department": get_students_by_department,
    "get_recent_onboarded_students": get_recent_onboarded_students,
    "get_active_students_last_7_days": get_active_students_last_7_days,
    "send_email": send_email
}

def get_conversation_context(user_id: str, max_turns: int = 10) -> List[Dict[str, str]]:
    history = conversation_memory.get(user_id, [])
    return history[-max_turns:] if len(history) > max_turns else history

def add_to_conversation(user_id: str, role: str, content: str):
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    conversation_memory[user_id].append({"role": role, "content": content})

async def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    try:
        if tool_name not in TOOL_FUNCTIONS:
            return f"Error: Tool '{tool_name}' not found"
        
        tool_func = TOOL_FUNCTIONS[tool_name]
        
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**arguments)
        else:
            result = tool_func(**arguments)
        
        return str(result)
        
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"

def call_gemini_api(messages: List[Dict[str, str]]) -> str:
    try:
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                continue
            elif msg["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
            elif msg["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
        
        system_prompt = """
    You are an AI Campus Admin Agent. You help manage student records and provide campus information.
    You have access to these tools:
    - list_students: Get all students
    - add_student: Add a new student (requires: name, student_id, department, email)
    - get_student: Get student by ID (requires: student_id)
    - update_student: Update student info (requires: student_id, field, new_value)
    - delete_student: Delete student (requires: student_id)
    - get_total_students: Get total count
    - get_students_by_department: Get department breakdown
    - get_recent_onboarded_students: Get recent students
    - get_active_students_last_7_days: Get active students count
    - send_email: Send email to student (requires: student_id, message)

    Tool calling format:
    - No parameters: [TOOL_CALL:tool_name:{}]
    - With parameters: [TOOL_CALL:tool_name:{"param": "value"}]

    Always call tools when needed, then provide a helpful response."""

        contents.insert(0, {"role": "user", "parts": [{"text": system_prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
        }

        response = requests.post(
            f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
        
        return "No response generated"
        
    except Exception as e:
        raise Exception(f"Gemini API error: {e}")

def parse_tool_calls(response_text: str) -> List[Tuple[str, Dict[str, Any]]]:
    import re
    tool_calls = []
    pattern_with_args = r'\[TOOL_CALL:(\w+):({[^}]+})\]'
    matches_with_args = re.findall(pattern_with_args, response_text)
    
    for tool_name, args_str in matches_with_args:
        try:
            args = json.loads(args_str)
            tool_calls.append((tool_name, args))
        except json.JSONDecodeError:
            pass
    
    pattern_no_args = r'\[TOOL_CALL:(\w+):\{\}\]'
    matches_no_args = re.findall(pattern_no_args, response_text)
    
    for tool_name in matches_no_args:
        tool_calls.append((tool_name, {}))
    
    return tool_calls

async def run_agent_with_tools(user_message: str, user_id: str = "default_user", use_memory: bool = True) -> Tuple[str, List[str]]:
    try:
        if use_memory:
            context = get_conversation_context(user_id)
            context.append({"role": "user", "content": user_message})
        else:
            context = [{"role": "user", "content": user_message}]

        response_text = call_gemini_api(context)
        tools_used = []

        tool_calls = parse_tool_calls(response_text)

        if tool_calls:
            tool_results = []
            for tool_name, tool_args in tool_calls:
                tools_used.append(tool_name)
                tool_result = await execute_tool_call(tool_name, tool_args)
                tool_results.append(f"{tool_name}: {tool_result}")

                context.append({"role": "assistant", "content": f"[TOOL_RESULT:{tool_name}]: {tool_result}"})

            final_response = call_gemini_api(context)

            if not final_response or final_response.strip() == response_text.strip():
                final_response = f"I've retrieved the requested information:\n\n" + "\n\n".join(tool_results)
        else:
            final_response = response_text

        if use_memory:
            add_to_conversation(user_id, "user", user_message)
            add_to_conversation(user_id, "assistant", final_response)

        return final_response, tools_used

    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}", []

async def run_agent(user_message: str, user_id: str = "default_user") -> str:
    response, _ = await run_agent_with_tools(user_message, user_id)
    return response
