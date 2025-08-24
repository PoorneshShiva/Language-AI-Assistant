"""Defines graph nodes for general grammar processing using LangGraph."""

from typing import List, Dict, Any

# Langchain and Langgraph imports
from langchain_core.messages import HumanMessage
from langgraph.constants import Send # Corrected import path for Send

# Internal LexiLearn imports
from lexilearn.utils.agents.system_prompts import SysPrompts # Uncommented
from lexilearn.models.common import (
    UserQuery, LanguageClass, PartOfSpeech, Translation,
    GermanVerbsDetails, GermanAdjectiveDetails, GermanNounDetails,
    GermanAdverbDetails, GermanPrepositionDetails, GermanConjunctionDetails
)
from lexilearn.models.grammar import GermanGrammarDetails
from lexilearn.utils.agents.model import AgenticModels

# Instantiate AgenticModels. This will load the default model (Google Gemini).
# If GOOGLE_API_KEY is not set or invalid, agentic_models_supervisor.llm will be None.
agentic_models_supervisor = AgenticModels() 

# Access the actual Langchain LLM model instance.
# This is what should be used for .invoke()
# If initialization in AgenticModels failed (e.g. API key missing), this will be None.
llm = agentic_models_supervisor.llm

class LLMPlaceholder:
    def invoke(self, messages: List[Any]) -> Any:
        print(f"LLMPlaceholder invoked with: {messages}. Returning dummy data.")
        # This should return a Pydantic model matching the parser's expectation or a string
        # For simplicity, we'll assume it returns a dict that can be parsed.
        # This needs to be replaced with actual LLM calls and error handling.
        if "verb" in str(messages).lower():
            return GermanVerbsDetails(infinitive="spielen", english_translation=["to play"])
        if "adjective" in str(messages).lower():
            return GermanAdjectiveDetails(positive="schön", comparative="schöner", superlative="am schönsten", english_translation="beautiful")
        if "noun" in str(messages).lower():
            return GermanNounDetails(singular="Haus", plural="Häuser", gender="das", english_translation="house")
        return LanguageClass(data={"raw_response": "Dummy LLM Response"})

class Nodes:
    """Class to manage all the nodes in the grammar processing graph."""

    def __init__(self):
        """Initializes the Nodes class, setting up system prompts.
        
        Assumes `SysPrompts` is defined in the current scope.
        """
        self.sys_prompt = SysPrompts() # Uncommented
        
    # Original name: part_of_speech
    def identify_parts_of_speech(self, state: UserQuery) -> Dict[str, Any]:
        """Identifies parts of speech (verbs, nouns, adjectives, etc.) in the user's query.

        Args:
            state: An object (expected to be `UserQuery` type) containing the user's query.
                   Expected to have a `query` attribute.

        Returns:
            A dictionary representing the identified parts of speech.
        """
        parser, pos_sys_query = self.sys_prompt.get_pos_query(
                            pydantic_format=PartOfSpeech)
        
        query = state.query
        pos_usr_query = HumanMessage(f"Query: {query}")

        response = llm.invoke([pos_sys_query, pos_usr_query])
        
        if parser: 
            formated_response = parser.invoke(response)
            return formated_response.model_dump()

        return {"error": "POS parser not available or parsing failed",
                "raw_response": response.dict() if hasattr(response,
                 'dict') else str(response)}
        
    # Original name: translation
    def translate_query(self, state: UserQuery) -> Dict[str, Any]:
        """Translates the user's query from a source language to a target language.

        Args:
            state: An object containing the user's query and language information.

        Returns:
            A dictionary containing the translated query.
        """
        query = state.query
        translation_usr_query = HumanMessage(f"Input (German): {query}") # Consider making "German" here dynamic if graph is multi-lingual

        original_language = state.query_language
        translated_language = state.translated_language
        parser, translation_sys_query = self.sys_prompt.get_translation_query(
                            src_lang=original_language,
                            dest_lang=translated_language,
                            pydantic_format=Translation)
        
        response = llm.invoke([translation_sys_query, translation_usr_query])
        if parser:
            formated_response = parser.invoke(response) # LLM response should match Translation model
            return {"translated_query": formated_response.model_dump()} # Matches notebook structure
        return {"error": "Translation parser not available", "raw_response": str(response)}

    # Original name: send_queries
    def dispatch_grammar_tasks(self, state: PartOfSpeech) -> List[Send]:
        """Prepares and dispatches tasks for detailed grammatical analysis.

        Args:
            state: Object containing identified parts of speech.

        Returns:
            A list of `Send` objects for downstream nodes.
        """
        verbs = state.verbs
        adjectives = state.adjectives
        # adverbs = state.adverbs # Assuming adverbs might be added to PartOfSpeech model
        nouns = state.nouns
        
        tasks = []
        if verbs:
            tasks.extend([Send("Verb Conjugation", {"verb": verb}) for verb in verbs])
        if adjectives:
            tasks.extend([Send("Adjective", {"adjective": adj}) for adj in adjectives])
        if nouns:
            tasks.extend([Send("Noun", {"noun": noun}) for noun in nouns])
        # Add other parts of speech as needed
        # If no tasks, LangGraph needs a way to end or proceed. 
        # The conditional_edges in graph definition should handle this (e.g. by including END).
        return tasks 
    
    # Original name: verb_conjugation
    def get_verb_details(self, state: Dict[str, str]) -> Dict[str, Any]: # Input state likely a dict from Send
        """Retrieves detailed conjugation for a given German verb.
        Args:
            state: A dictionary expected to contain a "verb" key.
        Returns:
            A dictionary part of GermanGrammarDetails state (e.g. {"verbs_info": [...]}).
        """
        verb = state["verb"]
        verb_usr_query = HumanMessage(f"Verb : {verb}")
        parser, verb_conj_sys_query = self.sys_prompt.get_verb_conjugations_query(
                            pydantic_format=GermanVerbsDetails)
        
        response = llm.invoke([verb_conj_sys_query, verb_usr_query])
        if parser:
            formated_response = parser.invoke(response)
            return {"verbs_info": [formated_response.model_dump()]}
        return {"verbs_info": [], "error": "Verb parser failed"}
    
    # Original name: adjective
    def get_adjective_details(self, state: Dict[str, str]) -> Dict[str, Any]:
        """Retrieves details for a given German adjective.
        Args:
            state: A dictionary expected to contain an "adjective" key.
        Returns:
            A dictionary part of GermanGrammarDetails state.
        """
        adj = state["adjective"]
        adj_usr_query = HumanMessage(f"Adjective : {adj}")
        parser, adj_sys_query = self.sys_prompt.get_adjectives_query(
                            pydantic_format=GermanAdjectiveDetails)
        
        response = llm.invoke([adj_sys_query, adj_usr_query])
        if parser:
            formated_response = parser.invoke(response)
            return {"adjectives_info": [formated_response.model_dump()]}
        return {"adjectives_info": [], "error": "Adjective parser failed"}

    # Original name: noun
    def get_noun_details(self, state: Dict[str, str]) -> Dict[str, Any]:
        """Retrieves details for a given German noun.
        Args:
            state: A dictionary expected to contain a "noun" key.
        Returns:
            A dictionary part of GermanGrammarDetails state.
        """
        noun_str = state["noun"] # Renamed to avoid conflict with 'noun' node name if used directly
        noun_usr_query = HumanMessage(f"Noun : {noun_str}")
        parser, noun_sys_query = self.sys_prompt.get_noun_query(
                            pydantic_format=GermanNounDetails)
        
        response = llm.invoke([noun_sys_query, noun_usr_query])
        if parser:
            formated_response = parser.invoke(response)
            return {"nouns_info": [formated_response.model_dump()]}
        return {"nouns_info": [], "error": "Noun parser failed"}

    # Placeholder methods for other grammar parts if needed, e.g.:
    # def get_adverb_details(self, state: Dict[str, str]) -> Dict[str, Any]: ...
    # def get_preposition_details(self, state: Dict[str, str]) -> Dict[str, Any]: ...
    # def get_conjunction_details(self, state: Dict[str, str]) -> Dict[str, Any]: ...
