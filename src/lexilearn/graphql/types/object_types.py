import strawberry
from typing import Optional, List
import datetime
from strawberry.scalars import JSON

from lexilearn.graphql.types.enums import Level, ItemType, LearnStatus, Confidence, LearnStyle

@strawberry.type
class AppUser:
    id: strawberry.ID
    email: str
    display_name: Optional[str]
    created_at: datetime.datetime

@strawberry.type
class UserSettings:
    user_id: strawberry.ID
    level: Level
    daily_goal: int
    style: LearnStyle
    review_enabled: bool
    updated_at: datetime.datetime

@strawberry.type
class WordIndex:
    word_uid: strawberry.ID
    item_type: ItemType
    item_id: str

@strawberry.type
class UserWord:
    user_id: strawberry.ID
    word_uid: strawberry.ID
    status: LearnStatus
    due_at: Optional[datetime.datetime]
    interval_days: float
    stability: float
    difficulty: float
    lapses: int
    last_result: Optional[Confidence]
    last_prompt_id: Optional[str]
    added_at: datetime.datetime
    updated_at: datetime.datetime

@strawberry.type
class PracticeSession:
    id: strawberry.ID
    user_id: strawberry.ID
    started_at: datetime.datetime
    ended_at: Optional[datetime.datetime]

@strawberry.type
class PracticeEvent:
    id: strawberry.ID
    session_id: Optional[strawberry.ID]
    user_id: strawberry.ID
    word_uid: strawberry.ID
    prompt_id: Optional[str]
    level_at_time: Level
    confidence: Optional[Confidence]
    expected: Optional[str]
    answer: Optional[str]
    correct: Optional[bool]
    issues: Optional[JSON]
    normalized: Optional[JSON]
    created_at: datetime.datetime

@strawberry.type
class Prompt:
    id: str
    level: Level
    en: str
    de: str
    tags: List[str]
    created_at: datetime.datetime

@strawberry.type
class PromptWord:
    prompt_id: str
    word_uid: strawberry.ID

@strawberry.type
class UserStatsDaily:
    user_id: strawberry.ID
    day: datetime.date
    learned: int
    practiced: int
    completed: int

@strawberry.type
class TotalStatsType:
    learned: int
    completed: int
    in_queue: int

@strawberry.type
class NounHintType:
    gender: str
    noun: str
    case_forms: JSON
    english_translation: str
    fallback: str
    label: str
    insert: str

@strawberry.type
class Example:
    de: str
    en: str

@strawberry.type
class Word:
    id: strawberry.ID
    lemma: str
    pos: str
    translations_en: List[str]
    grammar: JSON
    examples: List[Example]
    surface_forms: List[str]
    created_at: str
    updated_at: str

@strawberry.type
class ProgressEvent:
    event: str
    score: float
    at: str

@strawberry.type
class UserWordProgress:
    id: strawberry.ID
    user_id: strawberry.ID
    word: Word
    status: str
    confidence: float
    added_at: str
    learned_at: Optional[str]
    srs_stage: int
    next_review_at: Optional[str]
    history: List[ProgressEvent]
