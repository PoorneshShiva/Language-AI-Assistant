from fastapi import APIRouter, Request, HTTPException
import datetime
from lexilearn.rest.models import SuccessResponse, SettingsData, PatchSettingsRequest, StatsData, TodayStats, TotalStats
from lexilearn.database import Database

router = APIRouter()

@router.get("/settings", response_model=SuccessResponse[SettingsData])
async def get_settings(request_obj: Request):
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now
    
    user_settings = db.get_user_settings(user_id)
    if not user_settings:
        # Create default settings if they don't exist
        default_settings = {
            "user_id": user_id,
            "level": "beginner",
            "daily_goal": 10,
            "style": "mixed",
            "review_enabled": True
        }
        db.add_user_settings(default_settings)
        user_settings = db.get_user_settings(user_id)

    return SuccessResponse(
        data=SettingsData(**user_settings)
    )

@router.patch("/settings", response_model=SuccessResponse[SettingsData])
async def patch_settings(request: PatchSettingsRequest, request_obj: Request):
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now
    
    # Get current settings
    user_settings = db.get_user_settings(user_id)
    if not user_settings:
        # This should not happen if get_settings is called before, but as a fallback
        raise HTTPException(status_code=404, detail="Settings not found for user")

    # Update settings
    update_data = request.dict(exclude_unset=True)
    updated_settings = {**user_settings, **update_data}
    
    db.update_user_settings(
        user_id,
        level=updated_settings['level'],
        daily_goal=updated_settings['daily_goal'],
        style=updated_settings['style'],
        review_enabled=updated_settings['review_enabled']
    )

    return SuccessResponse(
        data=SettingsData(**updated_settings)
    )

@router.get("/stats", response_model=SuccessResponse[StatsData])
async def get_stats(request_obj: Request):
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now

    # Today's stats
    today = datetime.date.today().isoformat()
    today_stats = db.get_user_stats_daily(user_id, today)
    if not today_stats:
        today_stats = {"learned": 0, "practiced": 0, "completed": 0}

    # Total stats
    totals = db.get_total_stats(user_id)

    return SuccessResponse(
        data=StatsData(
            today=TodayStats(**{
                "learned": today_stats.get("learned", 0),
                "practiced": today_stats.get("practiced", 0),
                "completed": today_stats.get("completed", 0),
            }),
            totals=TotalStats(
                learned=totals.get("learned", 0),
                completed=totals.get("completed", 0),
                in_queue=totals.get("in_queue", 0)
            )
        )
    )
