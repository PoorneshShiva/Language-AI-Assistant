from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Literal
import datetime
from lexilearn.rest.models import SuccessResponse, PracticeQueueData, PracticeQueueItem, ConfidenceRequest, ConfidenceData, Scheduled, CompleteRequest, CompleteData, ReviewAgainRequest, ReviewAgainData
from lexilearn.database import Database

router = APIRouter()

@router.get("/queue", response_model=SuccessResponse[PracticeQueueData])
async def get_practice_queue(request_obj: Request, level: Literal["beginner", "advanced"], limit: int = 50):
    db = Database(request_obj.state.db_connection)
    user_id = "test_user" # Hardcoded user for now
    
    # TODO: Implement level filtering

    cursor = db.conn.cursor()
    
    now = datetime.datetime.now().isoformat()
    query = """
        SELECT uw.word_uid, uw.due_at, uw.stability, uw.interval_days, uw.lapses, wi.item_type, wi.item_id
        FROM user_word uw
        JOIN word_index wi ON uw.word_uid = wi.word_uid
        WHERE uw.user_id = ? AND uw.status IN ('queued', 'learning') AND uw.due_at <= ?
        ORDER BY uw.due_at
        LIMIT ?
    """
    
    cursor.execute(query, (user_id, now, limit))
    
    queue = []
    for row in cursor.fetchall():
        queue.append(PracticeQueueItem(
            type=row[5],
            id=row[6],
            due_at=row[1],
            stability=row[2],
            interval_days=row[3],
            lapses=row[4]
        ))
        
    return SuccessResponse(
        data=PracticeQueueData(queue=queue)
    )

@router.post("/confidence", response_model=SuccessResponse[ConfidenceData])
async def post_practice_confidence(request: ConfidenceRequest, request_obj: Request):
    db = Database(request_obj.state.db_connection)
    user_id = "test_user" # Hardcoded user for now

    # 1. Find word_uid
    cursor = db.conn.cursor()
    cursor.execute("SELECT word_uid FROM word_index WHERE item_type = ? AND item_id = ?", (request.item.type, request.item.id))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Word not found")
    word_uid = result[0]

    # 2. Get user_word
    user_word = db.get_user_word(user_id, word_uid)
    if not user_word:
        db.add_user_word({"user_id": user_id, "word_uid": word_uid})
        user_word = db.get_user_word(user_id, word_uid)

    # 3. Update interval based on confidence
    interval = user_word.get('interval_days', 1)
    if request.confidence == "Again":
        interval = 1
    elif request.confidence == "Hard":
        interval = interval * 1.2
    elif request.confidence == "Good":
        interval = interval * 2.5
    elif request.confidence == "Easy":
        interval = interval * 4

    new_due_date = datetime.datetime.now() + datetime.timedelta(days=interval)
    
    status = "queued"
    if request.confidence == "Easy" and interval > 30: # consider completed if interval is more than 30 days
        status = "completed"

    # 4. Update user_word in the database
    db.conn.execute("""
        UPDATE user_word
        SET due_at = ?, interval_days = ?, status = ?
        WHERE user_id = ? AND word_uid = ?
    """, (new_due_date.isoformat(), interval, status, user_id, word_uid))
    db.conn.commit()

    # 5. Return the new schedule
    return SuccessResponse(
        data=ConfidenceData(
            scheduled=Scheduled(
                due_at=new_due_date.isoformat(),
                interval_days=int(interval),
                stability=user_word.get('stability', 0.73) # dummy stability
            ),
            moved_to=status
        )
    )

@router.post("/complete", response_model=SuccessResponse[CompleteData])
async def post_practice_complete(request: CompleteRequest, request_obj: Request):
    db = Database(request_obj.state.db_connection)
    user_id = "test_user" # Hardcoded user for now

    # 1. Find word_uid
    cursor = db.conn.cursor()
    cursor.execute("SELECT word_uid FROM word_index WHERE item_type = ? AND item_id = ?", (request.item.type, request.item.id))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Word not found")
    word_uid = result[0]

    # 2. Update user_word status to 'completed'
    db.conn.execute("UPDATE user_word SET status = 'completed' WHERE user_id = ? AND word_uid = ?", (user_id, word_uid))
    db.conn.commit()
    
    return SuccessResponse(
        data=CompleteData(status="completed")
    )

@router.post("/review-again", response_model=SuccessResponse[ReviewAgainData])
async def post_practice_review_again(request: ReviewAgainRequest, request_obj: Request):
    db = Database(request_obj.state.db_connection)
    user_id = "test_user" # Hardcoded user for now

    # 1. Find word_uid
    cursor = db.conn.cursor()
    cursor.execute("SELECT word_uid FROM word_index WHERE item_type = ? AND item_id = ?", (request.item.type, request.item.id))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Word not found")
    word_uid = result[0]

    # 2. Update user_word status to 'queued'
    db.conn.execute("UPDATE user_word SET status = 'queued', due_at = ? WHERE user_id = ? AND word_uid = ?", (datetime.datetime.now().isoformat(), user_id, word_uid))
    db.conn.commit()
    
    return SuccessResponse(
        data=ReviewAgainData(status="queued")
    )
