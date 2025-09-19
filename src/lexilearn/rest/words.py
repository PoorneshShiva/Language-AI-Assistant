from fastapi import APIRouter, Query, HTTPException, Request
from typing import Dict, Iterable, Optional

from lexilearn.rest.models import (
    DetectWordsRequest,
    DetectWordsData,
    SuccessResponse,
    DetectedWord,
    RandomWordsRequest,
    RandomWordData,
    RandomWordItem,
    WordItem,
    WordsData,
    VerbDetails,
    NounDetails,
)
from lexilearn.utils.agents.main import AgenticMain
from lexilearn.models.common import UserQuery
from lexilearn.database import Database

router = APIRouter()


def _section(result: Optional[object], attr: str) -> Iterable:
    if result is None:
        return []
    if hasattr(result, attr):
        value = getattr(result, attr)
        if value:
            return value
    if isinstance(result, dict) and attr in result:
        value = result.get(attr)
        if value:
            return value
    if hasattr(result, "get"):
        try:
            value = result.get(attr)
            if value:
                return value
        except Exception:  # pragma: no cover - defensive
            pass
    return []


def _to_dict(obj: object) -> Dict:
    if isinstance(obj, dict):
        return obj
    try:
        return dict(obj)
    except Exception:
        return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("_")}


@router.post("/detect", response_model=SuccessResponse[DetectWordsData])
async def detect_words(request: DetectWordsRequest, request_obj: Request):
    agent_main: AgenticMain = request_obj.state.agent_main
    db: Database = request_obj.state.db
    agent = agent_main.build_german_graph()

    user_query_input = UserQuery(query=request.sentence)
    result = agent.invoke(user_query_input)
    print("LEXILEARN_DEBUG_DETECT result type:", type(result))
    if isinstance(result, dict):
        print("LEXILEARN_DEBUG_DETECT keys:", list(result.keys()))

    detected = []

    for verb_info in _section(result, "verbs_info"):
        data = _to_dict(verb_info)
        infinitive = data.get("infinitive")
        if infinitive and f"verb:{infinitive}" not in request.exclude_keys:
            payload = {
                "infinitive": infinitive,
                "present": data.get("present", {}),
                "present_perfect": data.get("present_perfect", []),
                "singular_present_tense": data.get("singular_present_tense", []),
                "simple_past": data.get("simple_past", []),
                "is_separable": bool(data.get("is_separable", False)),
                "is_regular": bool(data.get("is_regular", True)),
                "english_alternative": data.get("english_alternative", []),
                "notes": data.get("notes", []),
            }
            try:
                db.add_verb(payload)
                db.add_word_index({"item_type": "verb", "item_id": infinitive})
            except Exception as exc:  # pragma: no cover - defensive logging
                print("LEXILEARN_DEBUG_VERB_STORE_ERROR", exc)
            detected.append(DetectedWord(type="verb", id=infinitive))

    for noun_info in _section(result, "nouns_info"):
        data = _to_dict(noun_info)
        noun = data.get("noun")
        if noun and f"noun:{noun}" not in request.exclude_keys:
            payload = {
                "noun": noun,
                "plural": data.get("plural"),
                "gender": data.get("gender"),
                "case_forms": data.get("case_forms", {}),
                "english_translation": data.get("english_translation"),
                "is_irregular": bool(data.get("is_irregular", False)),
            }
            try:
                db.add_noun(payload)
                db.add_word_index({"item_type": "noun", "item_id": noun})
            except Exception as exc:  # pragma: no cover
                print("LEXILEARN_DEBUG_NOUN_STORE_ERROR", exc)
            detected.append(DetectedWord(type="noun", id=noun))

    for adj_info in _section(result, "adjectives_info"):
        data = _to_dict(adj_info)
        adjective = data.get("adjective")
        if adjective and f"adjective:{adjective}" not in request.exclude_keys:
            payload = {
                "adjective": adjective,
                "comparative": data.get("comparative"),
                "superlative": data.get("superlative"),
                "english_translation": data.get("english_translation"),
                "is_regular": bool(data.get("is_regular", True)),
                "is_comparable": bool(data.get("is_comparable", True)),
            }
            try:
                db.add_adjective(payload)
            except Exception as exc:  # pragma: no cover
                print("LEXILEARN_DEBUG_ADJECTIVE_STORE_ERROR", exc)
            detected.append(DetectedWord(type="adjective", id=adjective))

    return SuccessResponse(data=DetectWordsData(detected=detected))


@router.post("/random", response_model=SuccessResponse[RandomWordData])
async def random_words(request_obj: Request, request: RandomWordsRequest):
    db: Database = request_obj.state.db
    preferred_types = request.preferred_types or ["verb", "noun"]

    exclude_ids = [key.split(":", 1)[1] for key in request.exclude_keys if ":" in key]
    random_choice = db.random_word(
        user_id="test_user",
        preferred_types=preferred_types,
        exclude_ids=exclude_ids,
    )

    if not random_choice:
        return SuccessResponse(data=RandomWordData(item=RandomWordItem(type="verb", id="aufbewahren")))

    return SuccessResponse(
        data=RandomWordData(
            item=RandomWordItem(type=random_choice["item_type"], id=random_choice["item_id"])
        )
    )


@router.get("/", response_model=SuccessResponse[WordsData])
async def get_words(
    request_obj: Request,
    types: Optional[str] = Query(None),
    limit: int = 50,
    cursor: Optional[str] = None,
):
    db: Database = request_obj.state.db
    word_types = [t.strip() for t in types.split(',')] if types else ["verb", "noun"]

    offset = int(cursor) if cursor and cursor.isdigit() else 0
    window = max(limit + offset + 50, 200)
    pools = [db.list_words(item_type=word_type, limit=window) for word_type in word_types]

    merged = []
    pointers = [0] * len(pools)
    target = offset + limit

    while len(merged) < target and any(ptr < len(lst) for ptr, lst in zip(pointers, pools)):
        for idx, lst in enumerate(pools):
            if pointers[idx] < len(lst):
                merged.append(lst[pointers[idx]])
                pointers[idx] += 1
                if len(merged) >= target:
                    break

    page = merged[offset:offset + limit]
    items = [WordItem(type=word["item_type"], id=word["item_id"]) for word in page]
    has_more = len(merged) > offset + len(page) or any(ptr < len(lst) for ptr, lst in zip(pointers, pools))
    next_cursor = str(offset + len(items)) if has_more else None

    return SuccessResponse(data=WordsData(items=items, next_cursor=next_cursor))


@router.get("/verbs/{infinitive}", response_model=SuccessResponse[VerbDetails])
async def get_verb_details(infinitive: str, request_obj: Request):
    db: Database = request_obj.state.db
    verb_data = db.get_verb(infinitive)
    if not verb_data:
        raise HTTPException(status_code=404, detail="Verb not found")

    return SuccessResponse(data=VerbDetails(**verb_data))


@router.get("/nouns/{noun}", response_model=SuccessResponse[NounDetails])
async def get_noun_details(noun: str, request_obj: Request):
    db: Database = request_obj.state.db
    noun_data = db.get_noun(noun)
    if not noun_data:
        raise HTTPException(status_code=404, detail="Noun not found")

    return SuccessResponse(data=NounDetails(**noun_data))
