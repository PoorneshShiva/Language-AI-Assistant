from fastapi import APIRouter, Depends, Request, HTTPException
import datetime
from lexilearn.rest.models import SuccessResponse, SettingsData, PatchSettingsRequest, StatsData, TodayStats, TotalStats
from lexilearn.database import Database

router = APIRouter()

@router.get("/settings", response_model=SuccessResponse[SettingsData])
async def get_settings(request_obj: Request):
    db = Database(request_obj.state.db_connection)
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
    db = Database(request_obj.state.db_connection)
    user_id = "test_user" # Hardcoded user for now
    
    # Get current settings
    user_settings = db.get_user_settings(user_id)
    if not user_settings:
        # This should not happen if get_settings is called before, but as a fallback
        raise HTTPException(status_code=404, detail="Settings not found for user")

    # Update settings
    update_data = request.dict(exclude_unset=True)
    updated_settings = {**user_settings, **update_data}
    
    db.conn.execute("""
        UPDATE user_settings
        SET level = ?, daily_goal = ?, style = ?, review_enabled = ?, updated_at = ?
        WHERE user_id = ?
    """, (
        updated_settings['level'],
        updated_settings['daily_goal'],
        updated_settings['style'],
        updated_settings['review_enabled'],
        datetime.datetime.now().isoformat(),
        user_id
    ))
    db.conn.commit()

    return SuccessResponse(
        data=SettingsData(**updated_settings)
    )

@router.get("/stats", response_model=SuccessResponse[StatsData])
async def get_stats(request_obj: Request):
    db = Database(request_obj.state.db_connection)
    user_id = "test_user" # Hardcoded user for now

    # Today's stats
    today = datetime.date.today().isoformat()
    today_stats = db.get_user_stats_daily(user_id, today)
    if not today_stats:
        today_stats = {"learned": 0, "practiced": 0, "completed": 0}

    # Total stats
    cursor = db.conn.cursor()
    
    # Total learned
    cursor.execute("SELECT COUNT(*) FROM user_word WHERE user_id = ? AND status IN ('learning', 'queued', 'completed')", (user_id,))
    total_learned = cursor.fetchone()[0]
    
    # Total completed
    cursor.execute("SELECT COUNT(*) FROM user_word WHERE user_id = ? AND status = 'completed'", (user_id,))
    total_completed = cursor.fetchone()[0]
    
    # Total in queue
    cursor.execute("SELECT COUNT(*) FROM user_word WHERE user_id = ? AND status IN ('queued', 'learning')", (user_id,))
    total_in_queue = cursor.fetchone()[0]

    return SuccessResponse(
        data=StatsData(
            today=TodayStats(**today_stats),
            totals=TotalStats(
                learned=total_learned,
                completed=total_completed,
                in_queue=total_in_queue
            )
        )
    )
