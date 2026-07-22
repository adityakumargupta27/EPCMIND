from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from models.schemas import ComplianceDataResponse
from data.mock_data import mock_compliance, compliance_stats
from rag import vector_store
from services import compliance_service

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

class ComplianceAnalyzeRequest(BaseModel):
    requirement_document_id: str
    vendor_document_id: str
    equipment: Optional[str] = "UPS-04"
    discipline: Optional[str] = "Electrical"

@router.get("", response_model=ComplianceDataResponse)
async def get_compliance_checks():
    """
    Return the latest real persisted compliance analysis from SQLite database.
    If no real analysis exists, return initial empty/default state.
    """
    latest = vector_store.get_latest_compliance_analysis()
    if latest:
        return {
            "checks": latest["checks"],
            "stats": latest["stats"]
        }

    # Default initial state when no real analysis has been run yet
    return {
        "checks": mock_compliance,
        "stats": compliance_stats
    }

@router.post("/analyze")
async def run_compliance_analysis(request: ComplianceAnalyzeRequest):
    """
    Execute document-to-document specification compliance comparison.
    """
    try:
        res = compliance_service.analyze_compliance(
            requirement_document_id=request.requirement_document_id,
            vendor_document_id=request.vendor_document_id,
            equipment=request.equipment or "UPS-04",
            discipline=request.discipline or "Electrical"
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance analysis failed: {str(e)}")
