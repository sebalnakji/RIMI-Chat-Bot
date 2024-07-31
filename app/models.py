from pydantic import BaseModel

class ChatRequest(BaseModel):
    user: str
    thread_id: str
    