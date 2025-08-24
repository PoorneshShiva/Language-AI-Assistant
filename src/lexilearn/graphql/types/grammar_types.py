"""GraphQL type definitions for LexiLearn, based on Pydantic models."""

import strawberry
from typing import List, Optional, Dict, Any # Any and Dict for analysis field
from strawberry.experimental import pydantic
from strawberry.scalars import JSON # For generic Dict fields

from lexilearn.models import common, grammar

# Removed BasePydanticConfig class and its decorator
# class BasePydanticConfig:
#     pass


# Convert Pydantic models from common.py to Strawberry types
@strawberry.experimental.pydantic.type(model=common.UserQuery)
class UserQueryType:
    query: strawberry.auto
    query_language: strawberry.auto
    translated_language: strawberry.auto

@strawberry.experimental.pydantic.input(model=common.UserQuery) # Input type for mutations
class UserQueryInput:
    query: strawberry.auto
    query_language: strawberry.auto
    translated_language: strawberry.auto

# We might not need LanguageClass directly in GraphQL if it's an intermediate type
# @strawberry.experimental.pydantic.type(model=common.LanguageClass)
# class LanguageClassType:
#     data: strawberry.auto # This would become JSON

@strawberry.experimental.pydantic.type(model=common.PartOfSpeech, all_fields=True)
class PartOfSpeechType:
    pass
    # analysis: JSON # Using JSON for Dict[str, Any]
    # # analysis: strawberry.auto # if you want strawberry to infer, but JSON is more explicit for dicts

@strawberry.experimental.pydantic.type(model=common.Translation, all_fields=True)
class TranslationType:
    pass
    # translated_text: strawberry.auto
    # language: strawberry.auto

@strawberry.experimental.pydantic.type(model=common.GermanVerbsDetails)
class GermanVerbsDetailsType:
    infinitive: strawberry.auto
    singular_present_tense: strawberry.auto
    simple_past: strawberry.auto
    present_perfect: strawberry.auto
    english_translation: strawberry.auto
    is_regular: strawberry.auto
    is_separable: strawberry.auto

@strawberry.experimental.pydantic.type(model=common.GermanAdjectiveDetails)
class GermanAdjectiveDetailsType:
    positive: strawberry.auto
    comparative: strawberry.auto
    superlative: strawberry.auto
    english_translation: strawberry.auto
    is_regular: strawberry.auto
    is_comparable: strawberry.auto

@strawberry.experimental.pydantic.type(model=common.GermanNounDetails)
class GermanNounDetailsType:
    singular: strawberry.auto
    plural: strawberry.auto
    gender: strawberry.auto
    case_forms: JSON # Dict[str, str] maps well to JSON
    english_translation: strawberry.auto
    is_irregular: strawberry.auto

@strawberry.experimental.pydantic.type(model=common.GermanAdverbDetails)
class GermanAdverbDetailsType:
    adverb: strawberry.auto
    english_translation: strawberry.auto
    adverb_type: strawberry.auto
    is_comparable: strawberry.auto

@strawberry.experimental.pydantic.type(model=common.GermanPrepositionDetails)
class GermanPrepositionDetailsType:
    preposition: strawberry.auto
    english_translation: strawberry.auto
    case_governed: strawberry.auto
    preposition_type: strawberry.auto

@strawberry.experimental.pydantic.type(model=common.GermanConjunctionDetails)
class GermanConjunctionDetailsType:
    conjunction: strawberry.auto
    english_translation: strawberry.auto
    conjunction_type: strawberry.auto

# Convert Pydantic models from grammar.py to Strawberry types
@strawberry.experimental.pydantic.type(model=grammar.GermanGrammarDetails)
class GermanGrammarDetailsType:
    verbs_info: List[GermanVerbsDetailsType] # Now strongly typed
    adjectives_info: List[GermanAdjectiveDetailsType]
    nouns_info: List[GermanNounDetailsType]
    conjunctions_info: List[GermanConjunctionDetailsType]
    adverbs_info: List[GermanAdverbDetailsType]
    prepositions_info: List[GermanPrepositionDetailsType]

@strawberry.experimental.pydantic.type(model=grammar.LanggraphGrammarNodeOutput)
class LanggraphGrammarNodeOutputType:
    processed_text: strawberry.auto
    analysis: Optional[JSON] # Dict maps to JSON 