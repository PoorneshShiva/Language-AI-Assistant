from fastapi import APIRouter, Query, HTTPException, Depends, Request
import random
from typing import Optional
from lexilearn.rest.models import DetectWordsRequest, DetectWordsData, SuccessResponse, DetectedWord, RandomWordsRequest, RandomWordData, RandomWordItem, WordItem, WordsData, VerbDetails, NounDetails
from lexilearn.utils.agents.main import AgenticMain
from lexilearn.models.common import UserQuery
from lexilearn.database import Database

router = APIRouter()

@router.post("/detect", response_model=SuccessResponse[DetectWordsData])
async def detect_words(request: DetectWordsRequest, request_obj: Request):
    agent_main = request_obj.state.agent_main
    agent = agent_main.build_german_graph()
    
    user_query_input = UserQuery(query=request.sentence)
    result = agent.invoke(user_query_input)

    detected = []
    if result and result.verbs_info:
        for verb_info in result.verbs_info:
            if f"verb:{verb_info.infinitive}" not in request.exclude_keys:
                detected.append(DetectedWord(type="verb", id=verb_info.infinitive))
    if result and result.nouns_info:
        for noun_info in result.nouns_info:
            if f"noun:{noun_info.noun}" not in request.exclude_keys:
                detected.append(DetectedWord(type="noun", id=noun_info.noun))
    if result and result.adjectives_info:
        for adj_info in result.adjectives_info:
            if f"adjective:{adj_info.adjective}" not in request.exclude_keys:
                detected.append(DetectedWord(type="adjective", id=adj_info.adjective))

    return SuccessResponse(
        data=DetectWordsData(
            detected=detected
        )
    )

@router.post("/random", response_model=SuccessResponse[RandomWordData])
async def random_words(request_obj: Request, request: RandomWordsRequest):
    db = Database(request_obj.state.db_connection)
    preferred_types = request.preferred_types
    if not preferred_types:
        preferred_types = ["verb", "noun"]

    random.shuffle(preferred_types)

    for selected_type in preferred_types:
        exclude_ids = [key.split(":")[1] for key in request.exclude_keys if key.startswith(f"{selected_type}:")]
        
        if selected_type == "verb":
            cursor = db.conn.cursor()
            cursor.execute("SELECT infinitive FROM verbs")
            all_words = [row[0] for row in cursor.fetchall()]
            available_words = [word for word in all_words if word not in exclude_ids]
            if available_words:
                item_id = random.choice(available_words)
                return SuccessResponse(data=RandomWordData(item=RandomWordItem(type="verb", id=item_id)))

        elif selected_type == "noun":
            cursor = db.conn.cursor()
            cursor.execute("SELECT noun FROM nouns")
            all_words = [row[0] for row in cursor.fetchall()]
            available_words = [word for word in all_words if word not in exclude_ids]
            if available_words:
                item_id = random.choice(available_words)
                return SuccessResponse(data=RandomWordData(item=RandomWordItem(type="noun", id=item_id)))

    # Fallback if no words are found
    return SuccessResponse(data=RandomWordData(item=RandomWordItem(type="verb", id="aufbewahren")))

@router.get("/", response_model=SuccessResponse[WordsData])
async def get_words(
    request_obj: Request,
    types: Optional[str] = Query(None),
    limit: int = 50,
    cursor: Optional[str] = None
):
    db = Database(request_obj.state.db_connection)
    word_types = []
    if types:
        word_types = [t.strip() for t in types.split(',')]
    else:
        word_types = ['verb', 'noun']

    offset = int(cursor) if cursor and cursor.isdigit() else 0
    
    queries = []
    if 'verb' in word_types:
        queries.append("SELECT infinitive AS id, 'verb' AS type FROM verbs")
    if 'noun' in word_types:
        queries.append("SELECT noun AS id, 'noun' AS type FROM nouns")

    if not queries:
        return SuccessResponse(data=WordsData(items=[], next_cursor=None))

    final_query = " UNION ALL ".join(queries)
    final_query += " ORDER BY id LIMIT ? OFFSET ?"

    cursor_db = db.conn.cursor()
    cursor_db.execute(final_query, (limit, offset))
    
    items = [WordItem(type=row[1], id=row[0]) for row in cursor_db.fetchall()]
    
    next_cursor = str(offset + len(items)) if len(items) == limit else None
    
    return SuccessResponse(
        data=WordsData(
            items=items,
            next_cursor=next_cursor
        )
    )

@router.get("/verbs/{infinitive}", response_model=SuccessResponse[VerbDetails])
async def get_verb_details(infinitive: str, request_obj: Request):
    db = Database(request_obj.state.db_connection)
    verb_data = db.get_verb(infinitive)
    if not verb_data:
        raise HTTPException(status_code=404, detail="Verb not found")
    
    return SuccessResponse(
        data=VerbDetails(**verb_data)
    )

@router.get("/nouns/{noun}", response_model=SuccessResponse[NounDetails])
async def get_noun_details(noun: str, request_obj: Request):
    db = Database(request_obj.state.db_connection)
    noun_data = db.get_noun(noun)
    if not noun_data:
        raise HTTPException(status_code=404, detail="Noun not found")
    
    return SuccessResponse(
        data=NounDetails(**noun_data)
    )