from fastapi import APIRouter
from ..models.schemas import ScheduleDataResponse
from data.mock_data import schedule_activities, milestones, upcoming_milestones, schedule_stats, critical_path

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

@router.get("", response_model=ScheduleDataResponse)
async def get_schedule():
    return {
        "activities": schedule_activities,
        "milestones": milestones,
        "upcoming": upcoming_milestones,
        "stats": schedule_stats,
        "criticalPath": critical_path
    }
