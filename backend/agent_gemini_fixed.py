import os
import json
import logging
import requests
from typing import List, Dict, Any, Tuple
import asyncio

# Import our tools
from backend.tools import (
    add_student, get_student, update_student, delete_student, list_students,
    get_total_students, get_students_by_department, get_recent_onboarded_students,
    get_active_students_last_7_days, send_email
)

logger = logging.getLogger(__name__)

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")  # Fallback to OPENAI_API_KEY
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Conversation memory (in production, use Redis or database)
conversation_memory: Dict[str, List[Dict[str, str]]] = {}

# Tool function mapping
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
    """Get conversation history for context"""
    history = conversation_memory.get(user_id, [])
    return history[-max_turns:] if len(history) > max_turns else history

def add_to_conversation(user_id: str, role: str, content: str):
    """Add message to conversation history"""
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    
    conversation_memory[user_id].append({
        "role": role,
        "content": content
    })

async def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool function call"""
    try:
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        if tool_name not in TOOL_FUNCTIONS:
            return f"Error: Tool '{tool_name}' not found"
        
        tool_func = TOOL_FUNCTIONS[tool_name]
        
        # Handle async tools
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**arguments)
        else:
            result = tool_func(**arguments)
        
        logger.info(f"Tool {tool_name} executed successfully")
        return str(result)
        
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return f"Error executing {tool_name}: {str(e)}"

def call_gemini_api(messages: List[Dict[str, str]]) -> str:
    """Call Gemini API with messages"""
    try:
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                # Gemini doesn't have system messages, prepend to user message
                continue
            elif msg["role"] == "user":
                contents.append({
                    "role": "user",
                    "parts": [{"text": msg["content"]}]
                })
            elif msg["role"] == "assistant":
                contents.append({
                    "role": "model",
                    "parts": [{"text": msg["content"]}]
                })
        
        # Add system prompt as first user message
        system_prompt = """You are an AI Campus Admin Agent. You help manage student records, provide campus information, and generate analytics.

You have access to the following tools:
- list_students: Get all students (no parameters needed)
- add_student: Add a new student (requires: name, student_id, department, email)
- get_student: Get student by ID (requires: student_id)
- update_student: Update student info (requires: student_id, field, new_value)
- delete_student: Delete student (requires: student_id)
- get_total_students: Get total count (no parameters)
- get_students_by_department: Get department breakdown (no parameters)
- get_recent_onboarded_students: Get recent students (optional: limit)
- get_active_students_last_7_days: Get active students count (no parameters)
- send_email: Send email to student (requires: student_id, message)

IMPORTANT: When users ask for data, you MUST call the appropriate tool first, then provide a helpful response based on the tool results.

Tool calling format:
- For tools with no parameters: [TOOL_CALL:tool_name:{}]
- For tools with parameters: [TOOL_CALL:tool_name:{"param": "value"}]

Examples:
- User asks "list all students" → Call [TOOL_CALL:list_students:{}]
- User asks "how many students total" → Call [TOOL_CALL:get_total_students:{}]
- User asks "add student John Doe" → Call [TOOL_CALL:add_student:{"name": "John Doe", "student_id": "12345", "department": "CS", "email": "john@uni.edu"}]

After calling tools, provide a clear, well-formatted response that summarizes the results in a user-friendly way. Use markdown formatting for better readability."""

        # Prepend system prompt
        contents.insert(0, {
            "role": "user",
            "parts": [{"text": system_prompt}]
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        # Make request
        response = requests.post(
            f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extract response text
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
        
        return "No response generated"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Gemini API request failed: {e}")
        raise Exception(f"Gemini API error: {e}")
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise Exception(f"Gemini API error: {e}")

def format_tool_results(tool_calls: List[Tuple[str, Dict[str, Any]]], tool_results: List[str], user_message: str) -> str:
    """Format tool results into a nice response"""
    
    # Determine the type of request
    user_msg_lower = user_message.lower()
    
    if "list" in user_msg_lower and "student" in user_msg_lower:
        return format_student_list(tool_results[0] if tool_results else "")
    elif "total" in user_msg_lower or "count" in user_msg_lower or "how many" in user_msg_lower:
        return format_count_response(tool_results[0] if tool_results else "")
    elif "department" in user_msg_lower:
        return format_department_response(tool_results[0] if tool_results else "")
    elif "recent" in user_msg_lower:
        return format_recent_students_response(tool_results[0] if tool_results else "")
    else:
        # Generic response
        return f"✅ **Request Completed Successfully**\n\n" + "\n\n".join(tool_results)

def format_student_list(tool_result: str) -> str:
    """Format student list response"""
    try:
        # Extract the list from the tool result
        if "list_students:" in tool_result:
            students_data = tool_result.split("list_students:")[1].strip()
            
            # Try to parse as JSON if it looks like a list
            if students_data.startswith("[") and students_data.endswith("]"):
                import json
                students = json.loads(students_data)
                
                if not students:
                    return "📋 **Student List**\n\nNo students found in the database."
                
                response = "📋 **Student List**\n\n"
                for i, student in enumerate(students, 1):
                    response += f"**{i}. {student.get('name', 'Unknown')}**\n"
                    response += f"   • Student ID: `{student.get('student_id', 'N/A')}`\n"
                    response += f"   • Department: {student.get('department', 'N/A')}\n"
                    response += f"   • Email: {student.get('email', 'N/A')}\n\n"
                
                response += f"**Total Students:** {len(students)}"
                return response
            else:
                return f"📋 **Student List**\n\n{tool_result}"
        else:
            return f"📋 **Student List**\n\n{tool_result}"
    except Exception as e:
        return f"📋 **Student List**\n\n{tool_result}"

def format_count_response(tool_result: str) -> str:
    """Format count/total response"""
    try:
        if "get_total_students:" in tool_result:
            count = tool_result.split("get_total_students:")[1].strip()
            return f"📊 **Campus Statistics**\n\n**Total Students:** {count}"
        else:
            return f"📊 **Campus Statistics**\n\n{tool_result}"
    except:
        return f"📊 **Campus Statistics**\n\n{tool_result}"

def format_department_response(tool_result: str) -> str:
    """Format department breakdown response"""
    try:
        if "get_students_by_department:" in tool_result:
            dept_data = tool_result.split("get_students_by_department:")[1].strip()
            
            # Try to parse as JSON
            if dept_data.startswith("{") and dept_data.endswith("}"):
                import json
                departments = json.loads(dept_data)
                
                response = "🏫 **Students by Department**\n\n"
                for dept, count in departments.items():
                    response += f"• **{dept}:** {count} students\n"
                
                total = sum(departments.values())
                response += f"\n**Total:** {total} students"
                return response
            else:
                return f"🏫 **Students by Department**\n\n{tool_result}"
        else:
            return f"🏫 **Students by Department**\n\n{tool_result}"
    except:
        return f"🏫 **Students by Department**\n\n{tool_result}"

def format_recent_students_response(tool_result: str) -> str:
    """Format recent students response"""
    try:
        if "get_recent_onboarded_students:" in tool_result:
            students_data = tool_result.split("get_recent_onboarded_students:")[1].strip()
            
            # Try to parse as JSON
            if students_data.startswith("[") and students_data.endswith("]"):
                import json
                students = json.loads(students_data)
                
                if not students:
                    return "🆕 **Recent Enrollments**\n\nNo recent students found."
                
                response = "🆕 **Recent Enrollments**\n\n"
                for i, student in enumerate(students, 1):
                    response += f"**{i}. {student.get('name', 'Unknown')}**\n"
                    response += f"   • Student ID: `{student.get('student_id', 'N/A')}`\n"
                    response += f"   • Department: {student.get('department', 'N/A')}\n"
                    response += f"   • Enrolled: {student.get('created_at', 'N/A')}\n\n"
                
                return response
            else:
                return f"🆕 **Recent Enrollments**\n\n{tool_result}"
        else:
            return f"🆕 **Recent Enrollments**\n\n{tool_result}"
    except:
        return f"🆕 **Recent Enrollments**\n\n{tool_result}"

def parse_tool_calls(response_text: str) -> List[Tuple[str, Dict[str, Any]]]:
    """Parse tool calls from response text"""
    tool_calls = []
    
    # Look for tool call patterns - handle both with and without arguments
    import re
    
    # Pattern for tool calls with arguments: [TOOL_CALL:tool_name:{"arg": "value"}]
    pattern_with_args = r'\[TOOL_CALL:(\w+):({[^}]+})\]'
    matches_with_args = re.findall(pattern_with_args, response_text)
    
    for tool_name, args_str in matches_with_args:
        try:
            args = json.loads(args_str)
            tool_calls.append((tool_name, args))
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse tool arguments: {args_str}")
    
    # Pattern for tool calls without arguments: [TOOL_CALL:tool_name:{}]
    pattern_no_args = r'\[TOOL_CALL:(\w+):\{\}\]'
    matches_no_args = re.findall(pattern_no_args, response_text)
    
    for tool_name in matches_no_args:
        tool_calls.append((tool_name, {}))
    
    return tool_calls

async def run_agent_with_tools(user_message: str, user_id: str = "default_user") -> Tuple[str, List[str]]:
    """
    Main agent function with tool calling and memory
    Returns: (response_text, list_of_tools_used)
    """
    try:
        # Get conversation context
        context = get_conversation_context(user_id)
        
        # Add user message to context
        context.append({"role": "user", "content": user_message})
        
        logger.info(f"Processing message for user {user_id}: {user_message[:50]}...")
        
        # Call Gemini API
        response_text = call_gemini_api(context)
        logger.info(f"Gemini response: {response_text[:200]}...")
        
        tools_used = []
        
        # Check for tool calls
        tool_calls = parse_tool_calls(response_text)
        logger.info(f"Parsed tool calls: {tool_calls}")
        
        if tool_calls:
            logger.info(f"Found {len(tool_calls)} tool calls: {[tc[0] for tc in tool_calls]}")
            
            # Execute tool calls
            tool_results = []
            for tool_name, tool_args in tool_calls:
                tools_used.append(tool_name)
                tool_result = await execute_tool_call(tool_name, tool_args)
                tool_results.append(f"{tool_name}: {tool_result}")
                
                # Add tool result to context
                context.append({
                    "role": "assistant", 
                    "content": f"[TOOL_RESULT:{tool_name}]: {tool_result}"
                })
            
            # Get final response after tool execution
            logger.info("Getting final response after tool execution")
            final_response = call_gemini_api(context)
            
            # If the final response is empty or just repeats the tool call, provide a formatted summary
            if not final_response or final_response.strip() == response_text.strip():
                final_response = format_tool_results(tool_calls, tool_results, user_message)
                
        else:
            logger.info("No tool calls found, using direct response")
            final_response = response_text
        
        # Add assistant response to conversation memory
        add_to_conversation(user_id, "user", user_message)
        add_to_conversation(user_id, "assistant", final_response)
        
        logger.info(f"Agent response generated for user {user_id}")
        return final_response, tools_used
        
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}", []

# Legacy function for backward compatibility
async def run_agent(user_message: str, user_id: str = "default_user") -> str:
    """Legacy function that returns only the response text"""
    response, _ = await run_agent_with_tools(user_message, user_id)
    return response
