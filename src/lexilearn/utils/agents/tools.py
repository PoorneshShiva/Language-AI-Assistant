from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from lexilearn.utils.agents.user_prompts import UserPrompts
from lexilearn.utils.agents.system_prompts import SysPrompts
from lexilearn.utils.agents.model import llm_tools_user, llm_tools_user_sonnet
from langchain_core.runnables import RunnablePassthrough


import spacy
from langchain.tools import tool
# Load the German language model
try:
    nlp = spacy.load("de_core_news_sm")
except OSError:
    print("Downloading language model for the spaCy POS tagger\n" \
        "(don't worry, this will only happen once)")
    from spacy.cli import download
    download("de_core_news_sm")
    nlp = spacy.load("de_core_news_sm")
@tool
def detect_words_in_sentence(sentence: str) -> dict:
    """
    Detects verbs and nouns in a German sentence.
    Returns a dictionary with two keys: 'verbs' and 'nouns',
    each containing a list of the detected words.
    """
    doc = nlp(sentence)
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    nouns = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
    return {"verbs": verbs, "nouns": nouns}

@tool
def evaluate_german_sentence(expected: str, answer: str) -> dict:
    """
    Evaluates a user's German sentence against the expected answer.
    Returns a dictionary with the evaluation results.
    """
    
    # This is a simplified implementation.
    # A more robust implementation would use a language model with a specific prompt.
    
    normalized_expected = expected.lower().strip()
    normalized_answer = answer.lower().strip()
    
    if normalized_answer == normalized_expected:
        return {
            "correct": True,
            "why": "Correct!",
            "primary_fix": "",
            "issues": [],
            "normalized": {
                "answer": normalized_answer,
                "expected": normalized_expected
            }
        }
    else:
        # Use a language model to get more detailed feedback.
        # This requires a prompt that instructs the model to compare the two sentences
        # and return the feedback in a specific format.
        
        # For now, returning a generic response.
        return {
            "correct": False,
            "why": "The answer is not correct.",
            "primary_fix": expected,
            "issues": [{"type": "spelling", "detail": "The answer is not correct."}],
            "normalized": {
                "answer": normalized_answer,
                "expected": normalized_expected
            }
        }
