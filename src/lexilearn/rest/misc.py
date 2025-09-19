from fastapi import APIRouter, Query, HTTPException, Request
from typing import Literal, Optional
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
    db: Database = request_obj.state.db
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
        prompts = [Prompt(**prompt) for prompt in db.get_prompts(item_type=item_type, item_id=item_id, level=level, count=count)]
        return SuccessResponse(data=PromptsData(prompts=prompts))

@router.post("/evaluate", response_model=SuccessResponse[EvaluationData])
async def evaluate_answer(request: EvaluationRequest):
    evaluation_result = evaluate_german_sentence.run(expected=request.expected, answer=request.answer)
    return SuccessResponse(data=EvaluationData(**evaluation_result))

@router.get("/completed", response_model=SuccessResponse[CompletedData])
async def get_completed(request_obj: Request):
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now
    items = []
    for entry in db.completed_list(user_id):
        completed_at = entry.get("updated_at") or datetime.datetime.utcnow()
        items.append(
            CompletedItem(
                type=entry.get("item_type", "verb"),
                id=entry.get("item_id", ""),
                completed_at=completed_at.isoformat(),
            )
        )

    return SuccessResponse(
        data=CompletedData(items=items)
    )

@router.post("/ignore", response_model=SuccessResponse[IgnoreData])
async def post_ignore(request: IgnoreRequest, request_obj: Request):
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now
    word_uid = db.add_word_index({"item_type": request.item.type, "item_id": request.item.id})
    db.update_user_word(user_id, word_uid, status="ignored", due_at=None)
    
    return SuccessResponse(
        data=IgnoreData(status="ignored")
    )

@router.delete("/ignore", response_model=SuccessResponse[UnignoreData])
async def delete_ignore(request: UnignoreRequest, request_obj: Request):
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now
    word_uid = db.add_word_index({"item_type": request.item.type, "item_id": request.item.id})
    db.update_user_word(user_id, word_uid, status="new")
    
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
    db: Database = request_obj.state.db
    user_id = "test_user" # Hardcoded user for now
    # 1. Get learned nouns for the user
    nouns = db.noun_hints(user_id, limit=None)
    if scope == "recent":
        threshold = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        nouns = [noun for noun in nouns if noun.get("added_at") and noun["added_at"] >= threshold]

    if not nouns:
        return SuccessResponse(data=HintsData(hints=[]))

    # 2. Get noun details and format hints
    hints = []

    requested_cases = []
    if cases:
        requested_cases = [c.strip() for c in cases.split(',')]

    for noun_details in nouns:
        label = f"{noun_details['gender']} {noun_details['noun']}".strip()

        case_hints = []
        if 'accusative' in requested_cases:
            case_hints.append(f"acc: {noun_details['case_forms'].get('accusative', '')}")
        if 'dative' in requested_cases:
            case_hints.append(f"dat: {noun_details['case_forms'].get('dative', '')}")
        if 'genitive' in requested_cases:
            case_hints.append(f"gen: {noun_details['case_forms'].get('genitive', '')}")

        filtered_case_hints = [hint for hint in case_hints if hint and not hint.endswith(': ')]
        if filtered_case_hints:
            label += f" ({', '.join(filtered_case_hints)})"

        hints.append(Hint(label=label.strip(), insert=noun_details['noun']))

    return SuccessResponse(
        data=HintsData(hints=hints[:limit])
    )
