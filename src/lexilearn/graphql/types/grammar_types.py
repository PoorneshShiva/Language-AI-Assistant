import strawberry
from typing import List, Optional
from strawberry.scalars import JSON

@strawberry.type
class VerbType:
    infinitive: str
    present_perfect: List[str]
    singular_present_tense: List[str]
    simple_past: List[str]
    is_separable: bool
    is_regular: bool
    english_alternative: List[str]

@strawberry.type
class NounType:
    noun: str
    plural: str
    gender: str
    case_forms: JSON
    english_translation: str
    is_irregular: bool

@strawberry.type
class AdjectiveType:
    adjective: str
    comparative: str
    superlative: str
    english_translation: str
    is_regular: bool
    is_comparable: bool