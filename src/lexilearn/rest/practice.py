from fastapi import APIRouter, Request, HTTPException
from typing import Literal
import datetime
from lexilearn.rest.models import SuccessResponse, PracticeQueueData, PracticeQueueItem, ConfidenceRequest, ConfidenceData, Scheduled, CompleteRequest, CompleteData, ReviewAgainRequest, ReviewAgainData
from lexilearn.database import Database

router = APIRouter()

@router.get("/queue", response_model=SuccessResponse[PracticeQueueData])
async def get_practice_queue(request_obj: Request, level: Literal["beginner", "advanced"], limit: int = 50):
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now
    # TODO: Implement level filtering

    queue_items = []
    for entry in db.practice_queue(user_id, limit=limit):
        due_at = entry.get("due_at") or datetime.datetime.utcnow()
        queue_items.append(
            PracticeQueueItem(
                type=entry.get("item_type", "verb"),
                id=entry.get("item_id", ""),
                due_at=due_at.isoformat(),
                stability=float(entry.get("stability", 0.0)),
                interval_days=int(entry.get("interval_days", 0)),
                lapses=int(entry.get("lapses", 0)),
            )
        )

    return SuccessResponse(
        data=PracticeQueueData(queue=queue_items)
    )

@router.post("/confidence", response_model=SuccessResponse[ConfidenceData])
async def post_practice_confidence(request: ConfidenceRequest, request_obj: Request):
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now
    word_uid = db.add_word_index({"item_type": request.item.type, "item_id": request.item.id})

    user_word = db.get_user_word(user_id, word_uid)
    if not user_word:
        db.add_user_word(
            {
                "user_id": user_id,
                "word_uid": word_uid,
                "item_type": request.item.type,
                "item_id": request.item.id,
                "status": "queued",
                "due_at": datetime.datetime.utcnow(),
                "interval_days": 1,
                "stability": 0.5,
            }
        )
        user_word = db.get_user_word(user_id, word_uid)

    interval = float(user_word.get("interval_days", 1))
    if request.confidence == "Again":
        interval = 1
    elif request.confidence == "Hard":
        interval = max(interval * 1.2, 1)
    elif request.confidence == "Good":
        interval = max(interval * 2.5, 1)
    elif request.confidence == "Easy":
        interval = max(interval * 4, 1)

    new_due_date = datetime.datetime.utcnow() + datetime.timedelta(days=interval)

    status = "queued"
    if request.confidence == "Easy" and interval > 30:
        status = "completed"

    updated_word = db.update_user_word(
        user_id,
        word_uid,
        status=status,
        due_at=new_due_date,
        interval_days=interval,
        last_result=request.confidence,
    )

    return SuccessResponse(
        data=ConfidenceData(
            scheduled=Scheduled(
                due_at=new_due_date.isoformat(),
                interval_days=int(interval),
                stability=float(updated_word.get("stability", 0.73)),
            ),
            moved_to=status,
        )
    )

@router.post("/complete", response_model=SuccessResponse[CompleteData])
async def post_practice_complete(request: CompleteRequest, request_obj: Request):
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now
    word_uid = db.add_word_index({"item_type": request.item.type, "item_id": request.item.id})
    db.update_user_word(user_id, word_uid, status="completed", due_at=None)
    
    return SuccessResponse(
        data=CompleteData(status="completed")
    )

@router.post("/review-again", response_model=SuccessResponse[ReviewAgainData])
async def post_practice_review_again(request: ReviewAgainRequest, request_obj: Request):
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now
    word_uid = db.add_word_index({"item_type": request.item.type, "item_id": request.item.id})
    db.update_user_word(user_id, word_uid, status="queued", due_at=datetime.datetime.utcnow())
    
    return SuccessResponse(
        data=ReviewAgainData(status="queued")
    )
