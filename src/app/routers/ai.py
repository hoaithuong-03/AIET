from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.chat import StoryChatService
import logging

router = APIRouter(prefix="/ai", tags=["AI Agent"])
logger = logging.getLogger(__name__)

# Lazy initialization or singleton
_chat_service = None

def get_chat_service():
    global _chat_service
    if _chat_service is None:
        try:
            _chat_service = StoryChatService()
        except Exception as e:
            logger.error(f"Failed to initialize ChatService: {e}")
            raise HTTPException(status_code=500, detail="AI Service is currently unavailable (indexing might be in progress)")
    return _chat_service

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Ask a question about the stories."""
    service = get_chat_service()
    answer = await service.ask(request.query)
    return ChatResponse(answer=answer)
