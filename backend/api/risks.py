from fastapi import APIRouter
from models.schemas import RiskDataResponse
from data.mock_data import mock_risks, risk_stats, risk_distribution

router = APIRouter(prefix="/api/risks", tags=["risks"])

@router.get("", response_model=RiskDataResponse)
async def get_risks():
    return {
        "risks": mock_risks,
        "stats": risk_stats,
        "distribution": risk_distribution
    }

@router.post("/analyze")
async def run_risk_analysis():
    return {"ok": True, "criticalFound": 3}
