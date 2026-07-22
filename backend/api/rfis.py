from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from models.schemas import RFIDataResponse
from rag import vector_store
from services import rfi_service

router = APIRouter(prefix="/api/rfis", tags=["rfis"])

class CreateRFIRequest(BaseModel):
    subject: str
    question: str
    discipline: Optional[str] = "Electrical"
    priority: Optional[str] = "HIGH"
    equipment: Optional[str] = ""
    location: Optional[str] = ""
    raisedBy: Optional[str] = "Contractor"

class AnalyzeRFIRequest(BaseModel):
    rfi_id: Optional[str] = None
    subject: Optional[str] = None
    question: Optional[str] = None
    discipline: Optional[str] = "Electrical"
    equipment: Optional[str] = ""
    location: Optional[str] = ""

@router.get("", response_model=RFIDataResponse)
async def get_rfis():
    """Return all persisted RFIs and summary statistics."""
    rfi_service.seed_initial_rfis()
    db_rfis = vector_store.get_all_rfis()

    formatted_rfis = []
    open_cnt = 0
    critical_cnt = 0
    awaiting_cnt = 0
    closed_cnt = 0
    ai_matches_cnt = 0

    for r in db_rfis:
        status = r.get("status", "Open")
        priority = r.get("priority", "MEDIUM")
        
        if status == "Open":
            open_cnt += 1
        elif status == "Awaiting Response":
            awaiting_cnt += 1
        elif status == "Closed" or status == "Resolved":
            closed_cnt += 1

        if priority == "CRITICAL":
            critical_cnt += 1

        analysis = r.get("analysis") or {}
        ai_match_pct = analysis.get("similar", {}).get("match", 0) if analysis.get("similar") else 0
        if ai_match_pct >= 65:
            ai_matches_cnt += 1

        formatted_rfis.append({
            "id": r["rfi_id"],
            "subject": r["title"],
            "discipline": r["discipline"],
            "priority": priority,
            "status": status,
            "aiMatch": ai_match_pct,
            "created": r["created_at"][:11] if r.get("created_at") else "Today",
            "question": r["description"],
            "equipment": r.get("equipment"),
            "location": r.get("location"),
            "raisedBy": r.get("raised_by"),
            "similar": analysis.get("similar"),
            "suggested": analysis.get("suggestedResolution"),
            "reasoning": analysis.get("reasoning"),
            "recommendedActions": analysis.get("recommendedActions"),
            "confidence": analysis.get("confidence"),
            "sources": analysis.get("sources"),
            "finalResolution": r.get("final_resolution")
        })

    stats = {
        "open": open_cnt,
        "critical": critical_cnt,
        "awaiting": awaiting_cnt,
        "closed": closed_cnt,
        "avgResolution": "2.5 days",
        "aiMatches": ai_matches_cnt
    }

    return {
        "rfis": formatted_rfis,
        "stats": stats
    }

@router.get("/{rfi_id}")
async def get_rfi_by_id(rfi_id: str):
    """Retrieve detailed single RFI record by ID."""
    detail = rfi_service.get_rfi_detail(rfi_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"RFI with ID '{rfi_id}' not found.")
    return detail

@router.post("")
async def create_rfi(request: CreateRFIRequest):
    """Create, embed, analyze, and persist a new RFI record."""
    try:
        res = rfi_service.create_and_embed_rfi(
            title=request.subject,
            description=request.question,
            discipline=request.discipline or "Electrical",
            priority=request.priority or "HIGH",
            equipment=request.equipment or "",
            location=request.location or "",
            raised_by=request.raisedBy or "Contractor"
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create RFI: {str(e)}")

@router.post("/analyze")
async def analyze_rfi_endpoint(request: AnalyzeRFIRequest):
    """Trigger historical similarity and RAG intelligence analysis for an RFI."""
    try:
        rfi_data = {
            "rfi_id": request.rfi_id,
            "title": request.subject or "Technical Query",
            "description": request.question or request.subject or "Query details",
            "discipline": request.discipline or "Electrical",
            "equipment": request.equipment or "",
            "location": request.location or ""
        }
        if request.rfi_id:
            existing = rfi_service.get_rfi_detail(request.rfi_id)
            if existing:
                rfi_data["title"] = existing["subject"]
                rfi_data["description"] = existing["question"]
                rfi_data["discipline"] = existing["discipline"]

        res = rfi_service.analyze_rfi(rfi_data)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RFI analysis failed: {str(e)}")
