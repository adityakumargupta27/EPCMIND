from fastapi import APIRouter, HTTPException
from models.schemas import AIMessage
from pydantic import BaseModel
from services.gemini_service import get_copilot_status
from rag.rag_service import ask_copilot_rag

router = APIRouter(prefix="/api/copilot", tags=["copilot"])

class ChatRequest(BaseModel):
    question: str

@router.post("/chat", response_model=AIMessage)
async def ask_copilot_endpoint(request: ChatRequest):
    try:
        response_data = ask_copilot_rag(request.question)
        return AIMessage(**response_data)
    except Exception as e:
        # Prevent server crash on unhandled edge cases
        return AIMessage(
            role="assistant",
            content=f"An unexpected error occurred: {str(e)}",
            sources=[],
            meta={"action": "Contact Support"}
        )

@router.get("/status")
async def copilot_status():
    return get_copilot_status()
