from fastapi import APIRouter
from data.mock_data import mock_notifications, recent_activity

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/notifications")
async def get_notifications():
    return mock_notifications

@router.get("/activity")
async def get_activity():
    return recent_activity
