"""Common Pydantic models used across the LexiLearn application, especially for graph states and inputs."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class UserQuery(BaseModel):
    """Represents a user's query input to the system."""
    query: str = Field(..., description="The user's textual query.")
    query_language: Optional[str] = Field("German", description="The language of the user's query.")
    translated_language: Optional[str] = Field("English", description="The target language for translation.")
    # Add any other relevant fields for a user query state

class LanguageClass(BaseModel):
    """A generic model to represent language-related output, often from LLM parsing.
    This is a placeholder and should be refined based on actual use cases.
    """
    data: Dict[str, Any] = Field(default_factory=dict, description="Parsed language data.")
    # Example: could hold parsed POS tags, translation, etc.

class PartOfSpeech(BaseModel):
    """Represents identified parts of speech from a text."""
    verbs: List[str] = Field(default_factory=list, description="List of identified verbs.")
    nouns: List[str] = Field(default_factory=list, description="List of identified nouns.")
    adjectives: List[str] = Field(default_factory=list, description="List of identified adjectives.")
    adverbs: List[str] = Field(default_factory=list, description="List of identified adverbs.")
    # Add other POS categories as needed (e.g., prepositions, conjunctions)

class Translation(BaseModel):
    """Represents a translated text output."""
    translated_text: str = Field(..., description="The translated text.")
    source_language: Optional[str] = Field(None, description="The source language of the translation.")
    target_language: Optional[str] = Field(None, description="The target language of the translation.")

# Placeholder models for specific German grammar details.
# These are used by SysPrompts and Nodes, and their structure should match
# what the LLM is prompted to return.

class GermanVerbsDetails(BaseModel):
    """Detailed information for a German verb. Placeholder."""
    infinitive: str = Field(..., description="Infinitive form of the verb.")
    singular_present_tense: List[str] = Field(default_factory=list, description="Singular present tense forms.")
    simple_past: List[str] = Field(default_factory=list, description="Simple past (Präteritum) forms.")
    present_perfect: List[str] = Field(default_factory=list, description="Present perfect (Perfekt) forms.")
    english_translation: List[str] = Field(default_factory=list, description="English translation(s).")
    is_regular: bool = Field(True, description="Is the verb regular?")
    is_separable: bool = Field(False, description="Is the verb separable?")
    # Add other fields as per your LLM prompts and expected data.

class GermanAdjectiveDetails(BaseModel):
    """Detailed information for a German adjective. Placeholder."""
    positive: str = Field(..., description="Positive (base) form.")
    comparative: str = Field(..., description="Comparative form.")
    superlative: str = Field(..., description="Superlative form.")
    english_translation: str = Field(..., description="English translation.")
    is_regular: bool = Field(True, description="Is the adjective regular?")
    is_comparable: bool = Field(True, description="Is the adjective comparable?")
    # Add other fields as necessary.

class GermanNounDetails(BaseModel):
    """Detailed information for a German noun. Placeholder."""
    singular: str = Field(..., description="Singular form.")
    plural: str = Field(..., description="Plural form.")
    gender: str = Field(..., description="Grammatical gender (der, die, das).")
    case_forms: Dict[str, str] = Field(default_factory=dict, description="Case forms (nominative, accusative, dative, genitive).")
    english_translation: str = Field(..., description="English translation.")
    is_irregular: Optional[bool] = Field(None, description="Is the noun irregular in its declension or pluralization?")
    # Add other fields.

class GermanAdverbDetails(BaseModel):
    """Detailed information for a German adverb. Placeholder."""
    adverb: str = Field(..., description="The German adverb itself.")
    english_translation: str = Field(..., description="English translation.")
    adverb_type: Optional[str] = Field(None, description="Type of adverb (e.g., temporal, local, modal).")
    is_comparable: bool = Field(False, description="Is the adverb comparable?")
    # Add other fields.

class GermanPrepositionDetails(BaseModel):
    """Detailed information for a German preposition. Placeholder."""
    preposition: str = Field(..., description="The German preposition.")
    english_translation: str = Field(..., description="English translation.")
    case_governed: str = Field(..., description="Case(s) governed by the preposition (accusative, dative, genitive, mixed).")
    preposition_type: Optional[str] = Field(None, description="Type of preposition (e.g., local, temporal).")
    # Add other fields.

class GermanConjunctionDetails(BaseModel):
    """Detailed information for a German conjunction. Placeholder."""
    conjunction: str = Field(..., description="The German conjunction.")
    english_translation: str = Field(..., description="English translation.")
    conjunction_type: str = Field(..., description="Type of conjunction (coordinating, subordinating, correlative).")
    # Add other fields. 