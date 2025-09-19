import strawberry
from typing import Optional, List
from strawberry.scalars import JSON

@strawberry.input
class ExampleInput:
    de: str
    en: str

@strawberry.input
class UpsertWordInput:
    lemma: str
    pos: str
    translations_en: List[str]
    grammar: JSON
    examples: Optional[List[ExampleInput]] = None
    surface_forms: Optional[List[str]] = None

@strawberry.input
class ProgressEventInput:
    event: str
    score: float
    at: str

@strawberry.input
class UpdateProgressInput:
    user_id: strawberry.ID
    word_id: strawberry.ID
    status: Optional[str] = None
    confidence: Optional[float] = None
    learned_at: Optional[str] = None
    srs_stage: Optional[int] = None
    next_review_at: Optional[str] = None
    event: Optional[ProgressEventInput] = None
