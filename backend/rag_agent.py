from PyPDF2 import PdfReader
import io


def extract_pdf_text_from_bytes(pdf_in_memory: io.BytesIO) -> str:
    reader = PdfReader(pdf_in_memory)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def get_thread_context(conversation_memory, user_id: str, thread_id: str) -> str:
    if user_id not in conversation_memory or thread_id not in conversation_memory[user_id]:
        return ""
    thread_memory = conversation_memory[user_id][thread_id]
    context = thread_memory.get("pdf_context", "")
    messages = "\n".join([f"{m['role']}: {m['content']}" for m in thread_memory.get("messages", [])])
    return f"{context}\n{messages}" if context else messages

def clear_thread_memory(conversation_memory, user_id: str, thread_id: str):
    if user_id in conversation_memory and thread_id in conversation_memory[user_id]:
        del conversation_memory[user_id][thread_id]