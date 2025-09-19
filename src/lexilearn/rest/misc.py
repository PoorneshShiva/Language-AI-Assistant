from fastapi import APIRouter, Query, HTTPException, Depends, Request
from typing import Literal, Optional
import random
import uuid
import datetime
from lexilearn.rest.models import SuccessResponse, PromptsData, Prompt, EvaluationRequest, EvaluationData, CompletedData, CompletedItem, IgnoreRequest, IgnoreData, UnignoreRequest, UnignoreData, HintsData, Hint, VerbDetails
from lexilearn.database import Database
from lexilearn.utils.agents.tools import evaluate_german_sentence
from lexilearn.utils.agents.verb_agent import generate_verb_training_data

router = APIRouter()

@router.get("/health")
async def health():
    return {"ok": True, "data": {"status": "healthy"}}

@router.get("/prompts", response_model=SuccessResponse[PromptsData])
async def get_prompts(
    request_obj: Request,
    item_type: Literal["verb", "noun"],
    item_id: str,
    level: Literal["beginner", "advanced"],
    count: int = 1,
):
    db = Database(request_obj.state.db_connection)
    if item_type == "verb":
        # Generate verb training data using LangChain
        verb_training_data = generate_verb_training_data(item_id, level)
        # Map VerbTrainingData to Prompt and VerbDetails
        prompt_id = str(uuid.uuid4())
        prompt = Prompt(
            id=prompt_id,
            level=level,
            en=verb_training_data.english_translation,
            de=verb_training_data.german_sentence,
            tags=["verb"]
        )
        # For VerbDetails, we need to construct it from VerbTrainingData
        # This assumes VerbDetails is a subset or can be constructed from VerbTrainingData
        verb_details = VerbDetails(
            infinitive=verb_training_data.infinitive,
            present=verb_training_data.conjugations.present,
            present_perfect=[], # LLM doesn't provide this directly in this structure
            singular_present_tense=[], # LLM doesn't provide this directly in this structure
            simple_past=verb_training_data.conjugations.simple_past,
            is_separable=verb_training_data.is_separable,
            is_regular=verb_training_data.is_regular,
            english_alternative=[verb_training_data.english_translation],
            notes=verb_training_data.notes
        )
        # Return both prompt and verb_details (or just prompt, depending on frontend needs)
        # For now, we'll return a PromptsData with the generated prompt
        return SuccessResponse(
            data=PromptsData(prompts=[prompt])
        )
    else:
        # Existing logic for other item types
        # 1. Find word_uid
        cursor = db.conn.cursor()
        cursor.execute("SELECT word_uid FROM word_index WHERE item_type = ? AND item_id = ?", (item_type, item_id))
        result = cursor.fetchone()
        if not result:
            return SuccessResponse(data=PromptsData(prompts=[]))
        word_uid = result[0]

        # 2. Find prompt_ids
        cursor.execute("SELECT prompt_id FROM prompt_word WHERE word_uid = ?", (word_uid,))
        prompt_ids = [row[0] for row in cursor.fetchall()]
        if not prompt_ids:
            return SuccessResponse(data=PromptsData(prompts=[]))

        # 3. Filter prompts by level and fetch details
        prompts = []
        for prompt_id in prompt_ids:
            prompt_data = db.get_prompt(prompt_id)
            if prompt_data and prompt_data['level'] == level:
                prompts.append(Prompt(**prompt_data))

        # 4. Return `count` prompts
        random.shuffle(prompts)
        
        return SuccessResponse(
            data=PromptsData(prompts=prompts[:count])
        )

@router.post("/evaluate", response_model=SuccessResponse[EvaluationData])
async def evaluate_answer(request: EvaluationRequest):
    evaluation_result = evaluate_german_sentence.run(expected=request.expected, answer=request.answer)
    return SuccessResponse(data=EvaluationData(**evaluation_result))

@router.get("/completed", response_model=SuccessResponse[CompletedData])
async def get_completed(request_obj: Request):
    db = Database(request_obj.state.db_connection)
    user_id = "test_user" # Hardcoded user for now

    cursor = db.conn.cursor()
    query = """
        SELECT wi.item_id
        FROM user_word uw
        JOIN word_index wi ON uw.word_uid = wi.word_uid
        WHERE uw.user_id = ? AND uw.status = 'completed'
        ORDER BY uw.updated_at DESC
    """
    
    cursor.execute(query, (user_id,))
    
    items = []
    for row in cursor.fetchall():
        items.append(CompletedItem(
            type=row[0],
            id=row[1],
            completed_at=row[2]
        ))
        
    return SuccessResponse(
        data=CompletedData(items=items)
    )

@router.post("/ignore", response_model=SuccessResponse[IgnoreData])
async def post_ignore(request: IgnoreRequest, request_obj: Request):
    db = Database(request_obj.state.db_connection)
    user_id = "test_user" # Hardcoded user for now

    # 1. Find word_uid
    cursor = db.conn.cursor()
    cursor.execute("SELECT word_uid FROM word_index WHERE item_type = ? AND item_id = ?", (request.item.type, request.item.id))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Word not found")
    word_uid = result[0]

    # 2. Update user_word status to 'ignored'
    db.conn.execute("UPDATE user_word SET status = 'ignored' WHERE user_id = ? AND word_uid = ?", (user_id, word_uid))
    db.conn.commit()
    
    return SuccessResponse(
        data=IgnoreData(status="ignored")
    )

@router.delete("/ignore", response_model=SuccessResponse[UnignoreData])
async def delete_ignore(request: UnignoreRequest, request_obj: Request):
    db = Database(request_obj.state.db_connection)
    user_id = "test_user" # Hardcoded user for now

    # 1. Find word_uid
    cursor = db.conn.cursor()
    cursor.execute("SELECT word_uid FROM word_index WHERE item_type = ? AND item_id = ?", (request.item.type, request.item.id))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Word not found")
    word_uid = result[0]

    # 2. Update user_word status to 'new'
    db.conn.execute("UPDATE user_word SET status = 'new' WHERE user_id = ? AND word_uid = ?", (user_id, word_uid))
    db.conn.commit()
    
    return SuccessResponse(
        data=UnignoreData(status="unignored")
    )

@router.get("/hints/nouns", response_model=SuccessResponse[HintsData])
async def get_hints_nouns(
    request_obj: Request,
    scope: Literal["recent", "all"] = "recent",
    cases: Optional[str] = Query(None),
    limit: int = 20,
):
    db = Database(request_obj.state.db_connection)
    user_id = "test_user" # Hardcoded user for now

    # 1. Get learned nouns for the user
    cursor = db.conn.cursor()
    
    query = """
        SELECT wi.item_id
        FROM user_word uw
        JOIN word_index wi ON uw.word_uid = wi.word_uid
        WHERE uw.user_id = ? AND wi.item_type = 'noun' AND uw.status IN ('queued', 'learning', 'completed')
    """
    
    if scope == "recent":
        seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
        query += " AND uw.added_at >= ?"
        cursor.execute(query, (user_id, seven_days_ago))
    else:
        cursor.execute(query, (user_id,))
        
    learned_nouns = [row[0] for row in cursor.fetchall()]
    
    if not learned_nouns:
        return SuccessResponse(data=HintsData(hints=[]))

    # 2. Get noun details and format hints
    hints = []
    
    requested_cases = []
    if cases:
        requested_cases = [c.strip() for c in cases.split(',')]

    for noun_id in learned_nouns:
        noun_details = db.get_noun(noun_id)
        if noun_details:
            label = f"{noun_details['gender']} {noun_details['noun']}"
            
            case_hints = []
            if 'accusative' in requested_cases:
                case_hints.append(f"acc: {noun_details['case_forms']['accusative']}")
            if 'dative' in requested_cases:
                case_hints.append(f"dat: {noun_details['case_forms']['dative']}")
            if 'genitive' in requested_cases:
                case_hints.append(f"gen: {noun_details['case_forms']['genitive']}")

            if case_hints:
                label += f" ({ ', '.join(case_hints) })"
            
            hints.append(Hint(label=label, insert=noun_details['noun']))

    return SuccessResponse(
        data=HintsData(hints=hints[:limit])
    )
