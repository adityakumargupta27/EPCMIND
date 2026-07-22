from fastapi import APIRouter
from ..models.schemas import ProjectDataResponse
from data.mock_data import (
    mock_project, health_breakdown, progress_breakdown, project_team,
    disciplines, equipment_list
)

router = APIRouter(prefix="/api/project", tags=["project"])

@router.get("", response_model=ProjectDataResponse)
async def get_project():
    return {
        **mock_project,
        "healthBreakdown": health_breakdown,
        "progressBreakdown": progress_breakdown,
        "team": project_team,
        "disciplines": disciplines,
        "equipment": equipment_list
    }
