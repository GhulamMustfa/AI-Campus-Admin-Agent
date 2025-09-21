# agent.py
import os
from openai import OpenAI
import asyncio

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---- Normal chat ----
async def ask_model(messages):
    """
    messages: list of {"role":"user"|"system"|"assistant", "content": "..."}
    Returns model response as string
    """
    # The OpenAI Python client is synchronous by default
    # Wrap in asyncio to use with FastAPI
    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(
        None,
        lambda: client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=messages
        )
    )
    return resp.choices[0].message["content"]

# ---- Streaming chat ----
def stream_chat(messages):
    """
    Stream responses from the model as generator of strings
    """
    with client.chat.completions.stream(
        model="gemini-2.5-flash",
        messages=messages
    ) as stream:
        for event in stream:
            if event.type == "delta" and event.delta.get("content"):
                yield event.delta["content"]

