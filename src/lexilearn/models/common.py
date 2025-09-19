"""Common Pydantic models used across the LexiLearn application, especially for graph states and inputs."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
import operator
from typing import Annotated

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
    verbs: List[str] = Field(..., description="A list of verbs of a given query")
    adjectives: List[str] = Field(..., description="A list of adjectives of a given query")
    adverbs: List[str] = Field(..., description="A list of adjectives of a given query")
    prepositions: List[str] = Field(..., description="A list of prepositions of a given query")
    nouns: List[str] = Field(..., description="A list of nouns of a given query")
    conjunctions: List[str] = Field(..., description="A list of conjunctions of a given query")
    interjections: List[str] = Field(..., description="A list of interjections of a given query")
    translated_query: str = Field(None,
                            description="""A translated query on 
                            the given user query""")

class PartOfSpeech(BaseModel):
    """Represents identified parts of speech from a text."""
    verbs: List[str] = Field(default_factory=list, description="List of identified verbs.")
    nouns: List[str] = Field(default_factory=list, description="List of identified nouns.")
    adjectives: List[str] = Field(default_factory=list, description="List of identified adjectives.")
    adverbs: List[str] = Field(default_factory=list, description="List of identified adverbs.")
    prepositions: List[str] = Field(default_factory=list, description="List of identified prepositions.")
    conjunctions: List[str] = Field(default_factory=list, description="List of identified conjunctions.")
    interjections: List[str] = Field(default_factory=list, description="List of identified interjections.")

class Translation(BaseModel):
    """Represents a translated text output."""
    translated_text: str = Field(..., description="The translated text.")
    source_language: Optional[str] = Field(None, description="The source language of the translation.")
    target_language: Optional[str] = Field(None, description="The target language of the translation.")

# Placeholder models for specific German grammar details.
# These are used by SysPrompts and Nodes, and their structure should match
# what the LLM is prompted to return.

class GermanVerbsDetails(BaseModel):
    """State to manage conjugation of single verb given"""
    infinitive: str = Field(...,
                            description="""An Infintive form of 
                            the given string in German
                            """)
    present_perfect: List[str] = Field(default_factory=list, 
                                        description="Present perfect (Perfekt) forms.")
    singular_present_tense: List[str] = Field(...,
                            description="""The 3rd person singular used in present tense
                            for the given verb in German. 
                            """)
    simple_past: List[str] = Field(...,
       description="""it's regular else False""")
    is_separable: bool = Field(...,
                               description="""Wheather the verb is separable or inseparable? True
                               if it's seperable else False
                               """)
    is_regular: bool = Field(...,
                             description=""" Whather the verb is regular or irregular verb? True if
                             it's regular else False""")
    
    english_alternative: List[str] = Field(...,
                             description="""The English translation for the given verb. 
                             """)

class GermanAdjectiveDetails(BaseModel):
    """Detailed information for a German adjective. Placeholder."""
    adjective: str = Field(..., description="Positive (base) form.")
    comparative: str = Field(..., description="Comparative form.")
    superlative: str = Field(..., description="Superlative form.")
    english_translation: str = Field(..., description="English translation.")
    is_regular: bool = Field(True, description="Is the adjective regular?")
    is_comparable: bool = Field(True, description="Is the adjective comparable?")
    # Add other fields as necessary.

class GermanNounDetails(BaseModel):
    """Details about a German noun."""

    noun: str = Field(
        ...,
        description="The base form (singular) of the German noun."
    )

    plural: str = Field(
        ...,
        description="The plural form of the German noun."
    )

    gender: str = Field(
        ...,
        description="The grammatical gender of the noun (der, die, das)."
    )

    case_forms: Optional[dict] = Field(
        None,
        description="A dictionary of case forms for the noun. Includes nominative, accusative, dative, and genitive."
    )

    english_translation: Optional[str] = Field(
        None,
        description="The English translation of the German noun."
    )

    is_irregular: Optional[bool] = Field(
        None,
        description="Whether the noun follows irregular pluralization rules (True) or regular rules (False)."
    )

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

class Cases(BaseModel):
    """State to manage all the cases"""
    speech: str = Field(..., description="""A identifier of a speech whether
                    it is a direct, indirect or possesion""")

class GermanGrammerDetails(BaseModel):
    """State to manage detailed grammer """
    verbs_info: Annotated[List[dict], operator.add] = Field(None,
                            description="""A detailed german verb information
                            such as infinitive, singular_present_tense, simple_past,
                            present_perfect and english_alternative.
                            """)
    adjectives_info: Annotated[List[dict], operator.add] = Field(None,
                        description="""A detailed german adjective information.
                        """)
    nouns_info: Annotated[List[dict], operator.add] = Field(None,
                        description="""A detailed german noun information.
                        """)
    
    conjunctions_info: Annotated[List[dict], operator.add] = Field(None,
                        description="""A detailed german conjuctions information.
                        """)
    adverbs_info: Annotated[List[dict], operator.add] = Field(None,
                        description="""A detailed german adverb information.
                        """)
    prepositions_info: Annotated[List[dict], operator.add] = Field(None,
                        description="""A detailed german preposition information.
                        """)